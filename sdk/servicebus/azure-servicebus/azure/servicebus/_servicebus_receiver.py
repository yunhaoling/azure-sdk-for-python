# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import logging
import functools
from typing import Any, List, TYPE_CHECKING, Optional, Dict, Iterator, Union

import six

from uamqp import ReceiveClient, types, Message
from uamqp.constants import SenderSettleMode
from uamqp.authentication.common import AMQPAuth

from ._base_handler import BaseHandler
from ._common.utils import create_authentication
from ._common.message import ServiceBusPeekedMessage, ServiceBusReceivedMessage
from ._common.constants import (
    REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
    REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
    REQUEST_RESPONSE_RENEWLOCK_OPERATION,
    REQUEST_RESPONSE_PEEK_OPERATION,
    ReceiveMode,
    MGMT_REQUEST_DISPOSITION_STATUS,
    MGMT_REQUEST_LOCK_TOKENS,
    MGMT_REQUEST_SEQUENCE_NUMBERS,
    MGMT_REQUEST_RECEIVER_SETTLE_MODE,
    MGMT_REQUEST_FROM_SEQUENCE_NUMBER,
    MGMT_REQUEST_MAX_MESSAGE_COUNT
)
from ._common import mgmt_handlers
from ._common.receiver_mixins import ReceiverMixin
from ._servicebus_session import ServiceBusSession

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

_LOGGER = logging.getLogger(__name__)


class ServiceBusReceiver(BaseHandler, ReceiverMixin):  # pylint: disable=too-many-instance-attributes
    """The ServiceBusReceiver class defines a high level interface for
    receiving messages from the Azure Service Bus Queue or Topic Subscription.

    The two primary channels for message receipt are `receive()` to make a single request for messages,
    and `for message in receiver:` to continuously receive incoming messages in an ongoing fashion.

    :ivar fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
     The namespace format is: `<yournamespace>.servicebus.windows.net`.
    :vartype fully_qualified_namespace: str
    :ivar entity_path: The path of the entity that the client connects to.
    :vartype entity_path: str

    :param str fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
     The namespace format is: `<yournamespace>.servicebus.windows.net`.
    :param ~azure.core.credentials.TokenCredential credential: The credential object used for authentication which
     implements a particular interface for getting tokens. It accepts
     :class: credential objects generated by the azure-identity library and objects that implement the
     `get_token(self, *scopes)` method.
    :keyword str queue_name: The path of specific Service Bus Queue the client connects to.
    :keyword str topic_name: The path of specific Service Bus Topic which contains the Subscription
     the client connects to.
    :keyword str subscription_name: The path of specific Service Bus Subscription under the
     specified Topic the client connects to.
    :keyword Optional[float] max_wait_time: The timeout in seconds between received messages after which the
     receiver will automatically stop receiving. The default value is None, meaning no timeout.
    :keyword receive_mode: The mode with which messages will be retrieved from the entity. The two options
     are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
     lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
     will be immediately removed from the queue, and cannot be subsequently abandoned or re-received
     if the client fails to process the message.
     The default mode is PeekLock.
    :paramtype receive_mode: ~azure.servicebus.ReceiveMode
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the Service Bus service. Default is `TransportType.Amqp`.
    :paramtype transport_type: ~azure.servicebus.TransportType
    :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :keyword str user_agent: If specified, this will be added in front of the built-in user agent string.
    :keyword int prefetch_count: The maximum number of messages to cache with each request to the service.
     This setting is only for advanced performance tuning. Increasing this value will improve message throughput
     performance but increase the chance that messages will expire while they are cached if they're not
     processed fast enough.
     The default value is 0, meaning messages will be received from the service and processed one at a time.
     In the case of prefetch_count being 0, `ServiceBusReceiver.receive` would try to cache `max_message_count`
     (if provided) within its request to the service.

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START create_servicebus_receiver_sync]
            :end-before: [END create_servicebus_receiver_sync]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the ServiceBusReceiver.

    """
    def __init__(
        self,
        fully_qualified_namespace,
        credential,
        **kwargs
    ):
        # type: (str, TokenCredential, Any) -> None
        self._message_iter = None # type: Optional[Iterator[ServiceBusReceivedMessage]]
        if kwargs.get("entity_name"):
            super(ServiceBusReceiver, self).__init__(
                fully_qualified_namespace=fully_qualified_namespace,
                credential=credential,
                **kwargs
            )
        else:
            queue_name = kwargs.get("queue_name")  # type: Optional[str]
            topic_name = kwargs.get("topic_name")  # type: Optional[str]
            subscription_name = kwargs.get("subscription_name")
            if queue_name and topic_name:
                raise ValueError("Queue/Topic name can not be specified simultaneously.")
            if topic_name and not subscription_name:
                raise ValueError("Subscription name is missing for the topic. Please specify subscription_name.")
            entity_name = queue_name or topic_name
            if not entity_name:
                raise ValueError("Queue/Topic name is missing. Please specify queue_name/topic_name.")

            super(ServiceBusReceiver, self).__init__(
                fully_qualified_namespace=fully_qualified_namespace,
                credential=credential,
                entity_name=entity_name,
                **kwargs
            )

        self._populate_attributes(**kwargs)
        self._session = ServiceBusSession(self._session_id, self) if self._session_id else None

    def __iter__(self):
        return self._iter_contextual_wrapper()

    def _iter_contextual_wrapper(self, max_wait_time=None):
        # pylint: disable=protected-access
        original_timeout = None
        while True:
            # This is not threadsafe, but gives us a way to handle if someone passes
            # different max_wait_times to different iterators and uses them in concert.
            if max_wait_time:
                original_timeout = self._handler._timeout
                self._handler._timeout = max_wait_time * 1000
            try:
                yield next(self)
            except StopIteration:
                break
            finally:
                if original_timeout:
                    self._handler._timeout = original_timeout

    def __next__(self):
        self._check_live()
        while True:
            try:
                return self._do_retryable_operation(self._iter_next)
            except StopIteration:
                self._message_iter = None
                raise

    next = __next__  # for python2.7

    def _iter_next(self):
        self._open()
        if not self._message_iter:
            self._message_iter = self._handler.receive_messages_iter()
        uamqp_message = next(self._message_iter)
        message = self._build_message(uamqp_message)
        return message

    def _create_handler(self, auth):
        # type: (AMQPAuth) -> None
        self._handler = ReceiveClient(
            self._get_source(),
            auth=auth,
            debug=self._config.logging_enable,
            properties=self._properties,
            error_policy=self._error_policy,
            client_name=self._name,
            on_attach=self._on_attach,
            auto_complete=False,
            encoding=self._config.encoding,
            receive_settle_mode=self._receive_mode.value,
            send_settle_mode=SenderSettleMode.Settled if self._receive_mode == ReceiveMode.ReceiveAndDelete else None,
            timeout=self._max_wait_time * 1000 if self._max_wait_time else 0,
            prefetch=self._prefetch_count,
            keep_alive_interval=self._config.keep_alive,
            shutdown_after_timeout=False
        )

    def _open(self):
        # pylint: disable=protected-access
        if self._running:
            return
        if self._handler and not self._handler._shutdown:
            self._handler.close()

        auth = None if self._connection else create_authentication(self)
        self._create_handler(auth)
        try:
            self._handler.open(connection=self._connection)
            while not self._handler.client_ready():
                time.sleep(0.05)
            self._running = True
        except:
            self.close()
            raise

    def _receive(self, max_message_count=None, timeout=None):
        # type: (Optional[int], Optional[float]) -> List[ServiceBusReceivedMessage]
        # pylint: disable=protected-access
        self._open()

        amqp_receive_client = self._handler
        received_messages_queue = amqp_receive_client._received_messages
        max_message_count = max_message_count or self._prefetch_count
        timeout_ms = 1000 * (timeout or self._max_wait_time) if (timeout or self._max_wait_time) else 0
        abs_timeout_ms = amqp_receive_client._counter.get_current_ms() + timeout_ms if timeout_ms else 0

        batch = []  # type: List[Message]
        while not received_messages_queue.empty() and len(batch) < max_message_count:
            batch.append(received_messages_queue.get())
            received_messages_queue.task_done()
        if len(batch) >= max_message_count:
            return [self._build_message(message) for message in batch]

        # Dynamically issue link credit if max_message_count > 1 when the prefetch_count is the default value 1
        if max_message_count and self._prefetch_count == 1 and max_message_count > 1:
            link_credit_needed = max_message_count - len(batch)
            amqp_receive_client.message_handler.reset_link_credit(link_credit_needed)

        first_message_received = expired = False
        receiving = True
        while receiving and not expired and len(batch) < max_message_count:
            while receiving and received_messages_queue.qsize() < max_message_count:
                if abs_timeout_ms and amqp_receive_client._counter.get_current_ms() > abs_timeout_ms:
                    expired = True
                    break
                before = received_messages_queue.qsize()
                receiving = amqp_receive_client.do_work()
                received = received_messages_queue.qsize() - before
                if not first_message_received and received_messages_queue.qsize() > 0 and received > 0:
                    # first message(s) received, continue receiving for some time
                    first_message_received = True
                    abs_timeout_ms = amqp_receive_client._counter.get_current_ms() + \
                                     self._further_pull_receive_timeout_ms
            while not received_messages_queue.empty() and len(batch) < max_message_count:
                batch.append(received_messages_queue.get())
                received_messages_queue.task_done()

        return [self._build_message(message) for message in batch]

    def _settle_message(self, settlement, lock_tokens, dead_letter_details=None):
        # type: (bytes, List[str], Optional[Dict[str, Any]]) -> Any
        # Message settlement through the mgmt link.
        message = {
            MGMT_REQUEST_DISPOSITION_STATUS: settlement,
            MGMT_REQUEST_LOCK_TOKENS: types.AMQPArray(lock_tokens)
        }

        self._populate_message_properties(message)
        if dead_letter_details:
            message.update(dead_letter_details)

        # We don't do retry here, retry is done in the ReceivedMessage._settle_message
        return self._mgmt_request_response(
            REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
            message,
            mgmt_handlers.default
        )

    def _renew_locks(self, *lock_tokens, **kwargs):
        # type: (str, Any) -> Any
        timeout = kwargs.pop("timeout", None)
        message = {MGMT_REQUEST_LOCK_TOKENS: types.AMQPArray(lock_tokens)}
        return self._mgmt_request_response_with_retry(
            REQUEST_RESPONSE_RENEWLOCK_OPERATION,
            message,
            mgmt_handlers.lock_renew_op,
            timeout=timeout
        )

    @property
    def session(self):
        # type: () -> ServiceBusSession
        """
        Get the ServiceBusSession object linked with the receiver. Session is only available to session-enabled
        entities, it would return None if called on a non-sessionful receiver.

        :rtype: ~azure.servicebus.ServiceBusSession

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START get_session_sync]
                :end-before: [END get_session_sync]
                :language: python
                :dedent: 4
                :caption: Get session from a receiver
        """
        return self._session  # type: ignore

    def close(self):
        # type: () -> None
        super(ServiceBusReceiver, self).close()
        self._message_iter = None  # pylint: disable=attribute-defined-outside-init

    def get_streaming_message_iter(self, max_wait_time=None):
        # type: (float) -> Iterator[ServiceBusReceivedMessage]
        """Receive messages from an iterator indefinitely, or if a max_wait_time is specified, until
        such a timeout occurs.

        :param max_wait_time: Maximum time to wait in seconds for the next message to arrive.
         If no messages arrive, and no timeout is specified, this call will not return
         until the connection is closed. If specified, and no messages arrive for the
         timeout period, the iterator will stop.
        :type max_wait_time: Optional[float]
        :rtype: Iterator[ReceivedMessage]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START receive_forever]
                :end-before: [END receive_forever]
                :language: python
                :dedent: 4
                :caption: Receive indefinitely from an iterator in streaming fashion.
        """
        if max_wait_time is not None and max_wait_time <= 0:
            raise ValueError("The max_wait_time must be greater than 0.")
        return self._iter_contextual_wrapper(max_wait_time)

    @classmethod
    def from_connection_string(
        cls,
        conn_str,
        **kwargs
    ):
        # type: (str, Any) -> ServiceBusReceiver
        """Create a ServiceBusReceiver from a connection string.

        :param conn_str: The connection string of a Service Bus.
        :type conn_str: str
        :keyword str queue_name: The path of specific Service Bus Queue the client connects to.
        :keyword str topic_name: The path of specific Service Bus Topic which contains the Subscription
         the client connects to.
        :keyword str subscription_name: The path of specific Service Bus Subscription under the
         specified Topic the client connects to.
        :keyword receive_mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently abandoned or re-received
         if the client fails to process the message.
         The default mode is PeekLock.
        :paramtype receive_mode: ~azure.servicebus.ReceiveMode
        :keyword Optional[float] max_wait_time: The timeout in seconds between received messages after which the
         receiver will automatically stop receiving. The default value is None, meaning no timeout.
        :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
        :keyword transport_type: The type of transport protocol that will be used for communicating with
         the Service Bus service. Default is `TransportType.Amqp`.
        :paramtype transport_type: ~azure.servicebus.TransportType
        :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
         Additionally the following keys may also be present: `'username', 'password'`.
        :keyword str user_agent: If specified, this will be added in front of the built-in user agent string.
        :keyword int prefetch_count: The maximum number of messages to cache with each request to the service.
         This setting is only for advanced performance tuning. Increasing this value will improve message throughput
         performance but increase the chance that messages will expire while they are cached if they're not
         processed fast enough.
         The default value is 0, meaning messages will be received from the service and processed one at a time.
         In the case of prefetch_count being 0, `ServiceBusReceiver.receive` would try to cache `max_message_count`
         (if provided) within its request to the service.
        :rtype: ~azure.servicebus.ServiceBusReceiver

        :raises ~azure.servicebus.ServiceBusAuthenticationError: Indicates an issue in token/identity validity.
        :raises ~azure.servicebus.ServiceBusAuthorizationError: Indicates an access/rights related failure.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_servicebus_receiver_from_conn_str_sync]
                :end-before: [END create_servicebus_receiver_from_conn_str_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusReceiver from connection string.

        """
        constructor_args = cls._convert_connection_string_to_kwargs(
            conn_str,
            **kwargs
        )
        if kwargs.get("queue_name") and kwargs.get("subscription_name"):
            raise ValueError("Queue entity does not have subscription.")

        if kwargs.get("topic_name") and not kwargs.get("subscription_name"):
            raise ValueError("Subscription name is missing for the topic. Please specify subscription_name.")
        return cls(**constructor_args)

    def receive_messages(self, max_message_count=None, max_wait_time=None):
        # type: (int, float) -> List[ServiceBusReceivedMessage]
        """Receive a batch of messages at once.

        This approach is optimal if you wish to process multiple messages simultaneously, or
        perform an ad-hoc receive as a single call.

        Note that the number of messages retrieved in a single batch will be dependent on
        whether `prefetch_count` was set for the receiver. If `prefetch_count` is not set for the receiver,
        the receiver would try to cache max_message_count (if provided) messages within the request to the service.

        This call will prioritize returning quickly over meeting a specified batch size, and so will
        return as soon as at least one message is received and there is a gap in incoming messages regardless
        of the specified batch size.

        :param Optional[int] max_message_count: Maximum number of messages in the batch. Actual number
         returned will depend on prefetch_count and incoming stream rate.
        :param Optional[float] max_wait_time: Maximum time to wait in seconds for the first message to arrive.
         If no messages arrive, and no timeout is specified, this call will not return
         until the connection is closed. If specified, an no messages arrive within the
         timeout period, an empty list will be returned.

        :rtype: List[~azure.servicebus.ServiceBusReceivedMessage]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START receive_sync]
                :end-before: [END receive_sync]
                :language: python
                :dedent: 4
                :caption: Receive messages from ServiceBus.

        """
        if max_wait_time is not None and max_wait_time <= 0:
            raise ValueError("The max_wait_time must be greater than 0.")
        self._check_live()
        return self._do_retryable_operation(
            self._receive,
            max_message_count=max_message_count,
            timeout=max_wait_time,
            operation_requires_timeout=True
        )

    def receive_deferred_messages(self, sequence_numbers, **kwargs):
        # type: (Union[int,List[int]], Any) -> List[ServiceBusReceivedMessage]
        """Receive messages that have previously been deferred.

        When receiving deferred messages from a partitioned entity, all of the supplied
        sequence numbers must be messages from the same partition.

        :param Union[int,List[int]] sequence_numbers: A list of the sequence numbers of messages that have been
         deferred.
        :keyword float timeout: The total operation timeout in seconds including all the retries. The value must be
         greater than 0 if specified. The default value is None, meaning no timeout.
        :rtype: List[~azure.servicebus.ServiceBusReceivedMessage]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START receive_defer_sync]
                :end-before: [END receive_defer_sync]
                :language: python
                :dedent: 4
                :caption: Receive deferred messages from ServiceBus.

        """
        self._check_live()
        timeout = kwargs.pop("timeout", None)
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")
        if isinstance(sequence_numbers, six.integer_types):
            sequence_numbers = [sequence_numbers]
        if not sequence_numbers:
            raise ValueError("At least one sequence number must be specified.")
        self._open()
        try:
            receive_mode = self._receive_mode.value.value
        except AttributeError:
            receive_mode = int(self._receive_mode)
        message = {
            MGMT_REQUEST_SEQUENCE_NUMBERS: types.AMQPArray([types.AMQPLong(s) for s in sequence_numbers]),
            MGMT_REQUEST_RECEIVER_SETTLE_MODE: types.AMQPuInt(receive_mode)
        }

        self._populate_message_properties(message)

        handler = functools.partial(mgmt_handlers.deferred_message_op, receive_mode=self._receive_mode, receiver=self)
        messages = self._mgmt_request_response_with_retry(
            REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
            message,
            handler,
            timeout=timeout
        )
        return messages

    def peek_messages(self, max_message_count=1, **kwargs):
        # type: (int, Any) -> List[ServiceBusPeekedMessage]
        """Browse messages currently pending in the queue.

        Peeked messages are not removed from queue, nor are they locked. They cannot be completed,
        deferred or dead-lettered.

        :param int max_message_count: The maximum number of messages to try and peek. The default
         value is 1.
        :keyword int sequence_number: A message sequence number from which to start browsing messages.
        :keyword float timeout: The total operation timeout in seconds including all the retries. The value must be
         greater than 0 if specified. The default value is None, meaning no timeout.

        :rtype: List[~azure.servicebus.ServiceBusPeekedMessage]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START peek_messages_sync]
                :end-before: [END peek_messages_sync]
                :language: python
                :dedent: 4
                :caption: Look at pending messages in the queue.

        """
        self._check_live()
        sequence_number = kwargs.pop("sequence_number", 0)
        timeout = kwargs.pop("timeout", None)
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")
        if not sequence_number:
            sequence_number = self._last_received_sequenced_number or 1
        if int(max_message_count) < 1:
            raise ValueError("count must be 1 or greater.")
        if int(sequence_number) < 1:
            raise ValueError("start_from must be 1 or greater.")

        self._open()
        message = {
            MGMT_REQUEST_FROM_SEQUENCE_NUMBER: types.AMQPLong(sequence_number),
            MGMT_REQUEST_MAX_MESSAGE_COUNT: max_message_count
        }

        self._populate_message_properties(message)

        return self._mgmt_request_response_with_retry(
            REQUEST_RESPONSE_PEEK_OPERATION,
            message,
            mgmt_handlers.peek_op,
            timeout=timeout
        )

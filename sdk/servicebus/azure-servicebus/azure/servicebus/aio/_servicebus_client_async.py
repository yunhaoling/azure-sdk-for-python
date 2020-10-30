# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, List, TYPE_CHECKING, Optional
import logging

import uamqp

from .._base_handler import _parse_conn_str
from ._base_handler_async import ServiceBusSharedKeyCredential, ServiceBusSASTokenCredential, BaseHandler
from ._servicebus_sender_async import ServiceBusSender
from ._servicebus_receiver_async import ServiceBusReceiver
from .._common._configuration import Configuration
from .._common.utils import generate_dead_letter_entity_name
from .._common.constants import SubQueue
from ._async_utils import create_authentication

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

_LOGGER = logging.getLogger(__name__)


class ServiceBusClient(object):
    """The ServiceBusClient class defines a high level interface for
    getting ServiceBusSender and ServiceBusReceiver.

    :ivar fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
     The namespace format is: `<yournamespace>.servicebus.windows.net`.
    :vartype fully_qualified_namespace: str

    :param str fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
     The namespace format is: `<yournamespace>.servicebus.windows.net`.
    :param ~azure.core.credentials.TokenCredential credential: The credential object used for authentication which
     implements a particular interface for getting tokens. It accepts
     credential objects generated by the azure-identity library and objects that implement the
     `get_token(self, *scopes)` method.
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the Service Bus service. Default is `TransportType.Amqp`.
    :paramtype transport_type: ~azure.servicebus.TransportType
    :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :keyword str user_agent: If specified, this will be added in front of the built-in user agent string.
    :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
     Default value is 3.
    :keyword float retry_backoff_factor: Delta back-off internal in the unit of second between retries.
     Default value is 0.8.
    :keyword float retry_backoff_max: Maximum back-off interval in the unit of second. Default value is 120.

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
            :start-after: [START create_sb_client_async]
            :end-before: [END create_sb_client_async]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the ServiceBusClient.

    """
    def __init__(
        self,
        fully_qualified_namespace: str,
        credential: "TokenCredential",
        **kwargs: Any
    ) -> None:
        self.fully_qualified_namespace = fully_qualified_namespace
        self._credential = credential
        self._config = Configuration(**kwargs)
        self._connection = None
        # Optional entity name, can be the name of Queue or Topic.  Intentionally not advertised, typically be needed.
        self._entity_name = kwargs.get("entity_name")
        self._auth_uri = "sb://{}".format(self.fully_qualified_namespace)
        if self._entity_name:
            self._auth_uri = "{}/{}".format(self._auth_uri, self._entity_name)
        # Internal flag for switching whether to apply connection sharing, pending fix in uamqp library
        self._connection_sharing = False
        self._handlers = []  # type: List[BaseHandler]

    async def __aenter__(self):
        if self._connection_sharing:
            await self._create_uamqp_connection()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def _create_uamqp_connection(self):
        auth = await create_authentication(self)
        self._connection = uamqp.ConnectionAsync(
            hostname=self.fully_qualified_namespace,
            sasl=auth,
            debug=self._config.logging_enable
        )

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        **kwargs: Any
    ) -> "ServiceBusClient":
        """
        Create a ServiceBusClient from a connection string.

        :param str conn_str: The connection string of a Service Bus.
        :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
        :keyword transport_type: The type of transport protocol that will be used for communicating with
         the Service Bus service. Default is `TransportType.Amqp`.
        :paramtype transport_type: ~azure.servicebus.TransportType
        :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
         Additionally the following keys may also be present: `'username', 'password'`.
        :keyword str user_agent: If specified, this will be added in front of the built-in user agent string.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :keyword float retry_backoff_factor: Delta back-off internal in the unit of second between retries.
         Default value is 0.8.
        :keyword float retry_backoff_max: Maximum back-off interval in the unit of second. Default value is 120.
        :rtype: ~azure.servicebus.aio.ServiceBusClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
                :start-after: [START create_sb_client_from_conn_str_async]
                :end-before: [END create_sb_client_from_conn_str_async]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusClient from connection string.

        """
        host, policy, key, entity_in_conn_str, token, token_expiry = _parse_conn_str(conn_str)
        if token and token_expiry:
            credential = ServiceBusSASTokenCredential(token, token_expiry)
        elif policy and key:
            credential = ServiceBusSharedKeyCredential(policy, key)  # type: ignore
        return cls(
            fully_qualified_namespace=host,
            entity_name=entity_in_conn_str or kwargs.pop("entity_name", None),
            credential=credential,  # type: ignore
            **kwargs
        )

    async def close(self) -> None:
        """
        Close down the ServiceBus client.
        All spawned senders, receivers and underlying connection will be shutdown.

        :return: None
        """
        for handler in self._handlers:
            try:
                await handler.close()
            except Exception as exception:  # pylint: disable=broad-except
                _LOGGER.error(
                    "Client has met an exception when closing the handler: %r. Exception: %r.",
                    handler._container_id,  # pylint: disable=protected-access
                    exception,
                )
        del self._handlers[:]

        if self._connection_sharing and self._connection:
            await self._connection.destroy_async()

    def get_queue_sender(self, queue_name: str, **kwargs: Any) -> ServiceBusSender:
        """Get ServiceBusSender for the specific queue.

        :param str queue_name: The path of specific Service Bus Queue the client connects to.
        :rtype: ~azure.servicebus.aio.ServiceBusSender

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
                :start-after: [START create_servicebus_sender_from_sb_client_async]
                :end-before: [END create_servicebus_sender_from_sb_client_async]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusClient from connection string.

        """
        # pylint: disable=protected-access
        handler = ServiceBusSender(
            fully_qualified_namespace=self.fully_qualified_namespace,
            queue_name=queue_name,
            credential=self._credential,
            logging_enable=self._config.logging_enable,
            transport_type=self._config.transport_type,
            http_proxy=self._config.http_proxy,
            connection=self._connection,
            user_agent=self._config.user_agent,
            retry_total=self._config.retry_total,
            retry_backoff_factor=self._config.retry_backoff_factor,
            retry_backoff_max=self._config.retry_backoff_max,
            **kwargs
        )
        self._handlers.append(handler)
        return handler

    def get_queue_receiver(self, queue_name: str, **kwargs: Any) -> ServiceBusReceiver:
        """Get ServiceBusReceiver for the specific queue.

        :param str queue_name: The path of specific Service Bus Queue the client connects to.
        :keyword session_id: A specific session from which to receive. This must be specified for a
         sessionful queue, otherwise it must be None. In order to receive messages from the next available
         session, set this to ~azure.servicebus.NEXT_AVAILABLE_SESSION.
        :paramtype session_id: Union[str, ~azure.servicebus.NEXT_AVAILABLE_SESSION]
        :keyword Optional[SubQueue] sub_queue: If specified, the subqueue this receiver will connect to.
         This includes the DeadLetter and TransferDeadLetter queues, holds messages that can't be delivered to any
         receiver or messages that can't be processed.  The default is None, meaning connect to the primary queue.
        :keyword receive_mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :paramtype receive_mode: ~azure.servicebus.ReceiveMode
        :keyword Optional[float] max_wait_time: The timeout in seconds between received messages after which the
         receiver will automatically stop receiving. The default value is None, meaning no timeout.
        :keyword int prefetch_count: The maximum number of messages to cache with each request to the service.
         This setting is only for advanced performance tuning. Increasing this value will improve message throughput
         performance but increase the chance that messages will expire while they are cached if they're not
         processed fast enough.
         The default value is 0, meaning messages will be received from the service and processed one at a time.
         In the case of prefetch_count being 0, `ServiceBusReceiver.receive` would try to cache `max_message_count`
         (if provided) within its request to the service.
        :rtype: ~azure.servicebus.aio.ServiceBusReceiver

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
                :start-after: [START create_servicebus_receiver_from_sb_client_async]
                :end-before: [END create_servicebus_receiver_from_sb_client_async]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusSender from ServiceBusClient.

        """
        # pylint: disable=protected-access
        sub_queue = kwargs.get('sub_queue', None)
        if sub_queue and kwargs.get('session_id'):
            raise ValueError(
                "session_id and sub_queue can not be specified simultaneously. "
                "To connect to the sub queue of a sessionful queue, "
                "please set sub_queue only as sub_queue does not support session."
            )
        if sub_queue and sub_queue in SubQueue:
            queue_name = generate_dead_letter_entity_name(
                queue_name=queue_name,
                transfer_deadletter=(sub_queue == SubQueue.TransferDeadLetter)
            )
        handler = ServiceBusReceiver(
            fully_qualified_namespace=self.fully_qualified_namespace,
            entity_name=queue_name,
            credential=self._credential,
            logging_enable=self._config.logging_enable,
            transport_type=self._config.transport_type,
            http_proxy=self._config.http_proxy,
            connection=self._connection,
            user_agent=self._config.user_agent,
            retry_total=self._config.retry_total,
            retry_backoff_factor=self._config.retry_backoff_factor,
            retry_backoff_max=self._config.retry_backoff_max,
            **kwargs
        )
        self._handlers.append(handler)
        return handler

    def get_topic_sender(self, topic_name: str, **kwargs: Any) -> ServiceBusSender:
        """Get ServiceBusSender for the specific topic.

        :param str topic_name: The path of specific Service Bus Topic the client connects to.
        :rtype: ~azure.servicebus.aio.ServiceBusSender

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
                :start-after: [START create_topic_sender_from_sb_client_async]
                :end-before: [END create_topic_sender_from_sb_client_async]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusSender from ServiceBusClient.

        """
        handler = ServiceBusSender(
            fully_qualified_namespace=self.fully_qualified_namespace,
            topic_name=topic_name,
            credential=self._credential,
            logging_enable=self._config.logging_enable,
            transport_type=self._config.transport_type,
            http_proxy=self._config.http_proxy,
            connection=self._connection,
            user_agent=self._config.user_agent,
            retry_total=self._config.retry_total,
            retry_backoff_factor=self._config.retry_backoff_factor,
            retry_backoff_max=self._config.retry_backoff_max,
            **kwargs
        )
        self._handlers.append(handler)
        return handler

    def get_subscription_receiver(self, topic_name: str, subscription_name: str, **kwargs: Any) -> ServiceBusReceiver:
        """Get ServiceBusReceiver for the specific subscription under the topic.

        :param str topic_name: The name of specific Service Bus Topic the client connects to.
        :param str subscription_name: The name of specific Service Bus Subscription
         under the given Service Bus Topic.
        :keyword session_id: A specific session from which to receive. This must be specified for a
         sessionful subscription, otherwise it must be None. In order to receive messages from the next available
         session, set this to ~azure.servicebus.NEXT_AVAILABLE_SESSION.
        :paramtype session_id: Union[str, ~azure.servicebus.NEXT_AVAILABLE_SESSION]
        :keyword Optional[SubQueue] sub_queue: If specified, the subqueue this receiver will connect to.
         This includes the DeadLetter and TransferDeadLetter queues, holds messages that can't be delivered to any
         receiver or messages that can't be processed.  The default is None, meaning connect to the primary queue.
        :keyword receive_mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the subscription. Messages received with ReceiveAndDelete
         will be immediately removed from the subscription, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :paramtype receive_mode: ~azure.servicebus.ReceiveMode
        :keyword Optional[float] max_wait_time: The timeout in seconds between received messages after which the
         receiver will automatically stop receiving. The default value is None, meaning no timeout.
        :keyword int prefetch_count: The maximum number of messages to cache with each request to the service.
         This setting is only for advanced performance tuning. Increasing this value will improve message throughput
         performance but increase the chance that messages will expire while they are cached if they're not
         processed fast enough.
         The default value is 0, meaning messages will be received from the service and processed one at a time.
         In the case of prefetch_count being 0, `ServiceBusReceiver.receive` would try to cache `max_message_count`
         (if provided) within its request to the service.
        :rtype: ~azure.servicebus.aio.ServiceBusReceiver

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_servicebus_async.py
                :start-after: [START create_subscription_receiver_from_sb_client_async]
                :end-before: [END create_subscription_receiver_from_sb_client_async]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusReceiver from ServiceBusClient.


        """
        # pylint: disable=protected-access
        sub_queue = kwargs.get('sub_queue', None)
        if sub_queue and kwargs.get('session_id'):
            raise ValueError(
                "session_id and sub_queue can not be specified simultaneously. "
                "To connect to the sub queue of a sessionful subscription, "
                "please set sub_queue only as sub_queue is not sessionful."
            )
        if sub_queue and sub_queue in SubQueue:
            entity_name = generate_dead_letter_entity_name(
                topic_name=topic_name,
                subscription_name=subscription_name,
                transfer_deadletter=(sub_queue == SubQueue.TransferDeadLetter)
            )
            handler = ServiceBusReceiver(
                fully_qualified_namespace=self.fully_qualified_namespace,
                entity_name=entity_name,
                credential=self._credential,
                logging_enable=self._config.logging_enable,
                transport_type=self._config.transport_type,
                http_proxy=self._config.http_proxy,
                connection=self._connection,
                user_agent=self._config.user_agent,
                retry_total=self._config.retry_total,
                retry_backoff_factor=self._config.retry_backoff_factor,
                retry_backoff_max=self._config.retry_backoff_max,
                **kwargs
            )
        else:
            handler = ServiceBusReceiver(
                fully_qualified_namespace=self.fully_qualified_namespace,
                topic_name=topic_name,
                subscription_name=subscription_name,
                credential=self._credential,
                logging_enable=self._config.logging_enable,
                transport_type=self._config.transport_type,
                http_proxy=self._config.http_proxy,
                connection=self._connection,
                user_agent=self._config.user_agent,
                retry_total=self._config.retry_total,
                retry_backoff_factor=self._config.retry_backoff_factor,
                retry_backoff_max=self._config.retry_backoff_max,
                **kwargs
            )
        self._handlers.append(handler)
        return handler

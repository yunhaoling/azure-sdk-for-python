# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
import threading

from typing import Any, Union, TYPE_CHECKING, Iterable, List
from uamqp import constants  # type:ignore

from .exceptions import ConnectError, EventHubError
from ._client_base import ClientBase
from ._producer import EventHubProducer
from ._constants import ALL_PARTITIONS
from ._common import (
    EventData,
    EventHubSharedKeyCredential,
    EventHubSASTokenCredential,
    EventDataBatch
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential  # type: ignore

log = logging.getLogger(__name__)


class EventHubProducerClient(ClientBase):
    """
    The EventHubProducerClient class defines a high level interface for
    sending events to the Azure Event Hubs service.

    :param str host: The hostname of the Event Hub.
    :param str event_hub_path: The path of the specific Event Hub to connect the client to.
    :param credential: The credential object used for authentication which implements particular interface
     of getting tokens. It accepts :class:`EventHubSharedKeyCredential<azure.eventhub.EventHubSharedKeyCredential>`,
     :class:`EventHubSASTokenCredential<azure.eventhub.EventHubSASTokenCredential>`, or credential objects generated by
     the azure-identity library and objects that implement `get_token(self, *scopes)` method.
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword float auth_timeout: The time in seconds to wait for a token to be authorized by the service.
     The default value is 60 seconds. If set to 0, no timeout will be enforced from the client.
    :keyword str user_agent: The user agent that needs to be appended to the built in user agent string.
    :keyword int retry_total: The total number of attempts to redo the failed operation when an error happened. Default
     value is 3.
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the Event Hubs service. Default is `TransportType.Amqp`.
    :paramtype transport_type: ~azure.eventhub.TransportType
    :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: 'proxy_hostname' (str value) and 'proxy_port' (int value).
     Additionally the following keys may also be present: 'username', 'password'.

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
            :start-after: [START create_eventhub_producer_client_sync]
            :end-before: [END create_eventhub_producer_client_sync]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the EventHubProducerClient.

    """
    def __init__(self, host, event_hub_path, credential, **kwargs):
        # type:(str, str, Union[EventHubSharedKeyCredential, EventHubSASTokenCredential, TokenCredential], Any) -> None
        """"""
        super(EventHubProducerClient, self).__init__(
            host=host, event_hub_path=event_hub_path, credential=credential,
            network_tracing=kwargs.get("logging_enable"), **kwargs)
        self._producers = {ALL_PARTITIONS: self._create_producer()}  # type: Dict[str, EventHubProducer]
        self._max_message_size_on_link = 0
        self._partition_ids = None
        self._lock = threading.Lock()

    def _get_partitions(self):
        if not self._partition_ids:
            self._partition_ids = self.get_partition_ids()
            for p_id in self._partition_ids:
                self._producers[p_id] = None

    def _get_max_mesage_size(self):
        # pylint: disable=protected-access
        with self._lock:
            if not self._max_message_size_on_link:
                self._producers[ALL_PARTITIONS]._open_with_retry()
                self._max_message_size_on_link = \
                    self._producers[ALL_PARTITIONS]._handler.message_handler._link.peer_max_message_size \
                    or constants.MAX_MESSAGE_LENGTH_BYTES

    def _start_producer(self, partition_id, send_timeout):
        with self._lock:
            self._get_partitions()
            if partition_id not in self._partition_ids and partition_id != ALL_PARTITIONS:
                raise ConnectError("Invalid partition {} for the event hub {}".format(partition_id, self.eh_name))

            if not self._producers[partition_id] or self._producers[partition_id].closed:
                self._producers[partition_id] = self._create_producer(
                    partition_id=partition_id,
                    send_timeout=send_timeout
                )

    def _create_producer(self, partition_id=None, send_timeout=None):
        target = "amqps://{}{}".format(self._address.hostname, self._address.path)
        send_timeout = self._config.send_timeout if send_timeout is None else send_timeout

        handler = EventHubProducer(
            self, target, partition=partition_id, send_timeout=send_timeout)
        return handler

    def send(self, event_data, **kwargs):
        # type: (Union[EventData, EventDataBatch, Iterable[EventData]], Any) -> None
        """
        Sends event data and blocks until acknowledgement is received or operation times out.

        :param event_data: The event to be sent. It can be an EventData object, or iterable of EventData objects.
        :type event_data: ~azure.eventhub.EventData, ~azure.eventhub.EventDataBatch, EventData Iterator/Generator/list
        :keyword str partition_key: With the given partition_key, event data will land to
         a particular partition of the Event Hub decided by the service.
        :keyword str partition_id: The specific partition ID to send to. Default is None, in which case the service
         will assign to all partitions using round-robin.
        :keyword float timeout: The maximum wait time to send the event data.
         If not specified, the default wait time specified when the producer was created will be used.
        :rtype: None
        :raises: :class:`AuthenticationError<azure.eventhub.AuthenticationError>`
         :class:`ConnectError<azure.eventhub.ConnectError>`
         :class:`ConnectionLostError<azure.eventhub.ConnectionLostError>`
         :class:`EventDataError<azure.eventhub.EventDataError>`
         :class:`EventDataSendError<azure.eventhub.EventDataSendError>`
         :class:`EventHubError<azure.eventhub.EventHubError>`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
                :start-after: [START eventhub_producer_client_send_sync]
                :end-before: [END eventhub_producer_client_send_sync]
                :language: python
                :dedent: 4
                :caption: Sends event data

        """
        partition_id = kwargs.pop("partition_id", None) or ALL_PARTITIONS
        send_timeout = kwargs.pop("timeout", None)
        try:
            self._producers[partition_id].send(event_data, **kwargs)
        except (KeyError, AttributeError, EventHubError):
            self._start_producer(partition_id, send_timeout)
            self._producers[partition_id].send(event_data, **kwargs)

    def create_batch(self, max_size=None):
        # type:(int) -> EventDataBatch
        """
        Create an EventDataBatch object with max size being max_size.
        The max_size should be no greater than the max allowed message size defined by the service side.

        :param int max_size: The maximum size of bytes data that an EventDataBatch object can hold.
        :rtype: ~azure.eventhub.EventDataBatch

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
                :start-after: [START eventhub_producer_client_create_batch_sync]
                :end-before: [END eventhub_producer_client_create_batch_sync]
                :language: python
                :dedent: 4
                :caption: Create EventDataBatch object within limited size

        """
        # pylint: disable=protected-access
        if not self._max_message_size_on_link:
            self._get_max_mesage_size()

        if max_size and max_size > self._max_message_size_on_link:
            raise ValueError('Max message size: {} is too large, acceptable max batch size is: {} bytes.'
                             .format(max_size, self._max_message_size_on_link))

        return EventDataBatch(max_size=(max_size or self._max_message_size_on_link))

    def close(self):
        # type: () -> None
        """
        Close down the client. If the client has already closed, this will be a no op.

        :rtype: None

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
                :start-after: [START eventhub_producer_client_close_sync]
                :end-before: [END eventhub_producer_client_close_sync]
                :language: python
                :dedent: 4
                :caption: Close down the client.

        """
        with self._lock:
            for producer in self._producers:
                if producer:
                    producer.close()
            self._producers = {}
        self._conn_manager.close_connection()

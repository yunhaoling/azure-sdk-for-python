# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging
from typing import Any, TYPE_CHECKING

from ._common.receiver_mixins import SessionReceiverMixin
from ._servicebus_receiver import ServiceBusReceiver
from ._servicebus_session import ServiceBusSession

if TYPE_CHECKING:
    import datetime
    from azure.core.credentials import TokenCredential

_LOGGER = logging.getLogger(__name__)

class ServiceBusSessionReceiver(ServiceBusReceiver, SessionReceiverMixin):
    """The ServiceBusSessionReceiver class defines a high level interface for
    receiving messages from the Azure Service Bus Queue or Topic Subscription
    while utilizing a session for FIFO and ownership semantics.

    :ivar fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
     The namespace format is: `<yournamespace>.servicebus.windows.net`.
    :vartype fully_qualified_namespace: str
    :ivar entity_path: The path of the entity that the client connects to.
    :vartype entity_path: str

    :param str fully_qualified_namespace: The fully qualified host name for the Service Bus namespace.
     The namespace format is: `<yournamespace>.servicebus.windows.net`.
    :param ~azure.core.credentials.TokenCredential credential: The credential object used for authentication which
     implements a particular interface for getting tokens. It accepts
     :class:`ServiceBusSharedKeyCredential<azure.servicebus.ServiceBusSharedKeyCredential>`, or credential objects
     generated by the azure-identity library and objects that implement the `get_token(self, *scopes)` method.
    :keyword str queue_name: The path of specific Service Bus Queue the client connects to.
    :keyword str topic_name: The path of specific Service Bus Topic which contains the Subscription
     the client connects to.
    :keyword str subscription_name: The path of specific Service Bus Subscription under the
     specified Topic the client connects to.
    :keyword int prefetch: The maximum number of messages to cache with each request to the service.
     The default value is 0, meaning messages will be received from the service and processed
     one at a time. Increasing this value will improve message throughput performance but increase
     the change that messages will expire while they are cached if they're not processed fast enough.
    :keyword float idle_timeout: The timeout in seconds between received messages after which the receiver will
     automatically shutdown. The default value is 0, meaning no timeout.
    :keyword mode: The mode with which messages will be retrieved from the entity. The two options
     are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
     lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
     will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
     the client fails to process the message. The default mode is PeekLock.
    :paramtype mode: ~azure.servicebus.ReceiveSettleMode
    :keyword session_id: A specific session from which to receive. This must be specified for a
     sessionful entity, otherwise it must be None. In order to receive messages from the next available
     session, set this to None.  The default is None.
    :paramtype session_id: str
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
     Default value is 3.
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the Service Bus service. Default is `TransportType.Amqp`.
    :paramtype transport_type: ~azure.servicebus.TransportType
    :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START create_servicebus_receiver_sync]
            :end-before: [END create_servicebus_receiver_sync]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the ServiceBusReceiver.

    """
    def __init__(self, fully_qualified_namespace, credential, **kwargs):
        super(ServiceBusSessionReceiver, self).__init__(fully_qualified_namespace, credential, **kwargs)
        self._create_session_attributes(**kwargs)
        self._session = ServiceBusSession(self._session_id, self, self._config.encoding)

    @property
    def session(self):
        # type: ()->ServiceBusSession
        """
        Get the ServiceBusSession object linked with the receiver. Session is only available to session-enabled
        entities.

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

    @classmethod
    def from_connection_string(
        cls,
        conn_str,
        **kwargs
    ):
        # type: (str, Any) -> ServiceBusSessionReceiver
        """Create a ServiceBusSessionReceiver from a connection string.

        :param conn_str: The connection string of a Service Bus.
        :keyword str queue_name: The path of specific Service Bus Queue the client connects to.
        :keyword str topic_name: The path of specific Service Bus Topic which contains the Subscription
         the client connects to.
        :keyword str subscription_name: The path of specific Service Bus Subscription under the
         specified Topic the client connects to.
        :keyword mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :paramtype mode: ~azure.servicebus.ReceiveSettleMode
        :keyword session_id: A specific session from which to receive. This must be specified for a
         sessionful entity, otherwise it must be None. In order to receive messages from the next available
         session, set this to None.  The default is None.
        :paramtype session_id: str
        :keyword int prefetch: The maximum number of messages to cache with each request to the service.
         The default value is 0, meaning messages will be received from the service and processed
         one at a time. Increasing this value will improve message throughput performance but increase
         the change that messages will expire while they are cached if they're not processed fast enough.
        :keyword float idle_timeout: The timeout in seconds between received messages after which the receiver will
         automatically shutdown. The default value is 0, meaning no timeout.
        :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :keyword transport_type: The type of transport protocol that will be used for communicating with
         the Service Bus service. Default is `TransportType.Amqp`.
        :paramtype transport_type: ~azure.servicebus.TransportType
        :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
         Additionally the following keys may also be present: `'username', 'password'`.
        :rtype: ~azure.servicebus.ServiceBusSessionReceiver

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_servicebus_receiver_from_conn_str_sync]
                :end-before: [END create_servicebus_receiver_from_conn_str_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusReceiver from connection string.

        """
        return super(ServiceBusSessionReceiver, cls).from_connection_string(conn_str, **kwargs)

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, TYPE_CHECKING
from threading import RLock
import time

from uamqp import AMQPClient, c_uamqp
from uamqp.constants import LinkCreationMode

from ._base_handler import _parse_conn_str, ServiceBusSharedKeyCredential
from ._servicebus_sender import ServiceBusSender
from ._servicebus_receiver import ServiceBusReceiver
from ._servicebus_session_receiver import ServiceBusSessionReceiver
from ._common._servicebus_connection import (
    SeparateServiceBusConnection,
    SharedServiceBusConnection,
    CONNECTION_END_STATUS
)
from ._common._configuration import Configuration

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


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
     :class:`ServiceBusSharedKeyCredential<azure.servicebus.ServiceBusSharedKeyCredential>`, or credential objects
     generated by the azure-identity library and objects that implement the `get_token(self, *scopes)` method.
    :keyword str entity_name: Optional entity name, this can be the name of Queue or Topic.
     It must be specified if the credential is for specific Queue or Topic.
    :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the Service Bus service. Default is `TransportType.Amqp`.
    :paramtype transport_type: ~azure.servicebus.TransportType
    :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START create_sb_client_sync]
            :end-before: [END create_sb_client_sync]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the ServiceBusClient.

    """
    def __init__(
        self,
        fully_qualified_namespace,
        credential,
        **kwargs
    ):
        # type: (str, TokenCredential, Any) -> None
        self.fully_qualified_namespace = fully_qualified_namespace
        self._credential = credential
        self._config = Configuration(**kwargs)
        self._entity_name = kwargs.get("entity_name")
        self._auth_uri = "sb://{}".format(self.fully_qualified_namespace)
        if self._entity_name:
            self._auth_uri = "{}/{}".format(self._auth_uri, self._entity_name)
        # Internal flag for switching whether to apply connection sharing, pending fix in uamqp library
        self._connection_sharing = kwargs.get("connection_sharing", True)
        self._connection = SharedServiceBusConnection(self) \
            if self._connection_sharing else SeparateServiceBusConnection()
        self._mgmt_handlers = {}
        self._lock = RLock()
        self._mgmt_locks = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _get_management_handler(self, mgmt_target):
        # pylint:disable=protected-access
        #with self._lock:
            # if mgmt_target in self._mgmt_handlers and\
            #         self._mgmt_handlers[mgmt_target]._connection in CONNECTION_END_STATUS:
            #     try:
            #         self._mgmt_handlers[mgmt_target]._connection.lock(-1)
            #         self._mgmt_handlers[mgmt_target].close()
            #     finally:
            #         self._mgmt_handlers[mgmt_target]._connection.release()
            #         del self._mgmt_handlers[mgmt_target]
        if mgmt_target not in self._mgmt_handlers:
            try:
                mgmt_handler = AMQPClient(
                    mgmt_target,
                    link_creation_mode=LinkCreationMode.CreateLinkOnNewSession,
                    debug=self._config.logging_enable
                )
                self._connection.open_handler(mgmt_handler)
                #mgmt_handler.open(connection=self._connection.get_connection())
                # while not mgmt_handler.client_ready():
                #     time.sleep(0.05)
                self._mgmt_handlers[mgmt_target] = mgmt_handler
                self._mgmt_locks[mgmt_target] = RLock()
            except Exception as e:
                self._connection.close_handler(mgmt_handler)
                #self._connection.close_handler(mgmt_handler)
                raise
        return self._mgmt_handlers[mgmt_target]

    def _close_management_handler(self, mgmt_target):
        if mgmt_target in self._mgmt_handlers:
            with self._mgmt_locks[mgmt_target]:
                self._connection.close_handler(self._mgmt_handlers[mgmt_target])
        with self._lock:
            del self._mgmt_handlers[mgmt_target]
            del self._mgmt_locks[mgmt_target]

    def _mgmt_request(self, mgmt_target, mgmt_msg, mgmt_operation, **kwargs):
        with self._lock:
            mgmt_handler = self._get_management_handler(mgmt_target)
            mgmt_lock = self._mgmt_locks[mgmt_target]
        with mgmt_lock:
            # while not mgmt_handler.client_ready():
            #     time.sleep(0.05)
            return mgmt_handler.mgmt_request(
                mgmt_msg,
                mgmt_operation,
                **kwargs
            )

    def close(self):
        # type: () -> None
        """
        Close down the ServiceBus client and the underlying connection.

        :return: None
        """
        if self._connection_sharing and self._connection:
            self._connection.close()

    @classmethod
    def from_connection_string(
        cls,
        conn_str,
        **kwargs
    ):
        # type: (str, Any) -> ServiceBusClient
        """
        Create a ServiceBusClient from a connection string.

        :param str conn_str: The connection string of a Service Bus.
        :keyword str entity_name: Optional entity name, this can be the name of Queue or Topic.
         It must be specified if the credential is for specific Queue or Topic.
        :keyword bool logging_enable: Whether to output network trace logs to the logger. Default is `False`.
        :keyword transport_type: The type of transport protocol that will be used for communicating with
         the Service Bus service. Default is `TransportType.Amqp`.
        :paramtype transport_type: ~azure.servicebus.TransportType
        :keyword dict http_proxy: HTTP proxy settings. This must be a dictionary with the following
         keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
         Additionally the following keys may also be present: `'username', 'password'`.
        :rtype: ~azure.servicebus.ServiceBusClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_sb_client_from_conn_str_sync]
                :end-before: [END create_sb_client_from_conn_str_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusClient from connection string.

        """
        host, policy, key, entity_in_conn_str = _parse_conn_str(conn_str)
        return cls(
            fully_qualified_namespace=host,
            entity_name=entity_in_conn_str or kwargs.pop("entity_name", None),
            credential=ServiceBusSharedKeyCredential(policy, key),
            **kwargs
        )

    def get_queue_sender(self, queue_name, **kwargs):
        # type: (str, Any) -> ServiceBusSender
        """Get ServiceBusSender for the specific queue.

        :param str queue_name: The path of specific Service Bus Queue the client connects to.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :rtype: ~azure.servicebus.ServiceBusSender
        :raises: :class:`ServiceBusConnectionError`
         :class:`ServiceBusAuthorizationError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_servicebus_sender_from_sb_client_sync]
                :end-before: [END create_servicebus_sender_from_sb_client_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusSender from ServiceBusClient.

        """
        # pylint: disable=protected-access
        return ServiceBusSender(
            fully_qualified_namespace=self.fully_qualified_namespace,
            queue_name=queue_name,
            credential=self._credential,
            logging_enable=self._config.logging_enable,
            transport_type=self._config.transport_type,
            http_proxy=self._config.http_proxy,
            connection_sharing=self._connection_sharing,
            connection=self._connection,
            servicebus_client=self,
            **kwargs
        )

    def get_queue_receiver(self, queue_name, **kwargs):
        # type: (str, Any) -> ServiceBusReceiver
        """Get ServiceBusReceiver for the specific queue.

        :param str queue_name: The path of specific Service Bus Queue the client connects to.
        :keyword mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :paramtype mode: ~azure.servicebus.ReceiveSettleMode
        :keyword int prefetch: The maximum number of messages to cache with each request to the service.
         The default value is 0, meaning messages will be received from the service and processed
         one at a time. Increasing this value will improve message throughput performance but increase
         the change that messages will expire while they are cached if they're not processed fast enough.
        :keyword float idle_timeout: The timeout in seconds between received messages after which the receiver will
         automatically shutdown. The default value is 0, meaning no timeout.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :rtype: ~azure.servicebus.ServiceBusReceiver
        :raises: :class:`ServiceBusConnectionError`
         :class:`ServiceBusAuthorizationError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_servicebus_receiver_from_sb_client_sync]
                :end-before: [END create_servicebus_receiver_from_sb_client_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusReceiver from ServiceBusClient.


        """
        # pylint: disable=protected-access
        return ServiceBusReceiver(
            fully_qualified_namespace=self.fully_qualified_namespace,
            queue_name=queue_name,
            credential=self._credential,
            logging_enable=self._config.logging_enable,
            transport_type=self._config.transport_type,
            http_proxy=self._config.http_proxy,
            connection_sharing=self._connection_sharing,
            connection=self._connection,
            servicebus_client=self,
            **kwargs
        )

    def get_topic_sender(self, topic_name, **kwargs):
        # type: (str, Any) -> ServiceBusSender
        """Get ServiceBusSender for the specific topic.

        :param str topic_name: The path of specific Service Bus Topic the client connects to.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :keyword float retry_backoff_factor: Delta back-off internal in the unit of second between retries.
         Default value is 0.8.
        :keyword float retry_backoff_max: Maximum back-off interval in the unit of second. Default value is 120.
        :rtype: ~azure.servicebus.ServiceBusSender

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_topic_sender_from_sb_client_sync]
                :end-before: [END create_topic_sender_from_sb_client_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusSender from ServiceBusClient.

        """
        return ServiceBusSender(
            fully_qualified_namespace=self.fully_qualified_namespace,
            topic_name=topic_name,
            credential=self._credential,
            logging_enable=self._config.logging_enable,
            transport_type=self._config.transport_type,
            http_proxy=self._config.http_proxy,
            connection_sharing=self._connection_sharing,
            connection=self._connection,
            servicebus_client=self,
            **kwargs
        )

    def get_subscription_receiver(self, topic_name, subscription_name, **kwargs):
        # type: (str, str, Any) -> ServiceBusReceiver
        """Get ServiceBusReceiver for the specific subscription under the topic.

        :param str topic_name: The name of specific Service Bus Topic the client connects to.
        :param str subscription_name: The name of specific Service Bus Subscription
         under the given Service Bus Topic.
        :keyword mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the subscription. Messages received with ReceiveAndDelete
         will be immediately removed from the subscription, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :paramtype mode: ~azure.servicebus.ReceiveSettleMode
        :keyword int prefetch: The maximum number of messages to cache with each request to the service.
         The default value is 0, meaning messages will be received from the service and processed
         one at a time. Increasing this value will improve message throughput performance but increase
         the change that messages will expire while they are cached if they're not processed fast enough.
        :keyword float idle_timeout: The timeout in seconds between received messages after which the receiver will
         automatically shutdown. The default value is 0, meaning no timeout.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :keyword float retry_backoff_factor: Delta back-off internal in the unit of second between retries.
         Default value is 0.8.
        :keyword float retry_backoff_max: Maximum back-off interval in the unit of second. Default value is 120.
        :rtype: ~azure.servicebus.ServiceBusReceiver

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_subscription_receiver_from_sb_client_sync]
                :end-before: [END create_subscription_receiver_from_sb_client_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusReceiver from ServiceBusClient.


        """
        # pylint: disable=protected-access
        return ServiceBusReceiver(
            fully_qualified_namespace=self.fully_qualified_namespace,
            topic_name=topic_name,
            subscription_name=subscription_name,
            credential=self._credential,
            logging_enable=self._config.logging_enable,
            transport_type=self._config.transport_type,
            http_proxy=self._config.http_proxy,
            connection_sharing=self._connection_sharing,
            connection=self._connection,
            servicebus_client=self,
            **kwargs
        )

    def get_subscription_session_receiver(self, topic_name, subscription_name, session_id=None, **kwargs):
        # type: (str, str, Any) -> ServiceBusReceiver
        """Get ServiceBusReceiver for the specific subscription under the topic.

        :param str topic_name: The name of specific Service Bus Topic the client connects to.
        :param str subscription_name: The name of specific Service Bus Subscription
         under the given Service Bus Topic.
        :param str session_id: A specific session from which to receive. This must be specified for a
         sessionful entity, otherwise it must be None. In order to receive messages from the next available
         session, set this to None.  The default is None.
        :keyword mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the subscription. Messages received with ReceiveAndDelete
         will be immediately removed from the subscription, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :paramtype mode: ~azure.servicebus.ReceiveSettleMode
        :keyword int prefetch: The maximum number of messages to cache with each request to the service.
         The default value is 0, meaning messages will be received from the service and processed
         one at a time. Increasing this value will improve message throughput performance but increase
         the change that messages will expire while they are cached if they're not processed fast enough.
        :keyword float idle_timeout: The timeout in seconds between received messages after which the receiver will
         automatically shutdown. The default value is 0, meaning no timeout.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :keyword float retry_backoff_factor: Delta back-off internal in the unit of second between retries.
         Default value is 0.8.
        :keyword float retry_backoff_max: Maximum back-off interval in the unit of second. Default value is 120.
        :rtype: ~azure.servicebus.ServiceBusReceiver

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_subscription_receiver_from_sb_client_sync]
                :end-before: [END create_subscription_receiver_from_sb_client_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusReceiver from ServiceBusClient.


        """
        # pylint: disable=protected-access
        return ServiceBusSessionReceiver(
            fully_qualified_namespace=self.fully_qualified_namespace,
            topic_name=topic_name,
            subscription_name=subscription_name,
            credential=self._credential,
            logging_enable=self._config.logging_enable,
            transport_type=self._config.transport_type,
            http_proxy=self._config.http_proxy,
            connection_sharing=self._connection_sharing,
            connection=self._connection,
            session_id=session_id,
            servicebus_client=self,
            **kwargs
        )

    def get_queue_session_receiver(self, queue_name, session_id=None, **kwargs):
        # type: (str, str, Any) -> ServiceBusSessionReceiver
        """Get ServiceBusSessionReceiver for the specific queue.

        :param str queue_name: The path of specific Service Bus Queue the client connects to.
        :param str session_id: A specific session from which to receive. This must be specified for a
         sessionful entity, otherwise it must be None. In order to receive messages from the next available
         session, set this to None.  The default is None.
        :keyword mode: The mode with which messages will be retrieved from the entity. The two options
         are PeekLock and ReceiveAndDelete. Messages received with PeekLock must be settled within a given
         lock period before they will be removed from the queue. Messages received with ReceiveAndDelete
         will be immediately removed from the queue, and cannot be subsequently rejected or re-received if
         the client fails to process the message. The default mode is PeekLock.
        :paramtype mode: ~azure.servicebus.ReceiveSettleMode
        :keyword int prefetch: The maximum number of messages to cache with each request to the service.
         The default value is 0, meaning messages will be received from the service and processed
         one at a time. Increasing this value will improve message throughput performance but increase
         the change that messages will expire while they are cached if they're not processed fast enough.
        :keyword float idle_timeout: The timeout in seconds between received messages after which the receiver will
         automatically shutdown. The default value is 0, meaning no timeout.
        :keyword int retry_total: The total number of attempts to redo a failed operation when an error occurs.
         Default value is 3.
        :param int idle_timeout: The timeout in seconds between received messages after which the receiver will
         automatically shutdown. The default value is 0, meaning no timeout.
        :rtype: ~azure.servicebus.ServiceBusSessionReceiver
        :raises: :class:`ServiceBusConnectionError`
         :class:`ServiceBusAuthorizationError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START create_servicebus_receiver_from_sb_client_sync]
                :end-before: [END create_servicebus_receiver_from_sb_client_sync]
                :language: python
                :dedent: 4
                :caption: Create a new instance of the ServiceBusReceiver from ServiceBusClient.


        """
        # pylint: disable=protected-access
        return ServiceBusSessionReceiver(
            fully_qualified_namespace=self.fully_qualified_namespace,
            queue_name=queue_name,
            credential=self._credential,
            logging_enable=self._config.logging_enable,
            connection_sharing=self._connection_sharing,
            connection=self._connection,
            session_id=session_id,
            transport_type=self._config.transport_type,
            http_proxy=self._config.http_proxy,
            servicebus_client=self,
            **kwargs
        )


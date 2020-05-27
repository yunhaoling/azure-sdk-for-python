# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from threading import RLock
import time

from uamqp import Connection, c_uamqp

from .utils import create_authentication

CONNECTION_END_STATUS = (
    c_uamqp.ConnectionState.CLOSE_RCVD,
    c_uamqp.ConnectionState.CLOSE_SENT,
    c_uamqp.ConnectionState.DISCARDING,
    c_uamqp.ConnectionState.END,
    c_uamqp.ConnectionState.ERROR
)


class SharedServiceBusConnection(object):
    def __init__(self, client):
        self._conn = None
        self._client = client
        self._amqp_handlers = []
        self._lock = RLock()

    def _get_connection(self):
        # pylint:disable=c-extension-no-member
        if self._conn and self._conn._state in CONNECTION_END_STATUS:  # pylint:disable=protected-access:
            # try:
            #     self._conn.lock(-1)
            #     for handler in self._amqp_handlers:
            #         handler.close()
            # finally:
            #     self._conn.release()

            # self._amqp_handlers.clear()
            self._conn.destroy()
            self._conn = None

        if not self._conn:
            auth = create_authentication(self._client)
            self._conn = Connection(
                self._client.fully_qualified_namespace,
                auth,
                debug=self._client._config.logging_enable  # pylint:disable=protected-access
            )
        return self._conn

    def close(self):
        with self._lock:
            # try:
            #     self._conn.lock(-1)
            #     for handler in self._amqp_handlers:
            #         handler.close()
            # finally:
            #     self._conn.release()

            for handler in self._amqp_handlers:
                handler.close()

            self._amqp_handlers.clear()
            self._conn.destroy()
            self._conn = None

    def open_handler(self, amqp_handler):
        with self._lock:
            amqp_handler.open(self._get_connection())
            while not amqp_handler.client_ready():
                time.sleep(0.05)
            if amqp_handler not in self._amqp_handlers:
                self._amqp_handlers.append(amqp_handler)

    def close_handler(self, amqp_handler):
        connection = amqp_handler._connection
        try:
            connection.lock(-1)
            amqp_handler.close()
        finally:
            connection.release()

        with self._lock:
            if amqp_handler in self._amqp_handlers:
                self._amqp_handlers.remove(amqp_handler)


class SeparateServiceBusConnection(object):
    def __init__(self):
        pass

    def get_connection(self):
        pass

    def close(self):
        pass

    def open_handler(self, amqp_handler):
        amqp_handler.open()

    def close_handler(self, amqp_handler):
        amqp_handler.close()

from azure.servicebus import ServiceBusClient, ServiceBusReceiver, Message
import logging
import time
import random
from concurrent.futures import ThreadPoolExecutor
from uamqp import errors, c_uamqp
from threading import RLock
import gc
import os


logger = logging.getLogger("uamqp")
#logger.setLevel(logging.CRITICAL)
logger.disabled = True

azure_logger = logging.getLogger("azure.servicebus")
#azure_logger.setLevel(logging.CRITICAL)
#azure_logger.addHandler(logging.StreamHandler())

#logging.basicConfig(level=logging.DEBUG)

conn_str = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

lock = RLock()

#id_dict = {}

def destroy_connection(sb_client, lock):
    with lock:
        #sb_client._connection._conn._conn.destroy()
        #sb_client._connection._conn.destroy()
        sb_client._connection._conn._error = errors.ConnectionClose(b"amqp:internal-error")
        sb_client._connection._conn._state = c_uamqp.ConnectionState.ERROR


with ServiceBusClient.from_connection_string(
        conn_str,
        logging_enable=True
) as sb_client:
    sender_1 = sb_client.get_queue_sender(queue_name)
    sender_2 = sb_client.get_queue_sender(queue_name)
    sender_3 = sb_client.get_queue_sender(queue_name)
    sender_4 = sb_client.get_queue_sender(queue_name)
    sender_5 = sb_client.get_queue_sender(queue_name)
    sender_6 = sb_client.get_queue_sender(queue_name)
    receiver_1 = sb_client.get_queue_receiver(queue_name, idle_timeout=60)
    receiver_2 = sb_client.get_queue_receiver(queue_name, idle_timeout=60)
    receiver_3 = sb_client.get_queue_receiver(queue_name, idle_timeout=60)
    receiver_4 = sb_client.get_queue_receiver(queue_name, idle_timeout=60)
    receiver_5 = sb_client.get_queue_receiver(queue_name, idle_timeout=60)
    receiver_6 = sb_client.get_queue_receiver(queue_name, idle_timeout=60)

    id_dict = {
        id(sender_1): 'sender#1',
        id(sender_2): 'sender#2',
        id(sender_3): 'sender#3',
        id(sender_4): 'sender#4',
        id(sender_5): 'sender#3',
        id(sender_6): 'sender#4',
        id(receiver_1): 'receiver#1',
        id(receiver_2): 'receiver#2',
        id(receiver_3): 'receiver#3',
        id(receiver_4): 'receiver#4',
        id(receiver_5): 'receiver#5',
        id(receiver_6): 'receiver#6',
    }

    random_interruption = random.randint(4, 11)

    def send(sender):
        global id_dict

        with sender:
            while True:
                try:
                    msg = [Message("test message"), Message("test message"), Message("test message"), Message("test message")]
                    #msg.properties.message_id = str(id(sender)+i)
                    sender.send(msg)
                    print(id_dict[id(sender)] + '----- send message done')

                    with sb_client._connection._lock:
                        sb_client._connection._conn._error = errors.ConnectionClose(b"amqp:internal-error")
                        sb_client._connection._conn._state = c_uamqp.ConnectionState.ERROR
                    gc.collect()
                except Exception as e:
                    print(id_dict[id(sender)] + '----- meeting error' + str(type(e)) + str(e))
                    #print('sender error', type(e), e)


    def receive(receiver):
        global id_dict

        with receiver:
            while True:
                try:
                    msg_count = 0
                    while True:
                        msgs = receiver.receive()
                        if len(msgs) > 0:
                            msgs[0].complete()
                    # for msg in receiver:
                    #     print('I am here 3')
                    #     msg.complete()
                    #     print('I am here 4')
                        print(id_dict[id(receiver)] + '----- receive and complete message done')
                        msg_count += 1
                        # manually destroy uamqp connection and set error state
                        # with sb_client._lock:
                        #     sb_client._connection._conn._error = errors.ConnectionClose(b"amqp:internal-error")
                        #     sb_client._connection._conn._state = c_uamqp.ConnectionState.ERROR
                            #sb_client._connection._conn.destroy()
                except Exception as e:
                    print(id_dict[id(receiver)] + '----- meeting error' + str(type(e)) + str(e))

        print('################################### I am out of the while true loop unexpectedly')

    # with sender_1, sender_2, sender_3, sender_4, receiver_1, receiver_2, receiver_3, receiver_4, receiver_5, receiver_6:
    #     assert sender_1._connection._conn and sender_2._connection._conn and receiver_1._connection._conn and receiver_2._connection._conn
    #     assert sender_1._connection._conn == receiver_1._connection._conn == sender_2._connection._conn == receiver_2._connection._conn

    with ThreadPoolExecutor(max_workers=12) as executor:
        send_future1 = executor.submit(send, sender_1)
        send_future2 = executor.submit(send, sender_2)
        send_future3 = executor.submit(send, sender_3)
        send_future4 = executor.submit(send, sender_4)
        send_future5 = executor.submit(send, sender_5)
        send_future6 = executor.submit(send, sender_6)
        future_1 = executor.submit(receive, receiver_1)
        future_2 = executor.submit(receive, receiver_2)
        future_3 = executor.submit(receive, receiver_3)
        future_4 = executor.submit(receive, receiver_4)
        future_5 = executor.submit(receive, receiver_5)
        future_6 = executor.submit(receive, receiver_6)

        print(send_future1.result())
        print(send_future2.result())
        print(send_future3.result())
        print(send_future4.result())
        print(send_future5.result())
        print(send_future6.result())
        print(future_1.result())
        print(future_2.result())
        #print(future_3.result())
        #print(future_4.result())
        # print(future_5.result())
        # print(future_6.result())
        #assert future_1.result() and future_2.result()
        #assert (future_1.result() + future_2.result()) == 100

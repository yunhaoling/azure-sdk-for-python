#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition as an epoch receiver.
"""

import os
import time
import logging
import asyncio

from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventHubSharedKeyCredential

import examples
logger = examples.get_logger(logging.INFO)

HOSTNAME = os.environ.get('EVENT_HUB_HOSTNAME')  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ.get('EVENT_HUB_NAME')

USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

EXCLUSIVE_RECEIVER_PRIORITY = 42
PARTITION = "0"


async def pump(client, exclusive_receiver_priority):
    receiver = client.create_receiver(partition_id=PARTITION, exclusive_receiver_priority=exclusive_receiver_priority)
    async with receiver:
        total = 0
        start_time = time.time()
        for event_data in await receiver.receive(timeout=5):
            last_offset = event_data.offset
            last_sn = event_data.sequence_number
            total += 1
        end_time = time.time()
        run_time = end_time - start_time
        print("Received {} messages in {} seconds".format(total, run_time))

try:
    if not HOSTNAME:
        raise ValueError("No EventHubs URL supplied.")

    loop = asyncio.get_event_loop()
    client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                            network_tracing=False)
    loop.run_until_complete(pump(client, 20))
    loop.close()

except KeyboardInterrupt:
    pass

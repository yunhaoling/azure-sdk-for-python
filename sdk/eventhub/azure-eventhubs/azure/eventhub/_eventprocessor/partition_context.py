# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
from .partition_manager import PartitionManager

_LOGGER = logging.getLogger(__name__)


class PartitionContext(object):
    """Contains partition related context information for a PartitionProcessor instance to use.

    Users can use update_checkpoint() of this class to save checkpoint data.
    """
    def __init__(self, fully_qualified_namespace, eventhub_name, consumer_group_name,
                 partition_id, partition_manager=None):
        # type: (str, str, str, str, str, PartitionManager) -> None
        self.fully_qualified_namespace = fully_qualified_namespace
        self.partition_id = partition_id
        self.eventhub_name = eventhub_name
        self.consumer_group_name = consumer_group_name
        self._partition_manager = partition_manager
        self._last_received_event = None

    @property
    def last_enqueued_event_properties(self):
        """
        The latest enqueued event information. This property will be updated each time an event is received when
        the receiver is created with `track_last_enqueued_event_properties` being `True`.
        The dict includes following information of the partition:

            - `sequence_number`
            - `offset`
            - `enqueued_time`
            - `retrieval_time`

        :rtype: dict or None
        """
        if self._last_received_event:
            return self._last_received_event._get_last_enqueued_event_properties()  # pylint: disable=protected-access

    def update_checkpoint(self, event):
        """
        Updates the checkpoint using the given information for the associated partition and consumer group in the
        chosen storage service.

        :param ~azure.eventhub.EventData event: The EventData instance which contains the offset and
         sequence number information used for checkpoint.
        :rtype: None
        """
        if self._partition_manager:
            self._partition_manager.update_checkpoint(
                self.fully_qualified_namespace, self.eventhub_name, self.consumer_group_name,
                self.partition_id, event.offset, event.sequence_number
            )
        else:
            _LOGGER.info(
                "namespace %r, eventhub %r, consumer_group %r, partition_id %r "
                "update_checkpoint is called without partition manager. No checkpoint is updated.",
                self.fully_qualified_namespace, self.eventhub_name, self.consumer_group_name, self.partition_id)

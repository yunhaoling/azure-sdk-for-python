from azure.eventhub import EventPosition


class EventProcessorMixin(object):

    def get_init_event_position(self, partition_id, checkpoint):
        checkpoint_offset = checkpoint.get("offset") if checkpoint else None
        if checkpoint_offset:
            initial_event_position = EventPosition(checkpoint_offset)
        elif isinstance(self._initial_event_position, EventPosition):
            initial_event_position = self._initial_event_position
        elif isinstance(self._initial_event_position, dict):
            initial_event_position = self._initial_event_position.get(partition_id, EventPosition("-1"))
        else:
            initial_event_position = EventPosition(self._initial_event_position)
        return initial_event_position

    def create_consumer(self, partition_id, initial_event_position):
        consumer = self._eventhub_client._create_consumer(  # pylint: disable=protected-access
            self._consumer_group_name,
            partition_id,
            initial_event_position,
            owner_level=self._owner_level,
            track_last_enqueued_event_properties=self._track_last_enqueued_event_properties,
            prefetch=self._prefetch,
        )
        return consumer

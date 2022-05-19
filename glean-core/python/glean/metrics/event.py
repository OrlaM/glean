# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import enum
from typing import Dict, List, Optional, Union


from .._uniffi import CommonMetricData
from .._uniffi import EventMetric
from .._uniffi import RecordedEvent
from ..testing import ErrorType


class EventExtras:
    """
    A class that can be converted into key-value pairs of event extras.
    This will be automatically implemented for event properties of an [EventMetricType].
    """

    def to_ffi_extra(self) -> Dict[str, str]:
        """
        Convert the event extras into a key-value dict:
        """
        return {}


class EventMetricType:
    """
    This implements the developer facing API for recording events.

    Instances of this class type are automatically generated by
    `glean.load_metrics`, allowing developers to record values that were
    previously registered in the metrics.yaml file.

    The event API only exposes the `EventMetricType.record` method, which
    takes care of validating the input data and making sure that limits are
    enforced.
    """

    def __init__(
        self,
        common_metric_data: CommonMetricData,
        allowed_extra_keys: List[str],
    ):
        self._inner = EventMetric(common_metric_data, allowed_extra_keys)

    def record(
        self, extra: Optional[Union[Dict[str, str], EventExtras]] = None
    ) -> None:
        """
        Record an event by using the information provided by the instance of
        this class.

        Args:
            extra: optional. The extra keys and values for this event.
                   The maximum length for values is 100.
        """

        if isinstance(extra, EventExtras):
            extra = extra.to_ffi_extra()
        elif isinstance(extra, dict):

            def key_to_str(key):
                if isinstance(key, enum.Enum):
                    return key.value
                else:
                    return str(key)

            extra = {key_to_str(k): v for k, v in extra.items()}
        else:
            extra = {}

        self._inner.record(extra)

    def test_get_value(self, ping_name: Optional[str] = None) -> Optional[List[RecordedEvent]]:
        """
        Returns the stored value for testing purposes only.

        Args:
            ping_name (str): (default: first value in send_in_pings) The name
                of the ping to retrieve the metric for.

        Returns:
            value (list of RecordedEventData): value of the stored events.
        """
        # Translate NO extras into an empty dictionary,
        # to simplify handling.
        recordings = self._inner.test_get_value(ping_name)
        if recordings:
            for recording in recordings:
                if recording.extra is None:
                    recording.extra = {}

        return recordings

    def test_get_num_recorded_errors(
        self, error_type: ErrorType, ping_name: Optional[str] = None
    ) -> int:
        """
        Returns the number of errors recorded for the given metric.

        Args:
            error_type (ErrorType): The type of error recorded.
            ping_name (str): (default: first value in send_in_pings) The name
                of the ping to retrieve the metric for.

        Returns:
            num_errors (int): The number of errors recorded for the metric for
                the given error type.
        """
        return self._inner.test_get_num_recorded_errors(error_type, ping_name)


__all__ = ["EventMetricType", "RecordedEvent", "EventExtras"]

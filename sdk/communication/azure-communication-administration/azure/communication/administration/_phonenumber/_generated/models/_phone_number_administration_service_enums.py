# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from enum import Enum, EnumMeta
from six import with_metaclass

class _CaseInsensitiveEnumMeta(EnumMeta):
    def __getitem__(self, name):
        return super().__getitem__(name.upper())

    def __getattr__(cls, name):
        """Return the enum member matching `name`
        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.
        """
        try:
            return cls._member_map_[name.upper()]
        except KeyError:
            raise AttributeError(name)


class ActivationState(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The activation state of the phone number. Can be "Activated", "AssignmentPending",
    "AssignmentFailed", "UpdatePending", "UpdateFailed"
    """

    ACTIVATED = "Activated"
    ASSIGNMENT_PENDING = "AssignmentPending"
    ASSIGNMENT_FAILED = "AssignmentFailed"
    UPDATE_PENDING = "UpdatePending"
    UPDATE_FAILED = "UpdateFailed"

class AssignmentStatus(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The assignment status of the phone number. Conveys what type of entity the number is assigned
    to.
    """

    UNASSIGNED = "Unassigned"
    UNKNOWN = "Unknown"
    USER_ASSIGNED = "UserAssigned"
    CONFERENCE_ASSIGNED = "ConferenceAssigned"
    FIRST_PARTY_APP_ASSIGNED = "FirstPartyAppAssigned"
    THIRD_PARTY_APP_ASSIGNED = "ThirdPartyAppAssigned"

class CapabilitiesUpdateStatus(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """Status of the capabilities update.
    """

    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    COMPLETE = "Complete"
    ERROR = "Error"

class Capability(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """Represents the capabilities of a phone number.
    """

    USER_ASSIGNMENT = "UserAssignment"
    FIRST_PARTY_VOICE_APP_ASSIGNMENT = "FirstPartyVoiceAppAssignment"
    CONFERENCE_ASSIGNMENT = "ConferenceAssignment"
    P2_P_SMS_ENABLED = "P2PSmsEnabled"
    GEOGRAPHIC = "Geographic"
    NON_GEOGRAPHIC = "NonGeographic"
    TOLL_CALLING = "TollCalling"
    TOLL_FREE_CALLING = "TollFreeCalling"
    PREMIUM = "Premium"
    P2_P_SMS_CAPABLE = "P2PSmsCapable"
    A2_P_SMS_CAPABLE = "A2PSmsCapable"
    A2_P_SMS_ENABLED = "A2PSmsEnabled"
    CALLING = "Calling"
    TOLL_FREE = "TollFree"
    FIRST_PARTY_APP_ASSIGNMENT = "FirstPartyAppAssignment"
    THIRD_PARTY_APP_ASSIGNMENT = "ThirdPartyAppAssignment"
    AZURE = "Azure"
    OFFICE365 = "Office365"
    INBOUND_CALLING = "InboundCalling"
    OUTBOUND_CALLING = "OutboundCalling"
    INBOUND_A2_P_SMS = "InboundA2PSms"
    OUTBOUND_A2_P_SMS = "OutboundA2PSms"
    INBOUND_P2_P_SMS = "InboundP2PSms"
    OUTBOUND_P2_P_SMS = "OutboundP2PSms"

class CurrencyType(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The currency of a phone plan group
    """

    USD = "USD"

class LocationType(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The location type of the phone plan.
    """

    CIVIC_ADDRESS = "CivicAddress"
    NOT_REQUIRED = "NotRequired"
    SELECTION = "Selection"

class PhoneNumberReleaseStatus(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The release status of a phone number.
    """

    PENDING = "Pending"
    SUCCESS = "Success"
    ERROR = "Error"
    IN_PROGRESS = "InProgress"

class PhoneNumberType(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The phone number type of the plan group
    """

    UNKNOWN = "Unknown"
    GEOGRAPHIC = "Geographic"
    TOLL_FREE = "TollFree"
    INDIRECT = "Indirect"

class ReleaseStatus(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The release status.
    """

    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    COMPLETE = "Complete"
    FAILED = "Failed"
    EXPIRED = "Expired"

class SearchStatus(with_metaclass(_CaseInsensitiveEnumMeta, str, Enum)):
    """The status of the search.
    """

    PENDING = "Pending"
    IN_PROGRESS = "InProgress"
    RESERVED = "Reserved"
    EXPIRED = "Expired"
    EXPIRING = "Expiring"
    COMPLETING = "Completing"
    REFRESHING = "Refreshing"
    SUCCESS = "Success"
    MANUAL = "Manual"
    CANCELLED = "Cancelled"
    CANCELLING = "Cancelling"
    ERROR = "Error"
    PURCHASE_PENDING = "PurchasePending"

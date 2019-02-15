# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class EvaluatedNetworkSecurityGroup(Model):
    """Results of network security group evaluation.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param network_security_group_id: Network security group ID.
    :type network_security_group_id: str
    :param applied_to: Resource ID of nic or subnet to which network security
     group is applied.
    :type applied_to: str
    :param matched_rule:
    :type matched_rule: ~azure.mgmt.network.v2018_10_01.models.MatchedRule
    :ivar rules_evaluation_result: List of network security rules evaluation
     results.
    :vartype rules_evaluation_result:
     list[~azure.mgmt.network.v2018_10_01.models.NetworkSecurityRulesEvaluationResult]
    """

    _validation = {
        'rules_evaluation_result': {'readonly': True},
    }

    _attribute_map = {
        'network_security_group_id': {'key': 'networkSecurityGroupId', 'type': 'str'},
        'applied_to': {'key': 'appliedTo', 'type': 'str'},
        'matched_rule': {'key': 'matchedRule', 'type': 'MatchedRule'},
        'rules_evaluation_result': {'key': 'rulesEvaluationResult', 'type': '[NetworkSecurityRulesEvaluationResult]'},
    }

    def __init__(self, *, network_security_group_id: str=None, applied_to: str=None, matched_rule=None, **kwargs) -> None:
        super(EvaluatedNetworkSecurityGroup, self).__init__(**kwargs)
        self.network_security_group_id = network_security_group_id
        self.applied_to = applied_to
        self.matched_rule = matched_rule
        self.rules_evaluation_result = None

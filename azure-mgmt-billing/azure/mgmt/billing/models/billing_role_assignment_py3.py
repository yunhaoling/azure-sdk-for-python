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

from .resource_py3 import Resource


class BillingRoleAssignment(Resource):
    """a role assignment.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :ivar id: Resource Id.
    :vartype id: str
    :ivar name: Resource name.
    :vartype name: str
    :ivar type: Resource type.
    :vartype type: str
    :ivar created_on: the date the role assignment is created
    :vartype created_on: str
    :ivar created_by_principal_tenant_id: the creator's tenant Id
    :vartype created_by_principal_tenant_id: str
    :ivar created_by_principal_id: the creator's principal Id
    :vartype created_by_principal_id: str
    :ivar billing_role_assignment_name: the name of the role assignment
    :vartype billing_role_assignment_name: str
    :ivar principal_id: The user's principal id that the role gets assigned to
    :vartype principal_id: str
    :ivar role_definition_name: The role definition id
    :vartype role_definition_name: str
    :ivar scope: The scope the role get assigned to
    :vartype scope: str
    """

    _validation = {
        'id': {'readonly': True},
        'name': {'readonly': True},
        'type': {'readonly': True},
        'created_on': {'readonly': True},
        'created_by_principal_tenant_id': {'readonly': True},
        'created_by_principal_id': {'readonly': True},
        'billing_role_assignment_name': {'readonly': True},
        'principal_id': {'readonly': True},
        'role_definition_name': {'readonly': True},
        'scope': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
        'created_on': {'key': 'properties.createdOn', 'type': 'str'},
        'created_by_principal_tenant_id': {'key': 'properties.createdByPrincipalTenantId', 'type': 'str'},
        'created_by_principal_id': {'key': 'properties.createdByPrincipalId', 'type': 'str'},
        'billing_role_assignment_name': {'key': 'properties.name', 'type': 'str'},
        'principal_id': {'key': 'properties.principalId', 'type': 'str'},
        'role_definition_name': {'key': 'properties.roleDefinitionName', 'type': 'str'},
        'scope': {'key': 'properties.scope', 'type': 'str'},
    }

    def __init__(self, **kwargs) -> None:
        super(BillingRoleAssignment, self).__init__(**kwargs)
        self.created_on = None
        self.created_by_principal_tenant_id = None
        self.created_by_principal_id = None
        self.billing_role_assignment_name = None
        self.principal_id = None
        self.role_definition_name = None
        self.scope = None

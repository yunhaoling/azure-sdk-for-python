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

from msrest.service_client import SDKClient
from msrest import Serializer, Deserializer
from msrestazure import AzureConfiguration
from .version import VERSION
from msrest.pipeline import ClientRawResponse
from msrest.polling import LROPoller, NoPolling
from msrestazure.polling.arm_polling import ARMPolling
import uuid
from .operations.billing_accounts_operations import BillingAccountsOperations
from .operations.billing_accounts_with_create_invoice_section_permission_operations import BillingAccountsWithCreateInvoiceSectionPermissionOperations
from .operations.available_balance_by_billing_profile_operations import AvailableBalanceByBillingProfileOperations
from .operations.payment_methods_by_billing_profile_operations import PaymentMethodsByBillingProfileOperations
from .operations.billing_profiles_by_billing_account_name_operations import BillingProfilesByBillingAccountNameOperations
from .operations.billing_profiles_operations import BillingProfilesOperations
from .operations.invoice_sections_by_billing_account_name_operations import InvoiceSectionsByBillingAccountNameOperations
from .operations.invoice_sections_operations import InvoiceSectionsOperations
from .operations.invoice_sections_with_create_subscription_permission_operations import InvoiceSectionsWithCreateSubscriptionPermissionOperations
from .operations.departments_by_billing_account_name_operations import DepartmentsByBillingAccountNameOperations
from .operations.departments_operations import DepartmentsOperations
from .operations.enrollment_accounts_by_billing_account_name_operations import EnrollmentAccountsByBillingAccountNameOperations
from .operations.enrollment_accounts_operations import EnrollmentAccountsOperations
from .operations.invoices_by_billing_account_operations import InvoicesByBillingAccountOperations
from .operations.invoice_pricesheet_operations import InvoicePricesheetOperations
from .operations.invoices_by_billing_profile_operations import InvoicesByBillingProfileOperations
from .operations.invoice_operations import InvoiceOperations
from .operations.products_by_billing_subscriptions_operations import ProductsByBillingSubscriptionsOperations
from .operations.billing_subscriptions_by_billing_profile_operations import BillingSubscriptionsByBillingProfileOperations
from .operations.billing_subscriptions_by_invoice_section_operations import BillingSubscriptionsByInvoiceSectionOperations
from .operations.billing_subscription_operations import BillingSubscriptionOperations
from .operations.products_by_billing_account_operations import ProductsByBillingAccountOperations
from .operations.products_by_invoice_section_operations import ProductsByInvoiceSectionOperations
from .operations.products_operations import ProductsOperations
from .operations.transactions_by_billing_account_operations import TransactionsByBillingAccountOperations
from .operations.policy_operations import PolicyOperations
from .operations.billing_property_operations import BillingPropertyOperations
from .operations.operations import Operations
from .operations.billing_account_billing_permissions_operations import BillingAccountBillingPermissionsOperations
from .operations.invoice_sections_billing_permissions_operations import InvoiceSectionsBillingPermissionsOperations
from .operations.billing_profile_billing_permissions_operations import BillingProfileBillingPermissionsOperations
from .operations.billing_account_billing_role_definition_operations import BillingAccountBillingRoleDefinitionOperations
from .operations.invoice_section_billing_role_definition_operations import InvoiceSectionBillingRoleDefinitionOperations
from .operations.billing_profile_billing_role_definition_operations import BillingProfileBillingRoleDefinitionOperations
from .operations.billing_account_billing_role_assignment_operations import BillingAccountBillingRoleAssignmentOperations
from .operations.invoice_section_billing_role_assignment_operations import InvoiceSectionBillingRoleAssignmentOperations
from .operations.billing_profile_billing_role_assignment_operations import BillingProfileBillingRoleAssignmentOperations
from . import models


class BillingManagementClientConfiguration(AzureConfiguration):
    """Configuration for BillingManagementClient
    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: Azure Subscription ID.
    :type subscription_id: str
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, subscription_id, base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if subscription_id is None:
            raise ValueError("Parameter 'subscription_id' must not be None.")
        if not base_url:
            base_url = 'https://management.azure.com'

        super(BillingManagementClientConfiguration, self).__init__(base_url)

        self.add_user_agent('azure-mgmt-billing/{}'.format(VERSION))
        self.add_user_agent('Azure-SDK-For-Python')

        self.credentials = credentials
        self.subscription_id = subscription_id


class BillingManagementClient(SDKClient):
    """Billing client provides access to billing resources for Azure subscriptions.

    :ivar config: Configuration for client.
    :vartype config: BillingManagementClientConfiguration

    :ivar billing_accounts: BillingAccounts operations
    :vartype billing_accounts: azure.mgmt.billing.operations.BillingAccountsOperations
    :ivar billing_accounts_with_create_invoice_section_permission: BillingAccountsWithCreateInvoiceSectionPermission operations
    :vartype billing_accounts_with_create_invoice_section_permission: azure.mgmt.billing.operations.BillingAccountsWithCreateInvoiceSectionPermissionOperations
    :ivar available_balance_by_billing_profile: AvailableBalanceByBillingProfile operations
    :vartype available_balance_by_billing_profile: azure.mgmt.billing.operations.AvailableBalanceByBillingProfileOperations
    :ivar payment_methods_by_billing_profile: PaymentMethodsByBillingProfile operations
    :vartype payment_methods_by_billing_profile: azure.mgmt.billing.operations.PaymentMethodsByBillingProfileOperations
    :ivar billing_profiles_by_billing_account_name: BillingProfilesByBillingAccountName operations
    :vartype billing_profiles_by_billing_account_name: azure.mgmt.billing.operations.BillingProfilesByBillingAccountNameOperations
    :ivar billing_profiles: BillingProfiles operations
    :vartype billing_profiles: azure.mgmt.billing.operations.BillingProfilesOperations
    :ivar invoice_sections_by_billing_account_name: InvoiceSectionsByBillingAccountName operations
    :vartype invoice_sections_by_billing_account_name: azure.mgmt.billing.operations.InvoiceSectionsByBillingAccountNameOperations
    :ivar invoice_sections: InvoiceSections operations
    :vartype invoice_sections: azure.mgmt.billing.operations.InvoiceSectionsOperations
    :ivar invoice_sections_with_create_subscription_permission: InvoiceSectionsWithCreateSubscriptionPermission operations
    :vartype invoice_sections_with_create_subscription_permission: azure.mgmt.billing.operations.InvoiceSectionsWithCreateSubscriptionPermissionOperations
    :ivar departments_by_billing_account_name: DepartmentsByBillingAccountName operations
    :vartype departments_by_billing_account_name: azure.mgmt.billing.operations.DepartmentsByBillingAccountNameOperations
    :ivar departments: Departments operations
    :vartype departments: azure.mgmt.billing.operations.DepartmentsOperations
    :ivar enrollment_accounts_by_billing_account_name: EnrollmentAccountsByBillingAccountName operations
    :vartype enrollment_accounts_by_billing_account_name: azure.mgmt.billing.operations.EnrollmentAccountsByBillingAccountNameOperations
    :ivar enrollment_accounts: EnrollmentAccounts operations
    :vartype enrollment_accounts: azure.mgmt.billing.operations.EnrollmentAccountsOperations
    :ivar invoices_by_billing_account: InvoicesByBillingAccount operations
    :vartype invoices_by_billing_account: azure.mgmt.billing.operations.InvoicesByBillingAccountOperations
    :ivar invoice_pricesheet: InvoicePricesheet operations
    :vartype invoice_pricesheet: azure.mgmt.billing.operations.InvoicePricesheetOperations
    :ivar invoices_by_billing_profile: InvoicesByBillingProfile operations
    :vartype invoices_by_billing_profile: azure.mgmt.billing.operations.InvoicesByBillingProfileOperations
    :ivar invoice: Invoice operations
    :vartype invoice: azure.mgmt.billing.operations.InvoiceOperations
    :ivar products_by_billing_subscriptions: ProductsByBillingSubscriptions operations
    :vartype products_by_billing_subscriptions: azure.mgmt.billing.operations.ProductsByBillingSubscriptionsOperations
    :ivar billing_subscriptions_by_billing_profile: BillingSubscriptionsByBillingProfile operations
    :vartype billing_subscriptions_by_billing_profile: azure.mgmt.billing.operations.BillingSubscriptionsByBillingProfileOperations
    :ivar billing_subscriptions_by_invoice_section: BillingSubscriptionsByInvoiceSection operations
    :vartype billing_subscriptions_by_invoice_section: azure.mgmt.billing.operations.BillingSubscriptionsByInvoiceSectionOperations
    :ivar billing_subscription: BillingSubscription operations
    :vartype billing_subscription: azure.mgmt.billing.operations.BillingSubscriptionOperations
    :ivar products_by_billing_account: ProductsByBillingAccount operations
    :vartype products_by_billing_account: azure.mgmt.billing.operations.ProductsByBillingAccountOperations
    :ivar products_by_invoice_section: ProductsByInvoiceSection operations
    :vartype products_by_invoice_section: azure.mgmt.billing.operations.ProductsByInvoiceSectionOperations
    :ivar products: Products operations
    :vartype products: azure.mgmt.billing.operations.ProductsOperations
    :ivar transactions_by_billing_account: TransactionsByBillingAccount operations
    :vartype transactions_by_billing_account: azure.mgmt.billing.operations.TransactionsByBillingAccountOperations
    :ivar policy: Policy operations
    :vartype policy: azure.mgmt.billing.operations.PolicyOperations
    :ivar billing_property: BillingProperty operations
    :vartype billing_property: azure.mgmt.billing.operations.BillingPropertyOperations
    :ivar operations: Operations operations
    :vartype operations: azure.mgmt.billing.operations.Operations
    :ivar billing_account_billing_permissions: BillingAccountBillingPermissions operations
    :vartype billing_account_billing_permissions: azure.mgmt.billing.operations.BillingAccountBillingPermissionsOperations
    :ivar invoice_sections_billing_permissions: InvoiceSectionsBillingPermissions operations
    :vartype invoice_sections_billing_permissions: azure.mgmt.billing.operations.InvoiceSectionsBillingPermissionsOperations
    :ivar billing_profile_billing_permissions: BillingProfileBillingPermissions operations
    :vartype billing_profile_billing_permissions: azure.mgmt.billing.operations.BillingProfileBillingPermissionsOperations
    :ivar billing_account_billing_role_definition: BillingAccountBillingRoleDefinition operations
    :vartype billing_account_billing_role_definition: azure.mgmt.billing.operations.BillingAccountBillingRoleDefinitionOperations
    :ivar invoice_section_billing_role_definition: InvoiceSectionBillingRoleDefinition operations
    :vartype invoice_section_billing_role_definition: azure.mgmt.billing.operations.InvoiceSectionBillingRoleDefinitionOperations
    :ivar billing_profile_billing_role_definition: BillingProfileBillingRoleDefinition operations
    :vartype billing_profile_billing_role_definition: azure.mgmt.billing.operations.BillingProfileBillingRoleDefinitionOperations
    :ivar billing_account_billing_role_assignment: BillingAccountBillingRoleAssignment operations
    :vartype billing_account_billing_role_assignment: azure.mgmt.billing.operations.BillingAccountBillingRoleAssignmentOperations
    :ivar invoice_section_billing_role_assignment: InvoiceSectionBillingRoleAssignment operations
    :vartype invoice_section_billing_role_assignment: azure.mgmt.billing.operations.InvoiceSectionBillingRoleAssignmentOperations
    :ivar billing_profile_billing_role_assignment: BillingProfileBillingRoleAssignment operations
    :vartype billing_profile_billing_role_assignment: azure.mgmt.billing.operations.BillingProfileBillingRoleAssignmentOperations

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: Azure Subscription ID.
    :type subscription_id: str
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, subscription_id, base_url=None):

        self.config = BillingManagementClientConfiguration(credentials, subscription_id, base_url)
        super(BillingManagementClient, self).__init__(self.config.credentials, self.config)

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self.api_version = '2018-11-01-preview'
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)

        self.billing_accounts = BillingAccountsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_accounts_with_create_invoice_section_permission = BillingAccountsWithCreateInvoiceSectionPermissionOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.available_balance_by_billing_profile = AvailableBalanceByBillingProfileOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.payment_methods_by_billing_profile = PaymentMethodsByBillingProfileOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_profiles_by_billing_account_name = BillingProfilesByBillingAccountNameOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_profiles = BillingProfilesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.invoice_sections_by_billing_account_name = InvoiceSectionsByBillingAccountNameOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.invoice_sections = InvoiceSectionsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.invoice_sections_with_create_subscription_permission = InvoiceSectionsWithCreateSubscriptionPermissionOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.departments_by_billing_account_name = DepartmentsByBillingAccountNameOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.departments = DepartmentsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.enrollment_accounts_by_billing_account_name = EnrollmentAccountsByBillingAccountNameOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.enrollment_accounts = EnrollmentAccountsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.invoices_by_billing_account = InvoicesByBillingAccountOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.invoice_pricesheet = InvoicePricesheetOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.invoices_by_billing_profile = InvoicesByBillingProfileOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.invoice = InvoiceOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.products_by_billing_subscriptions = ProductsByBillingSubscriptionsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_subscriptions_by_billing_profile = BillingSubscriptionsByBillingProfileOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_subscriptions_by_invoice_section = BillingSubscriptionsByInvoiceSectionOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_subscription = BillingSubscriptionOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.products_by_billing_account = ProductsByBillingAccountOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.products_by_invoice_section = ProductsByInvoiceSectionOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.products = ProductsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.transactions_by_billing_account = TransactionsByBillingAccountOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.policy = PolicyOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_property = BillingPropertyOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.operations = Operations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_account_billing_permissions = BillingAccountBillingPermissionsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.invoice_sections_billing_permissions = InvoiceSectionsBillingPermissionsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_profile_billing_permissions = BillingProfileBillingPermissionsOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_account_billing_role_definition = BillingAccountBillingRoleDefinitionOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.invoice_section_billing_role_definition = InvoiceSectionBillingRoleDefinitionOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_profile_billing_role_definition = BillingProfileBillingRoleDefinitionOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_account_billing_role_assignment = BillingAccountBillingRoleAssignmentOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.invoice_section_billing_role_assignment = InvoiceSectionBillingRoleAssignmentOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.billing_profile_billing_role_assignment = BillingProfileBillingRoleAssignmentOperations(
            self._client, self.config, self._serialize, self._deserialize)

    def transactions_by_billing_profile(
            self, billing_account_name, billing_profile_name, start_date, end_date, filter=None, custom_headers=None, raw=False, **operation_config):
        """Lists the transactions by billingProfileName for given start date and
        end date.

        :param billing_account_name: billing Account Id.
        :type billing_account_name: str
        :param billing_profile_name: Billing Profile Id.
        :type billing_profile_name: str
        :param start_date: Start date
        :type start_date: str
        :param end_date: End date
        :type end_date: str
        :param filter: May be used to filter by transaction kind. The filter
         supports 'eq', 'lt', 'gt', 'le', 'ge', and 'and'. It does not
         currently support 'ne', 'or', or 'not'. Tag filter is a key value pair
         string where key and value is separated by a colon (:).
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: TransactionsListResult or ClientRawResponse if raw=true
        :rtype: ~azure.mgmt.billing.models.TransactionsListResult or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<azure.mgmt.billing.models.ErrorResponseException>`
        """
        # Construct URL
        url = self.transactions_by_billing_profile.metadata['url']
        path_format_arguments = {
            'billingAccountName': self._serialize.url("billing_account_name", billing_account_name, 'str'),
            'billingProfileName': self._serialize.url("billing_profile_name", billing_profile_name, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')
        query_parameters['startDate'] = self._serialize.query("start_date", start_date, 'str')
        query_parameters['endDate'] = self._serialize.query("end_date", end_date, 'str')
        if filter is not None:
            query_parameters['$filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('TransactionsListResult', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    transactions_by_billing_profile.metadata = {'url': '/providers/Microsoft.Billing/billingAccounts/{billingAccountName}/billingProfiles/{billingProfileName}/transactions'}

    def update_auto_renew_for_billing_account(
            self, billing_account_name, product_name, auto_renew=None, custom_headers=None, raw=False, **operation_config):
        """Cancel product by product id.

        :param billing_account_name: billing Account Id.
        :type billing_account_name: str
        :param product_name: Invoice Id.
        :type product_name: str
        :param auto_renew: Request parameters to update auto renew policy a
         product. Possible values include: 'true', 'false'
        :type auto_renew: str or ~azure.mgmt.billing.models.UpdateAutoRenew
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpdateAutoRenewOperationSummary or ClientRawResponse if
         raw=true
        :rtype: ~azure.mgmt.billing.models.UpdateAutoRenewOperationSummary or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<azure.mgmt.billing.models.ErrorResponseException>`
        """
        body = models.UpdateAutoRenewRequest(auto_renew=auto_renew)

        # Construct URL
        url = self.update_auto_renew_for_billing_account.metadata['url']
        path_format_arguments = {
            'billingAccountName': self._serialize.url("billing_account_name", billing_account_name, 'str'),
            'productName': self._serialize.url("product_name", product_name, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct body
        body_content = self._serialize.body(body, 'UpdateAutoRenewRequest')

        # Construct and send request
        request = self._client.post(url, query_parameters, header_parameters, body_content)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('UpdateAutoRenewOperationSummary', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    update_auto_renew_for_billing_account.metadata = {'url': '/providers/Microsoft.Billing/billingAccounts/{billingAccountName}/products/{productName}/updateAutoRenew'}

    def update_auto_renew_for_invoice_section(
            self, billing_account_name, invoice_section_name, product_name, auto_renew=None, custom_headers=None, raw=False, **operation_config):
        """Cancel auto renew for product by product id.

        :param billing_account_name: billing Account Id.
        :type billing_account_name: str
        :param invoice_section_name: InvoiceSection Id.
        :type invoice_section_name: str
        :param product_name: Invoice Id.
        :type product_name: str
        :param auto_renew: Request parameters to update auto renew policy a
         product. Possible values include: 'true', 'false'
        :type auto_renew: str or ~azure.mgmt.billing.models.UpdateAutoRenew
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpdateAutoRenewOperationSummary or ClientRawResponse if
         raw=true
        :rtype: ~azure.mgmt.billing.models.UpdateAutoRenewOperationSummary or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`ErrorResponseException<azure.mgmt.billing.models.ErrorResponseException>`
        """
        body = models.UpdateAutoRenewRequest(auto_renew=auto_renew)

        # Construct URL
        url = self.update_auto_renew_for_invoice_section.metadata['url']
        path_format_arguments = {
            'billingAccountName': self._serialize.url("billing_account_name", billing_account_name, 'str'),
            'invoiceSectionName': self._serialize.url("invoice_section_name", invoice_section_name, 'str'),
            'productName': self._serialize.url("product_name", product_name, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if self.config.generate_client_request_id:
            header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
        if custom_headers:
            header_parameters.update(custom_headers)
        if self.config.accept_language is not None:
            header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

        # Construct body
        body_content = self._serialize.body(body, 'UpdateAutoRenewRequest')

        # Construct and send request
        request = self._client.post(url, query_parameters, header_parameters, body_content)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise models.ErrorResponseException(self._deserialize, response)

        deserialized = None

        if response.status_code == 200:
            deserialized = self._deserialize('UpdateAutoRenewOperationSummary', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    update_auto_renew_for_invoice_section.metadata = {'url': '/providers/Microsoft.Billing/billingAccounts/{billingAccountName}/invoiceSections/{invoiceSectionName}/products/{productName}/updateAutoRenew'}

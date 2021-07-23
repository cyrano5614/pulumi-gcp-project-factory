import unittest

import pulumi


class TestMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + "_id", args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}


pulumi.runtime.set_mocks(TestMocks())

# It's important to import _after_ the mocks are defined.
from pulumi_gcp_project_factory.budget import (  # noqa isort:skip type: ignore
    Budget,
)

TEST_NAME = "test-resource"
TEST_BILLING_ACCOUNT = "test-billing-account"
# TEST_PROJECTS = ["test-12345"]
TEST_PROJECTS = []  # if project is defined, it tries to fetch project which errors
TEST_AMOUNT = 10000


class TestingWithMocks(unittest.TestCase):
    @pulumi.runtime.test
    def setUp(self):
        self.budget = Budget(
            TEST_NAME,
            billing_account=TEST_BILLING_ACCOUNT,
            projects=TEST_PROJECTS,
            amount=TEST_AMOUNT,
        )

    @pulumi.runtime.test
    def test_billing_account(self):
        def check_billing_account(args):
            project_id = args[0]
            self.assertEqual(project_id, TEST_BILLING_ACCOUNT)

        return pulumi.Output.all(self.budget.billing_account).apply(
            check_billing_account
        )  # noqa

    @pulumi.runtime.test
    def test_urn(self):
        def check_urn(args):
            urn = args[0][0]
            self.assertIn(TEST_NAME, urn)

        return pulumi.Output.all([self.budget.urn]).apply(check_urn)  # noqa

    @pulumi.runtime.test
    def test_budget_amount(self):
        def check_budget_amount(args):
            amount = args[0][0]
            self.assertEqual(amount, str(float(TEST_AMOUNT)))

        return pulumi.Output.all([self.budget.amount]).apply(check_budget_amount)

    # @pulumi.runtime.test
    # def test_project_service_identities(self):
    #     def check_project_service_identities(args):
    #         project_service_identities = args
    #         self.assertEqual(
    #             project_service_identities,
    #             [
    #                 test_api_identity["api"]
    #                 for test_api_identity in TEST_ACTIVATE_API_IDENTITIES
    #             ],
    #         )

    #     self.assertIsInstance(self.project_services.project_service_identities, dict)
    #     self.assertTrue(self.project_services.project_service_identities)

    #     return pulumi.Output.all(
    #         *[
    #             project_service_identity.service
    #             for _, project_service_identity in self.project_services.project_service_identities.items()  # noqa
    #         ]  # noqa
    #     ).apply(check_project_service_identities)

    # @pulumi.runtime.test
    # def test_project_service_identity_roles(self):
    #     def check_project_service_identity_roles(args):
    #         project_service_identity_roles = args
    #         self.assertEqual(
    #             project_service_identity_roles,
    #             [
    #                 role
    #                 for test_api_identity in TEST_ACTIVATE_API_IDENTITIES
    #                 for role in test_api_identity["roles"]
    #             ],
    #         )

    #     self.assertIsInstance(
    #         self.project_services.project_service_identity_roles, list
    #     )
    #     self.assertTrue(self.project_services.project_service_identity_roles)

    #     return pulumi.Output.all(
    #         *[
    #             project_service_identity_role.role
    #             for project_service_identity_role in self.project_services.project_service_identity_roles  # noqa
    #         ]  # noqa
    #     ).apply(check_project_service_identity_roles)

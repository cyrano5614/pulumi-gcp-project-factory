import unittest

import pulumi


class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + "_id", args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}


pulumi.runtime.set_mocks(MyMocks())

# It's important to import _after_ the mocks are defined.
from pulumi_gcp_project_factory.project_services import (  # noqa isort:skip type: ignore
    ProjectServices,
)

# from project import DEFAULT_APIS  # noqa isort:skip

TEST_NAME = "test-resource"
TEST_PROJECT_ID = "test-12345"

TEST_ACTIVATE_APIS = [
    "sqladmin.googleapis.com",
    "bigquery.googleapis.com",
]

TEST_ACTIVATE_API_IDENTITIES = [
    {
        "api": "healthcare.googleapis.com",
        "roles": [
            "roles/healthcare.serviceAgent",
            "roles/bigquery.jobUser",
        ],
    }
]


class TestingWithMocks(unittest.TestCase):
    @pulumi.runtime.test
    def setUp(self):
        self.project_services = ProjectServices(
            name=TEST_NAME,
            project_id=TEST_PROJECT_ID,
            activate_apis=TEST_ACTIVATE_APIS,
            activate_api_identities=TEST_ACTIVATE_API_IDENTITIES,  # type: ignore
        )

    @pulumi.runtime.test
    def test_project_id(self):
        def check_project_id(args):
            project_id = args[0]
            self.assertEqual(project_id, TEST_PROJECT_ID)

        return pulumi.Output.all(self.project_services.project_id).apply(
            check_project_id
        )  # noqa

    @pulumi.runtime.test
    def test_urn(self):
        def check_urn(args):
            urn = args[0][0]
            self.assertIn(TEST_NAME, urn)

        return pulumi.Output.all([self.project_services.urn]).apply(check_urn)  # noqa

    @pulumi.runtime.test
    def test_project_services(self):
        def check_project_services(args):
            api_services = args
            tmp_test_activate_apis = [api for api in TEST_ACTIVATE_APIS]
            tmp_test_activate_apis.extend(
                [identity["api"] for identity in TEST_ACTIVATE_API_IDENTITIES]
            )
            self.assertEqual(set(tmp_test_activate_apis), set(api_services))

        return pulumi.Output.all(
            *[
                project_service.service
                for project_service in self.project_services.project_services  # noqa
            ]  # noqa
        ).apply(check_project_services)

    @pulumi.runtime.test
    def test_project_service_identities(self):
        def check_project_service_identities(args):
            project_service_identities = args
            self.assertEqual(
                project_service_identities,
                [
                    test_api_identity["api"]
                    for test_api_identity in TEST_ACTIVATE_API_IDENTITIES
                ],
            )

        self.assertIsInstance(self.project_services.project_service_identities, dict)
        self.assertTrue(self.project_services.project_service_identities)

        return pulumi.Output.all(
            *[
                project_service_identity.service
                for _, project_service_identity in self.project_services.project_service_identities.items()  # noqa
            ]  # noqa
        ).apply(check_project_service_identities)

    @pulumi.runtime.test
    def test_project_service_identity_roles(self):
        def check_project_service_identity_roles(args):
            project_service_identity_roles = args
            self.assertEqual(
                project_service_identity_roles,
                [
                    role
                    for test_api_identity in TEST_ACTIVATE_API_IDENTITIES
                    for role in test_api_identity["roles"]
                ],
            )

        self.assertIsInstance(
            self.project_services.project_service_identity_roles, list
        )
        self.assertTrue(self.project_services.project_service_identity_roles)

        return pulumi.Output.all(
            *[
                project_service_identity_role.role
                for project_service_identity_role in self.project_services.project_service_identity_roles  # noqa
            ]  # noqa
        ).apply(check_project_service_identity_roles)

"""A Google Cloud Python Pulumi program for opionated admin project"""
from typing import Dict, List, Optional

import pulumi
import pulumi_gcp as gcp
import pulumi_random as random

from pulumi_gcp_project_factory.project_services import APIIdentity, ProjectServices

"""
defaults
"""
random_suffix = random.RandomId("random_suffix", byte_length=2)

# def generate_project_id():
#     return random_suffix.hex.apply(lambda suffix: f"{random_}-seed-{suffix}")


class CoreProjectFactory(pulumi.ComponentResource):
    """CoreProjectFactory."""

    def __init__(
        self,
        # Required
        name: str,
        org_id: str,
        # Optional
        billing_account: str,
        group_email: Optional[str] = None,
        group_role: Optional[str] = None,
        lien: bool = False,
        manage_group: bool = False,
        project_id: Optional[str] = None,
        random_project_id: bool = False,
        shared_vpc: Optional[str] = None,
        folder_id: Optional[str] = None,
        create_project_sa: bool = True,
        project_sa_name: str = "project-service-account",
        sa_role: Optional[str] = None,
        activate_apis: List[str] = [],
        activate_api_identities: List[APIIdentity] = [],
        usage_bucket_name: Optional[str] = None,
        usage_bucket_prefix: Optional[str] = None,
        shared_vpc_subnets: List[str] = [],
        labels: Dict[str, str] = {},
        bucket_project: Optional[str] = None,
        bucket_name: Optional[str] = None,
        bucket_location: str = "US",
        bucket_versioning: bool = False,
        bucket_force_destroy: bool = False,
        bucket_ula: bool = True,
        auto_create_network: bool = False,
        disable_services_on_destroy: bool = True,
        default_service_account: str = "disable",
        disable_dependent_services: bool = True,
        enable_shared_vpc_service_project: bool = False,
        enable_shared_vpc_host_project: bool = False,
        vpc_service_control_attach_enabled: bool = False,
        vpc_service_control_perimeter_name: Optional[str] = None,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """__init__.

        :param name: The name for the project
        :type name: str
        :param org_id: The organization ID.
        :type org_id: str
        :param billing_account: The ID of the billing account to associate this project
            with.
        :type billing_account: str
        :param group_email: The email address of a group to control the project by being
            assigned group_role.
        :type group_email: Optional[str]
        :param group_role: The role to give the controlling group (group_name) over the
            project.
        :type group_role: Optional[str]
        :param lien: Add a lien on the project to prevent accidental deletion
        :type lien: bool
        :param manage_group: A toggle to indicate if a G Suite group should be managed.
        :type manage_group: bool
        :param project_id: The ID to give the project. If not provided, the `name` will
            be used.
        :type project_id: Optional[str]
        :param random_project_id: Adds a suffix of 4 random characters to the
            `project_id`.
        :type random_project_id: bool
        :param shared_vpc: The ID of the host project which hosts the shared VPC
        :type shared_vpc: Optional[str]
        :param folder_id: The ID of a folder to host this project
        :type folder_id: Optional[str]
        :param create_project_sa: Whether the default service account for the project
            shall be created.
        :type create_project_sa: bool
        :param project_sa_name: Default service account name for the project, defaults
            to 'project-service-account'.
        :type project_sa_name: str
        :param sa_role: A role to give the default Service Account for the project,
            defaults to None.
        :type sa_role: Optional[str]
        :param activate_apis: The list of apis to activate within the project.
        :type activate_apis: List[str]
        :param activate_api_identities: The list of service identities (Google Managed
            service account for the API) to force-create for the project (e.g. in order
            to grant additional roles). APIs in this list will automatically be
            appended to `activate_apis`. Not including the API in this list will
            follow the default behaviour for identity creation
            (which is usually when the first resource using the API is created).
            Any roles (e.g. service agent role) must be explicitly listed. See
            https://cloud.google.com/iam/docs/understanding-roles#service-agent-roles-roles
            for a list of related roles.
        :type activate_api_identities: List[APIIdentity]
        :param usage_bucket_name: Name of a GCS bucket to store GCE usage reports in.
        :type usage_bucket_name: Optional[str]
        :param usage_bucket_prefix: Prefix in the GCS bucket to store GCE usage
            reports in.
        :type usage_bucket_prefix: Optional[str]
        :param shared_vpc_subnets: List of subnets fully qualified subnet IDs
            (ie. projects/$project_id/regions/$region/subnetworks/$subnet_id)
        :type shared_vpc_subnets: List[str]
        :param labels: Map of labels for project
        :type labels: Dict[str, str]
        :param bucket_project: A project to create a GCS bucket (bucket_name) in,
            useful for Terraform state.
        :type bucket_project: Optional[str]
        :param bucket_name: A name for a GCS bucket to create
            (in the bucket_project project), useful for Terraform state.
        :type bucket_name: Optional[str]
        :param bucket_location: The location for a GCS bucket to create.
        :type bucket_location: str
        :param bucket_versioning: Enable versioning for a GCS bucket to create,
            defaults to False.
        :type bucket_versioning: bool
        :param bucket_labels: Map of labels for bucket, defaults to {}
        :type bucket_labels: Dict[str, str]
        :param bucket_force_destroy: Force the deletion of all objects within
            the GCS bucket when deleting the bucket, defaults to False
        :type bucket_force_destroy: bool
        :param bucket_ula: Enable Uniform Bucket Level Access, defaults to True.
        :type bucket_ula: bool
        :param auto_create_network: Create the default network, defaults to False.
        :type auto_create_network: bool
        :param disable_services_on_destroy: Whether project services will be
            disabled when the resources are destroyed, defaults to True.
        :type disable_services_on_destroy: bool
        :param default_service_account: Project default service account setting:
            can be one of `delete`, `deprivilege`, `disable`, or `keep`,
            defaults to 'disable'.
        :type default_service_account: str
        :param disable_dependent_services: Whether services that are enabled and
            which depend on this service should also be disabled when this service
            is destroyed. Defaults to True.
        :type disable_dependent_services: bool
        :param enable_shared_vpc_service_project: If this project should be
            attached to a shared VPC. If true, you must set shared_vpc variable.
        :type enable_shared_vpc_service_project: bool
        :param enable_shared_vpc_host_project: If this project is a shared VPC
            host project. If true, you must *not* set shared_vpc variable.
            Defaults to false.
        :type enable_shared_vpc_host_project: bool
        :param vpc_service_control_attach_enabled: Whether the project will be
            attached to a VPC Service Control Perimeter. Defaults to False.
        :type vpc_service_control_attach_enabled: bool
        :param vpc_service_control_perimeter_name: The name of a VPC Service
            Control Perimeter to add the created project to, defaults to None.
        :type vpc_service_control_perimeter_name: Optional[str]
        :param opts:
        :type opts: Optional[pulumi.ResourceOptions]
        """
        super().__init__(
            t="projectfactory:gcp:CoreProjectFactory",
            name=name,
            props={},
            opts=opts,
        )

        group_id = f"group:{group_email}" if manage_group else None
        base_project_id = name if project_id is None else project_id
        project_org_id = org_id if folder_id is None else None
        project_folder_id = folder_id if folder_id is not None else None
        temp_project_id = (
            f"{base_project_id}-{random_project_id}"
            if random_project_id is not None
            else base_project_id
        )
        # api_s_account = main_project.number.apply(
        #     lambda number: f"{number}@cloudservices.gserviceaccount.com"
        # )
        # api_s_account_fmt = f"serviceAccount:{api_s_account}"
        # project_bucket_name = (
        #     bucket_name if bucket_name is not None else f"{temp_project_id}-state"
        # )
        # create_bucket = True if bucket_project is not None else False
        # shared_vpc_users = [
        #     user
        #     for user in [group_id, s_account_fmt, api_s_account_fmt]
        #     if user is not None
        # ]
        # shared_vpc_users_length = 3 if create_project_sa else 2

        """
        project
        """

        main_project = gcp.organizations.Project(
            "project",
            name=name,
            org_id=project_org_id,
            project_id=temp_project_id,
            folder_id=project_folder_id,
            auto_create_network=auto_create_network,
            billing_account=billing_account,
            labels=labels,
            opts=pulumi.ResourceOptions(parent=self),
        )

        """
        project lien
        """
        if lien:
            project_lien = gcp.resourcemanager.Lien(  # noqa
                "project_lien",
                origin="project-factory",
                parent=main_project.number.apply(lambda number: f"projects/{number}"),
                reason="Project Factory Lien",
                restrictions=["resourcemanager.projects.delete"],
                opts=pulumi.ResourceOptions(parent=self),
            )

        """
        project services
        """

        created_project_services = ProjectServices(  # noqa
            "project_services",
            project_id=main_project.project_id,
            activate_apis=activate_apis,
            activate_api_identities=activate_api_identities,
            disable_services_on_destroy=disable_services_on_destroy,
            disable_dependent_services=disable_dependent_services,
            opts=pulumi.ResourceOptions(parent=self),
        )

        """
        shared vpc configuration
        """
        # default_service_account_value = default_service_account.upper()
        # TODO: implement
        """
        default service account configuration
        """

        s_account_fmt = None
        if create_project_sa:
            _default_service_account = gcp.serviceaccount.Account(
                "default_service_account",
                account_id=project_sa_name,
                display_name=f"{name} Project Service Account",
                project=main_project.project_id,
                opts=pulumi.ResourceOptions(parent=self),
            )
            s_account_fmt = _default_service_account.email.apply(
                lambda email: f"serviceAccount:{email}"
            )

            # account_id
        """
        Policy to operate instances in shared subnetwork
        """
        if sa_role and create_project_sa:
            default_service_account_membership = gcp.projects.IAMMember(  # noqa
                "default_service_account_membership",
                project=main_project.project_id,
                role=sa_role,
                member=s_account_fmt,
                opts=pulumi.ResourceOptions(parent=self),
            )

        """
        Gsuite Group Role Configuration
        """
        if manage_group:
            gsuite_group_role = gcp.projects.IAMMember(  # noqa
                "gsuite_group_role",
                member=group_id,
                project=main_project.project_id,
                role=group_role,
                opts=pulumi.ResourceOptions(parent=self),
            )

        """
        Granting serviceAccountUser to group
        """
        if manage_group and create_project_sa:
            service_account_grant_to_group = gcp.serviceaccount.IAMMember(  # noqa
                "service_account_grant_to_group",
                member=group_id,
                role="roles/iam.serviceAccountUser",
                service_account_id=pulumi.Output.concat(
                    "projects/",
                    main_project.project_id,
                    "/serviceAccounts/",
                    _default_service_account.email,
                ),
            )

        """
        compute.networkUser role granted to G Suite group, APIs Service account,
        and Project Service Account
        """
        # TODO: implement

        """
        compute.networkUser role granted to Project Service Account on vpc subnets
        """
        # TODO: implement

        """
        compute.networkUser role granted to G Suite group on vpc subnets
        """
        # TODO: implement

        """
        compute.networkUser role granted to APIs Service Account on vpc subnets
        """
        # TODO: implement

        """
        Usage report export (to bucket) configuration
        """
        # TODO: implement

        """
        Project's bucket creation
        """
        # TODO: implement

        """
        Project's bucket storage.admin granting to group
        """
        # TODO: implement

        """
        Project's bucket storage.admin granting to default compute service account
        """
        # TODO: implement

        """
        Project's bucket storage.admin granting to Google APIs service account
        """
        # TODO: implement

        """
        Attachment to VPC Service Control Perimeter
        """
        # TODO: implement

        """
        Enable Access Context Manager API
        """
        # TODO: implement

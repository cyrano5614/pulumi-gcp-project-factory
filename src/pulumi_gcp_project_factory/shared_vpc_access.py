from itertools import product
from typing import Dict, List, Optional, Sequence  # noqa

import pulumi
import pulumi_gcp as gcp

# import pulumi_random as random


@pulumi.input_type
class SharedVPCAccessArgs:
    # Shorten without init call and getter/setters for property
    # https://github.com/pulumi/pulumi/blob/b16d50085b532f635605dc31ce68dc48881595f7/sdk/python/lib/pulumi/_types.py#L59

    host_project_id: pulumi.Input[str] = pulumi.property("hostProjectId")
    enable_shared_vpc_service_project: pulumi.Input[bool] = pulumi.property(
        "enableSharedVPCServiceProject"
    )
    service_project_id: pulumi.Input[str] = pulumi.property("serviceProjectId")
    service_project_number: Optional[pulumi.Input[str]] = pulumi.property(
        "serviceProjectNumber", default=None
    )
    lookup_project_numbers: pulumi.Input[bool] = pulumi.property(
        "lookupProjectNumbers", default=True
    )
    shared_vpc_subnets: pulumi.Input[Sequence[pulumi.Input[str]]] = pulumi.property(
        "sharedVPCSubnets", default=[]
    )
    active_apis: pulumi.Input[Sequence[pulumi.Input[str]]] = pulumi.property(
        "activeApis", default=[]
    )
    grant_services_security_admin_role: pulumi.Input[bool] = pulumi.property(
        "grantServicesSecurityAdminRole", default=False
    )


class SharedVPCAccess(pulumi.ComponentResource):
    def __init__(
        self,
        resource_name: str,
        host_project_id: pulumi.Input[str],
        enable_shared_vpc_service_project: pulumi.Input[bool],
        service_project_id: pulumi.Input[str],
        service_project_number: Optional[pulumi.Input[str]] = None,
        lookup_project_numbers: pulumi.Input[bool] = True,
        shared_vpc_subnets: pulumi.Input[Sequence[pulumi.Input[str]]] = [],
        active_apis: pulumi.Input[Sequence[pulumi.Input[str]]] = [],
        grant_services_security_admin_role: pulumi.Input[bool] = False,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """
        :param host_project_id: The ID of the host project which hosts the shared VPC
        :type host_project_id: pulumi.Input[str]
        :param enable_shared_vpc_service_project: Flag set if SVPC enabled.
        :type enable_shared_vpc_service_project: pulumi.Input[bool]
        :param service_project_id: The ID of the service project.
        :type service_project_id: pulumi.Input[str]
        :param service_project_number: Project number of the service project.
            Will be used if `lookup_service_project_number` is false.
        :type service_project_number: Optional[pulumi.Input[str]]
        :param lookup_project_numbers: Whether to look up the project numbers from
            data sources. If false, `service_project_number` will be used instead.
            Defaults to True.
        :type lookup_project_numbers: pulumi.Input[bool]
        :param shared_vpc_subnets: List of subnets fully qualified subnet IDs
            (ie. projects/$project_id/regions/$region/subnetworks/$subnet_id)
            Defaults to [].
        :type shared_vpc_subnets: pulumi.Input[Sequence[pulumi.Input[str]]]
        :param active_apis: The list of active apis on the service project.
            If api is not active this module will not try to activate it,
            defaults to [].
        :type active_apis: pulumi.Input[Sequence[pulumi.Input[str]]]
        :param grant_services_security_admin_role: Whether or not to grant
            Kubernetes Engine Service Agent the Security Admin role on the
            host project so it can manage firewall rules. Defaults to False.
        :type grant_services_security_admin_role: pulumi.Input[bool]
        """
        super().__init__(
            t="zityspace-gcp:projectfactory:SharedVPCAccess",
            name=resource_name,
            props={},
            opts=opts,
        )

        assert (
            service_project_number or lookup_project_numbers
        ), "One of 'service_project_number' or 'lookup_project_numbers'\
                needs to be specified!"
        self.service_project_number = (
            service_project_number
            if not lookup_project_numbers
            else self.get_service_project_number(service_project_id)
        )

        self.apis = {
            "container.googleapis.com": f"service-{self.service_project_number}@container-engine-robot.iam.gserviceaccount.com",  # noqa
            "dataproc.googleapis.com": f"service-{self.service_project_number}@dataproc-accounts.iam.gserviceaccount.com",  # noqa
            "dataflow.googleapis.com": f"service-{self.service_project_number}@dataflow-service-producer-prod.iam.gserviceaccount.com",  # noqa
            "composer.googleapis.com": f"service-{self.service_project_number}@cloudcomposer-accounts.iam.gserviceaccount.com",  # noqa
        }

        self.gke_shared_vpc_enabled = (
            "container.googleapis.com" in active_apis
        )  # type: ignore
        self.composer_shared_vpc_enabled = (
            "composer.googleapis.com" in active_apis
        )  # type: ignore
        self.active_apis = list(set(self.apis) & set(active_apis))  # type: ignore
        self.subnetwork_api = (
            []
            if not shared_vpc_subnets
            else list(set(product(active_apis, shared_vpc_subnets)))  # type: ignore
        )

        """ # noqa
          if "container.googleapis.com" compute.networkUser role granted to GKE service account for GKE on shared VPC subnets
          if "dataproc.googleapis.com" compute.networkUser role granted to dataproc service account for dataproc on shared VPC subnets
          if "dataflow.googleapis.com" compute.networkUser role granted to dataflow  service account for Dataflow on shared VPC subnets
          See: https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-shared-vpc
               https://cloud.google.com/dataflow/docs/concepts/security-and-permissions#cloud_dataflow_service_account
        """

        self.service_shared_vpc_subnet_users = []
        if self.subnetwork_api:

            for i, _subnetwork_api in enumerate(self.subnetwork_api):
                _service_shared_vpc_subnet_user = gcp.compute.SubnetworkIAMMember(
                    f"service_shared_vpc_subnet_user-{i}",
                    role="roles/compute.networkUser",
                    project=host_project_id,
                    region=self.get_partition(_subnetwork_api, "regions"),
                    subnetwork=self.get_partition(_subnetwork_api, "subnetworks"),
                    member=f"serviceAccount:{self.apis[_subnetwork_api[0]]}",
                    opts=pulumi.ResourceOptions(parent=self),
                )
                self.service_shared_vpc_subnet_users.append(
                    _service_shared_vpc_subnet_user
                )

        """ # noqa
         if "container.googleapis.com" compute.networkUser role granted to GKE service account for GKE on shared VPC Project if no subnets defined
         if "dataproc.googleapis.com" compute.networkUser role granted to dataproc service account for Dataproc on shared VPC Project if no subnets defined
         if "dataflow.googleapis.com" compute.networkUser role granted to dataflow service account for Dataflow on shared VPC Project if no subnets defined
        """
        self.service_shared_vpc_users = []
        if shared_vpc_subnets and enable_shared_vpc_service_project:

            for i, active_api in enumerate(self.active_apis):
                _service_shared_vpc_user = gcp.projects.IAMMember(
                    f"service_shared_vpc_user-{i}",
                    project=host_project_id,
                    role="roles/compute.networkUser",
                    member=f"serviceAccount:{self.apis[active_api]}",
                    opts=pulumi.ResourceOptions(parent=self),
                )
                self.service_shared_vpc_users.append(_service_shared_vpc_user)

        """ # noqa
          composer.sharedVpcAgent role granted to Composer service account for Composer on shared VPC host project
          See: https://cloud.google.com/composer/docs/how-to/managing/configuring-shared-vpc
        """
        if self.composer_shared_vpc_enabled and enable_shared_vpc_service_project:
            self.composer_host_agent = gcp.projects.IAMMember(
                "composer_host_agent",
                project=host_project_id,
                role="roles/composer.sharedVpcAgent",
                member=f"serviceAccount:{self.apis['composer.googleapis.com']}",
                opts=pulumi.ResourceOptions(parent=self),
            )

        """ # noqa
          container.hostServiceAgentUser role granted to GKE service account for GKE on shared VPC host project
          See: https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-shared-vpc
        """
        if self.gke_shared_vpc_enabled and enable_shared_vpc_service_project:
            self.gke_host_agent = gcp.projects.IAMMember(
                "gke_host_agent",
                project=host_project_id,
                role="roles/container.hostServiceAgentUser",
                member=f"serviceAccount:{self.apis['container.googleapis.com']}",
                opts=pulumi.ResourceOptions(parent=self),
            )
        """ # noqa
          roles/compute.securityAdmin role granted to GKE service account for GKE on shared VPC host project
          See: https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-shared-vpc#enabling_and_granting_roles
          and https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-shared-vpc#creating_additional_firewall_rules
        """
        if (
            self.gke_shared_vpc_enabled
            and enable_shared_vpc_service_project
            and grant_services_security_admin_role
        ):
            self.gke_security_admin = gcp.projects.IAMMember(
                "gke_security_admin",
                project=host_project_id,
                role="roles/compute.securityAdmin",
                member=f"serviceAccount:{self.apis['container.googleapis.com']}",
                opts=pulumi.ResourceOptions(parent=self),
            )

    @staticmethod
    def get_service_project_number(service_project_id: pulumi.Input[str]):
        return gcp.projects.get_project(filter=f"project_id:{service_project_id}")

    @staticmethod
    def get_partition(shared_vpc_subnet: str, partition_word="regions") -> str:
        _, _, after = shared_vpc_subnet.partition(partition_word)
        after = after.strip().split("/")[1]
        return after

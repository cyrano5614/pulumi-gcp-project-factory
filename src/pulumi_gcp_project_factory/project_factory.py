# pyright: reportUnboundVariable=false
try:
    from typing import List, Mapping, Optional, Sequence, TypedDict
except ImportError:
    from typing import List, Optional
    from typing_extensions import TypedDict

import pulumi
import pulumi_gcp as gcp  # noqa

from .core_project_factory import CoreProjectFactory
from .project_services import ProjectServices


class APIIdentity(TypedDict):
    api: str
    roles: List[str]


class ConsumerQuotas(TypedDict):
    service: str
    metric: str
    limit: str
    value: str


class ProjectFactory(pulumi.ComponentResource):
    """ProjectFactory."""

    def __init__(
        self,
        resource_name: str,
        name: pulumi.Input[str],
        org_id: pulumi.Input[str],
        billing_account: pulumi.Input[str],
        random_project_id: pulumi.Input[bool] = False,
        project_id: Optional[pulumi.Input[str]] = None,
        domain: Optional[pulumi.Input[str]] = None,
        svpc_host_project_id: Optional[pulumi.Input[str]] = None,
        enable_shared_vpc_host_project: pulumi.Input[bool] = False,
        folder_id: Optional[pulumi.Input[str]] = None,
        group_name: Optional[pulumi.Input[str]] = None,
        group_role: pulumi.Input[str] = "roles/editor",
        create_project_sa: pulumi.Input[bool] = True,
        project_sa_name: pulumi.Input[str] = "project-service-account",
        sa_role: Optional[pulumi.Input[str]] = None,
        activate_apis: pulumi.Input[Sequence[pulumi.Input[str]]] = [
            "compute.googleapis.com"
        ],
        activate_api_identities: pulumi.Input[Sequence[pulumi.Input[APIIdentity]]] = [],
        usage_bucket_name: Optional[pulumi.Input[str]] = None,
        usage_bucket_prefix: Optional[pulumi.Input[str]] = None,
        shared_vpc_subnets: pulumi.Input[Sequence[pulumi.Input[str]]] = [],
        labels: pulumi.Input[Mapping[str, pulumi.Input[str]]] = {},
        bucket_project: Optional[pulumi.Input[str]] = None,
        bucket_name: Optional[pulumi.Input[str]] = None,
        bucket_location: pulumi.Input[str] = "US",
        bucket_versioning: pulumi.Input[bool] = False,
        bucket_labels: pulumi.Input[Mapping[str, pulumi.Input[str]]] = {},
        bucket_force_destroy: pulumi.Input[bool] = False,
        bucket_ula: pulumi.Input[bool] = True,
        auto_create_network: pulumi.Input[bool] = False,
        lien: pulumi.Input[bool] = False,
        disable_services_on_destroy: pulumi.Input[bool] = True,
        default_service_account: pulumi.Input[str] = "disable",
        disable_dependent_services: pulumi.Input[bool] = True,
        budget_amount: Optional[pulumi.Input[float]] = None,
        budget_alert_pubsub_topic: Optional[pulumi.Input[str]] = None,
        budget_monitoring_notification_channels: pulumi.Input[
            Sequence[pulumi.Input[str]]
        ] = [],
        budget_alert_spent_percents: pulumi.Input[Sequence[pulumi.Input[float]]] = [
            0.5,
            0.7,
            1.0,
        ],
        vpc_service_control_attach_enabled: pulumi.Input[bool] = False,
        vpc_service_control_perimeter_name: Optional[pulumi.Input[str]] = None,
        grant_services_security_admin_role: pulumi.Input[bool] = False,
        consumer_quotas: pulumi.Input[Sequence[pulumi.Input[ConsumerQuotas]]] = [],
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__(
            t="zityspace-gcp:projectfactory:ProjectFactory",
            name=resource_name,
            props={},
            opts=opts,
        )
        """
        Organization info retrieval
        """

        """
        Core Project Factory
        """
        _core_project_factory = CoreProjectFactory()

        """
        Setting API service accounts for shared VPC
        """
        _shared_vpc_access = SharedVPCAccess()

        """
        Billing budget to create if amount is set
        """
        _budget = Budget()

        """
        Quota to override if metrics are set
        """
        _quotas = QuotaManager()

# pyright: reportUnboundVariable=false
try:
    from typing import List, Optional, Sequence, TypedDict
except ImportError:
    from typing import List, Optional
    from typing_extensions import TypedDict

import pulumi
import pulumi_gcp as gcp


class APIIdentity(TypedDict):
    api: str
    roles: List[str]


class ProjectServices(pulumi.ComponentResource):
    """ProjectServices."""

    def __init__(
        self,
        # Required
        name: str,
        project_id: pulumi.Input[str],
        # Optional
        enable_apis: pulumi.Input[bool] = True,
        activate_apis: pulumi.Input[Sequence[pulumi.Input[str]]] = [],
        activate_api_identities: pulumi.Input[Sequence[pulumi.Input[APIIdentity]]] = [],
        disable_services_on_destroy: pulumi.Input[bool] = True,
        disable_dependent_services: pulumi.Input[bool] = True,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        """__init__.

        :param name: Name of the pulumi resource.
        :type name: str
        :param project_id: The GCP project you want to enable APIs on.
        :type project_id: str
        :param enable_apis: Whether to actually enable the APIs. If false,
            this module is a no-op.
        :type enable_apis: bool
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
        :param disable_services_on_destroy: Whether project services will be disabled
            when the resources are destroyed.
            https://www.terraform.io/docs/providers/google/r/google_project_service.html#disable_on_destroy
        :type disable_services_on_destroy: bool
        :param disable_dependent_services: Whether services that are enabled and which
            depend on this service should also be disabled when this service is
            destroyed.
            https://www.terraform.io/docs/providers/google/r/google_project_service.html#disable_dependent_services
        :type disable_dependent_services: bool
        :param opts: Options for the resource.
        :type opts: Optional[pulumi.ResourceOptions]
        """
        super().__init__(
            t="projectfactory:gcp:ProjectServices",
            name=name,
            props={"project_id": project_id},
            opts=opts,
        )

        tmp_activate_apis = [api for api in activate_apis]  # deep copy
        tmp_activate_apis.extend(
            [identity["api"] for identity in activate_api_identities]
        )
        services = list(set(tmp_activate_apis)) if enable_apis else []
        service_identities = [
            {"api": identity["api"], "role": role}
            for identity in activate_api_identities
            for role in identity["roles"]
        ]

        """
        Eample:

        activate_apis = [
            "sqladmin.googleapis.com",
            "bigquery-json.googleapis.com",
        ]
        activate_api_identities = [{
            api: "healthcare.googleapis.com"
            roles: [
                "roles/healthcare.serviceAgent",
                "roles/bigquery.jobUser",
            ]
        }]
        """

        """
        apis
        """
        self.project_services = []

        for service in services:
            _project_service = gcp.projects.Service(
                "project_service" + "-" + service,
                disable_dependent_services=disable_dependent_services,
                disable_on_destroy=disable_services_on_destroy,
                project=project_id,
                service=service,
                opts=pulumi.ResourceOptions(parent=self),
            )
            self.project_services.append(_project_service)

        """
        service identities
        """
        self.project_service_identities = {}
        for identity in activate_api_identities:
            _project_service_identity = gcp.projects.ServiceIdentity(
                "project_service_identity" + "-" + identity["api"],
                project=project_id,
                service=identity["api"],
                # opts=pulumi.ResourceOptions(provider=google_beta, parent=self),
                opts=pulumi.ResourceOptions(parent=self),
            )

            self.project_service_identities[identity["api"]] = _project_service_identity

        """
        service identitiy roles
        """
        self.project_service_identity_roles = []
        for service_identity in service_identities:
            _project_service_identity_role = gcp.projects.IAMMember(
                "project_service_identity_role"
                + "-"
                + service_identity["api"]
                + "-"
                + service_identity["role"],
                project=project_id,
                role=service_identity["role"],
                member=f"serviceAccount:{self.project_service_identities[service_identity['api']].email}",  # noqa type: ignore
            )
            self.project_service_identity_roles.append(_project_service_identity_role)

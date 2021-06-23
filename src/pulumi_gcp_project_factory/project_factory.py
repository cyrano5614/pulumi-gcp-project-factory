from typing import Optional

import pulumi
import pulumi_gcp  # noqa

from pulumi_gcp_project_factory import core_project_factory, project_services  # noqa

"""
Organization info retrieval
"""


class ProjectFactory(pulumi.ComponentResource):
    """ProjectFactory."""

    def __init__(
        self,
        name: pulumi.Input[str],
        org_id: pulumi.Input[str],
        random_project_id: pulumi.Input[bool] = False,
        project_id: Optional[pulumi.Input[str]] = None,
        domain: Optional[pulumi.Input[str]] = None,
        svpc_host_project_id: Optional[pulumi.Input[str]] = None,
    ):
        pass

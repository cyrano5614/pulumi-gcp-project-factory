import sys

sys.path.append("../../src")

from pulumi_gcp_project_factory.project_services import ProjectServices  # noqa

project_services = ProjectServices(
    "project_services",
    project_id="demo",
    activate_apis=[
        "sqladmin.googleapis.com",
        "bigquery.googleapis.com",
    ],
    activate_api_identities=[
        {
            "api": "healthcare.googleapis.com",
            "roles": [
                "roles/healthcare.serviceAgent",
                "roles/bigquery.jobUser",
            ],
        }
    ],
)

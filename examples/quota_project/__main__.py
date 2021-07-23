import sys

sys.path.append("../../src")
from pulumi_gcp_project_factory.quota_manager import ConsumerQuota, QuotaManager  # noqa

project_services = QuotaManager(
    "quotamanager",
    project_id="demo",
    consumer_quotas=[
        ConsumerQuota(  # type: ignore
            service="compute.googleapis.com",
            metric="SimulateMaintenanceEventGroup",
            limit="%2F100s%2Fproject",
            value="19",
        ),
        ConsumerQuota(  # type: ignore
            service="servicemanagement.googleapis.com",
            metric="servicemanagement.googleapis.com%2Fdefault_requests",
            limit="%2Fmin%2Fproject",
            value="95",
        ),
    ],
)

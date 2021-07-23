import sys

sys.path.append("../../src")

from pulumi_gcp_project_factory.budget import Budget  # noqa

project_budget = Budget(
    "budget",
    billing_account="demo",
    # projects=["demo"],  #  can't define project for what doesn't exist
    amount=100,
)

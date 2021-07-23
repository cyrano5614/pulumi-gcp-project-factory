import dataclasses
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

import pulumi
import pulumi_gcp as gcp
from pydantic import validate_arguments

if TYPE_CHECKING:  # pragma: no cover
    static_check_init_args = dataclasses.dataclass
else:

    def static_check_init_args(cls):
        return cls


@static_check_init_args
class BudgetCreditTypesEnum(str, Enum):
    INCLUDE_ALL_CREDITS = "INCLUDE_ALL_CREDITS"
    EXCLUDE_ALL_CREDITS = "EXCLUDE_ALL_CREDITS"
    INCLUDE_SPECIFIED_CREDITS = "INCLUDE_SPECIFIED_CREDITS"


class Budget(pulumi.ComponentResource):
    @validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __init__(
        self,
        resource_name: str,
        billing_account: str,
        amount: float,
        projects: List[str] = [],
        create_budget: bool = True,
        display_name: Optional[str] = None,
        credit_types_treatment: BudgetCreditTypesEnum = (
            BudgetCreditTypesEnum.INCLUDE_ALL_CREDITS
        ),
        services: List[str] = [],
        alert_spent_percents: List[float] = [
            0.5,
            0.7,
            1.0,
        ],
        alert_pubsub_topic: Optional[str] = None,
        monitoring_notification_channels: List[str] = [],
        opts: Optional[pulumi.ResourceOptions] = None,
    ):

        super().__init__(
            t="zityspace-gcp:projectfactory:Budget",
            name=resource_name,
            props={},
            opts=opts,
        )
        """
        local
        """
        self.billing_account = billing_account
        self.credit_types_treatment = credit_types_treatment
        self.amount = str(amount)
        self.alert_spent_percents = alert_spent_percents
        self.alert_pubsub_topic = alert_pubsub_topic
        self.monitoring_notification_channels = monitoring_notification_channels
        self.project_name = "All Projects" if not projects else projects[0]
        self.display_name = (
            display_name if display_name is None else f"Budget For {self.project_name}"
        )
        self.all_updates_rule = (
            []
            if alert_pubsub_topic is None and not monitoring_notification_channels
            else ["1"]
        )
        self.projects = None if not projects else self.get_projects(projects)
        self.services = None if services is None else self.get_services(services)

        """
        budget
        """

        self.budget = None
        if create_budget:
            self.budget = self._create_budget()

    @staticmethod
    def get_projects(projects: List[str] = []) -> List[str]:

        retrieved_projects = []

        for project in projects:
            _project = gcp.organizations.get_project(project_id=project)  # type: ignore
            assert _project, f"Project {project} does not exist!"

            project_number = _project.number
            retrieved_projects.append(f"projects/{project_number}")
        return retrieved_projects

    @staticmethod
    def get_services(services: List[str] = []) -> List[str]:
        return [f"services/{service}" for service in services]

    def _create_budget(self) -> gcp.billing.Budget:

        return gcp.billing.Budget(
            "budget",
            billing_account=self.billing_account,
            display_name=self.display_name,
            budget_filter=gcp.billing.BudgetBudgetFilterArgs(
                projects=self.projects,
                credit_types_treatment=self.credit_types_treatment,
                services=self.services,
            ),
            amount=gcp.billing.BudgetAmountArgs(
                specified_amount=gcp.billing.BudgetAmountSpecifiedAmountArgs(
                    units=self.amount,
                ),
            ),
            threshold_rules=[
                gcp.billing.BudgetThresholdRuleArgs(threshold_percent=percent)
                for percent in self.alert_spent_percents
            ],
            all_updates_rule=gcp.billing.BudgetAllUpdatesRuleArgs(
                monitoring_notification_channels=self.monitoring_notification_channels,
                pubsub_topic=self.alert_pubsub_topic,
            )
            if self.all_updates_rule
            else None,
            opts=pulumi.ResourceOptions(parent=self),
        )

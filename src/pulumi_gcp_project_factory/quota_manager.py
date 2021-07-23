import dataclasses
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

import pulumi
import pulumi_gcp as gcp
from pydantic import BaseModel, validate_arguments

if TYPE_CHECKING:  # pragma: no cover
    static_check_init_args = dataclasses.dataclass
else:

    def static_check_init_args(cls):
        return cls


@static_check_init_args
class ConsumerQuota(BaseModel):
    service: pulumi.Input[str]
    metric: pulumi.Input[str]
    limit: pulumi.Input[str]
    value: pulumi.Input[str]


class QuotaManager(pulumi.ComponentResource):
    @validate_arguments
    def __init__(
        self,
        resource_name: str,
        project_id: str,
        consumer_quotas: List[ConsumerQuota] = [],
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__(
            t="zityspace-gcp:projectfactory:QuotaManager",
            name=resource_name,
            props={},
            opts=opts,
        )

        self.consumer_quotas = []
        for consumer_quota in consumer_quotas:  # type: ignore
            _consumer_quota = gcp.serviceusage.ConsumerQuotaOverride(
                f"{consumer_quota.service}-override",
                project=project_id,
                service=consumer_quota.service,
                metric=consumer_quota.metric,
                limit=consumer_quota.limit,
                override_value=consumer_quota.value,
                force=True,
                opts=pulumi.ResourceOptions(parent=self),
            )
            self.consumer_quotas.append(_consumer_quota)

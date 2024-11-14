from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from com.sun.star.frame import XFrame


class AsyncJobInfo:
    """Store job related info when executeAsync() is called"""

    def __init__(
        self,
        env_type: str = "",
        event_name: str = "",
        alias: str = "",
        frame: str = "",
        generic_config_list: str = "",
        job_config_list: str = "",
        environment_list: str = "",
        dynamic_data_list: str = "",
    ):
        self.env_type = env_type
        self.event_name = event_name
        self.alias = alias
        self.frame = frame
        self.generic_config_list = generic_config_list
        self.job_config_list = job_config_list
        self.env_list = environment_list
        self.dynamic_data_list = dynamic_data_list

    def __eq__(self, other: object):
        if not isinstance(other, AsyncJobInfo):
            return NotImplemented
        return (
            self.env_type == other.env_type
            and self.event_name == other.event_name
            and self.alias == other.alias
            and self.frame == other.frame
            and self.generic_config_list == other.generic_config_list
            and self.job_config_list == other.job_config_list
            and self.env_list == other.env_list
            and self.dynamic_data_list == other.dynamic_data_list
        )

    def __hash__(self):
        return hash(
            (
                self.env_type,
                self.event_name,
                self.alias,
                self.frame,
                self.generic_config_list,
                self.job_config_list,
                self.env_list,
                self.dynamic_data_list,
            )
        )

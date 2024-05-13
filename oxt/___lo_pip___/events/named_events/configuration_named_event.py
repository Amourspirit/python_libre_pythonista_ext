"""
Configuration Named Events.
"""
from __future__ import annotations
from typing import NamedTuple


class ConfigurationNamedEvent(NamedTuple):
    """
    Named events for utils.lo.LO class
    """

    CONFIGURATION_SAVING = "configuration_saving"
    """Event triggered before ``Configuration.save_configuration()`` is saved."""
    CONFIGURATION_SAVED = "configuration_saved"
    """Event triggered after ``Configuration.save_configuration()`` is saved."""
    CONFIGURATION_STR_LST_SAVING = "configuration_str_lst_saving"
    """Event triggered before ``Configuration.save_configuration_str_lst()`` is saved."""
    CONFIGURATION_STR_LST_SAVED = "configuration_str_lst_saved"
    """Event triggered after ``Configuration.save_configuration_str_lst()`` is saved."""
    GET_CONFIGURATION = "get_configuration"
    """Event triggered when getting configuration."""

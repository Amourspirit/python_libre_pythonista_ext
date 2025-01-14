import os
from .oxt_logger import OxtLogger
from .config import Config


class Initializer:
    def __init__(self) -> None:
        self._log = OxtLogger(log_name=self.__class__.__name__)
        self._config = Config()

    def check_and_create_remove_script(self) -> None:
        """
        Check if the remove script exists and create it if it does not.
        """
        if self.config.is_win:
            from .install.pkg_installers.batch.batch_writer_ps1 import BatchWriterPs1

            writer = BatchWriterPs1()
            if writer.script_file.exists():
                self.log.debug("Remove script '%s' already exists.", writer.script_file)
            else:
                writer.write_file()
                self.log.info("Remove script '%s' created successfully.", writer.script_file)
        else:
            from .install.pkg_installers.batch.batch_writer_bash import BatchWriterBash

            writer = BatchWriterBash()
            if writer.script_file.exists():
                self.log.debug("Remove script '%s' already exists.", writer.script_file)
            else:
                writer.write_file()
                self.log.info("Remove script '%s' created successfully.", writer.script_file)

    def run_checks(self) -> None:
        # Add your checks here
        self.check_and_create_remove_script()
        # Add more checks as needed

    # region Properties
    @property
    def log(self) -> OxtLogger:
        return self._log

    @property
    def config(self) -> Config:
        return self._config

    # endregion Properties

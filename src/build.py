from __future__ import annotations
import os
import shutil
from .config import Config
from . import file_util
from .build_args import BuildArgs
from .processing.token import Token
from .processing.packages import Packages
from .processing.req_packages import ReqPackages
from .processing.update import Update
from .processing.json_config import JsonConfig
from .processing.default_resource import DefaultResource
from .processing.locale.descriptions import Descriptions
from .processing.locale.publisher import Publisher
from .processing.locale.publisher_update import PublisherUpdate
from .processing.locale.name import Name
from .install.pre_install_pure import PreInstallPure


class Build:
    """Builds the project."""

    def __init__(self, args: BuildArgs) -> None:
        self._config = Config()
        self._build_path = self._config.build_path
        self._args = args
        self._src_path = self._config.root_path / args.oxt_src
        if not self._src_path.exists():
            raise FileNotFoundError(f"Oxt source directory '{self._src_path}' not found")
        self._dist_path = self._config.root_path / self._config.dist_dir_name
        self._dist_path.mkdir(parents=True, exist_ok=True)

    def build(self) -> None:
        """Builds the project."""
        # sourcery skip: extract-method
        if self._args.clean:
            self.clean()
        # self._ensure_build()
        self._copy_src_dest()
        self._rename_lo_pip()
        if self._args.process_tokens:
            self._process_tokens()

        self._process_config()

        self._copy_py_req_packages()
        self._copy_py_req_files()
        self._clear_req_cache()
        self._zip_req_python_path()

        if self._args.process_py_packages:
            pythonpath = self._build_path / self._config.py_pkg_dir
            if pythonpath.exists():
                shutil.rmtree(pythonpath)

            self._copy_py_packages()
            self._copy_py_files()
            self._clear_cache()
            self._zip_python_path()

        if self._args.pre_install_pure_packages:
            self._pre_install_pure_packages()

        self._write_xml()
        self._ensure_default_resource()

        if self._args.make_dist:
            self._zip_build()
            self._process_update()

    def process_tokens(self, text: str) -> str:
        """Processes the tokens in the given text."""
        token = Token()
        return token.process(text)

    def _write_xml(self) -> None:
        """Writes the descriptions."""
        descriptions = Descriptions()
        descriptions.write()

        name = Name()
        name.write()

        publisher = Publisher()
        publisher.write()

    def clean(self) -> None:
        """Cleans the project."""
        if self._build_path.exists():
            shutil.rmtree(self._build_path)

    def _rename_lo_pip(self) -> None:
        """Renames the lo_pip folder."""
        token = Token()
        src_dir = self._build_path / "___lo_pip___"
        if not src_dir.exists():
            raise FileNotFoundError(f"lo_pip folder '{src_dir}' not found")
        dest_dir = self._build_path / token.get_token_value("lo_pip")
        os.rename(src_dir, dest_dir)

    def _ensure_build(self) -> None:
        """Ensures the build directory exists."""
        if not self._build_path.exists():
            self._build_path.mkdir(parents=True, exist_ok=True)

    def _ensure_default_resource(self) -> None:
        """Ensures the default resource file exists."""
        default_resource = DefaultResource()
        default_resource.ensure_default()

    def _copy_src_dest(self) -> None:
        """Copies the source files to the build directory."""
        shutil.copytree(src=self._src_path, dst=self._build_path)

    def _process_tokens(self) -> None:
        """Processes the tokens in the dest files."""
        files = file_util.find_files_matching_patterns(self._build_path, self._config.token_file_ext)
        for file in files:
            text = file_util.read_file(file)
            text = self.process_tokens(text)
            file_util.write_string_to_file(file, text)
        # process py_runner.py
        file = self._build_path / "py_runner.py"
        if file.exists():
            py_file = str(file)
            text = file_util.read_file(py_file)
            text = self.process_tokens(text)
            file_util.write_string_to_file(py_file, text)

    def _process_config(self) -> None:
        token = Token()
        config_file = self._build_path / token.get_token_value("lo_pip") / "config.json"
        json_config = JsonConfig()
        json_config.update_json_config(config_file)

    def _copy_py_packages(self) -> None:
        """Copies the python packages to the build directory."""
        packages = Packages()
        packages.copy_packages(self._build_path / self._config.py_pkg_dir)

    def _copy_py_files(self) -> None:
        """Copies the python files to the build directory."""
        packages = Packages()
        packages.copy_files(self._build_path / self._config.py_pkg_dir)

    def _copy_py_req_packages(self) -> None:
        """Copies the python packages to the build directory."""
        packages = ReqPackages()
        packages.copy_packages(self._build_path / f"req_{self._config.py_pkg_dir}")

    def _copy_py_req_files(self) -> None:
        """Copies the python files to the build directory."""
        packages = ReqPackages()
        packages.copy_files(self._build_path / f"req_{self._config.py_pkg_dir}")

    def _clear_cache(self) -> None:
        """Cleans the cache."""
        packages = Packages()
        if not packages.has_modules():
            return
        packages.clear_cache(self._build_path / self._config.py_pkg_dir)

    def _clear_req_cache(self) -> None:
        """Cleans the cache."""
        packages = ReqPackages()
        packages.clear_cache(self._build_path / f"req_{self._config.py_pkg_dir}")

    def _zip_python_path(self) -> None:
        """Zips the python path."""
        pth = self._build_path / self._config.py_pkg_dir
        if not pth.exists():
            return
        file_util.zip_folder(folder=pth)
        shutil.rmtree(pth)

    def _pre_install_pure_packages(self) -> None:
        """Installs the pure python packages."""
        pre_install = PreInstallPure()
        pre_install.install()

    def _zip_req_python_path(self) -> None:
        """Zips the required packages path."""
        pth = self._build_path / f"req_{self._config.py_pkg_dir}"
        if not pth.exists():
            return
        file_util.zip_folder(folder=pth)
        shutil.rmtree(pth)

    def _zip_build(self) -> None:
        """Zips the build directory."""

        old_file = self._dist_path / f"{self._config.build_dir_name}.zip"
        new_file = self._dist_path / f"{self._config.otx_name}.oxt"
        if new_file.exists():
            os.remove(new_file)

        file_util.zip_folder(folder=self._build_path, dest_dir=self._dist_path)

        os.rename(old_file, new_file)

    def _process_update(self) -> None:
        """Processes the update file."""
        update = Update()
        update.process()

        publisher_update = PublisherUpdate()
        publisher_update.write()

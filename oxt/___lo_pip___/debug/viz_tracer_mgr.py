from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Union
from pathlib import Path

if TYPE_CHECKING:

    class VizTracer:
        def start(self) -> None: ...
        def stop(self) -> None: ...
        def save(
            self, output_file: Optional[str] = None, file_info: Optional[bool] = None, verbose: Optional[int] = None
        ) -> None: ...

    # VizTracer = Type[Any]
    # from viztracer import VizTracer
else:
    try:
        from viztracer import VizTracer
    except (ModuleNotFoundError, ImportError):
        print("VizTracer not found")
        VizTracer = None


class VizTracerMgr:
    """Breakpoint Manager. Singleton Class."""

    _instance = None

    def __new__(cls, *args, **kwargs):  # noqa: ANN002, ANN003, ANN204
        if not cls._instance:
            cls._instance = super(VizTracerMgr, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_is_init"):
            return
        self._is_started = False
        self._is_stopped = False
        if VizTracer is None:
            self._tracer = None
        else:
            self._tracer = VizTracer()
        self._is_init = True

    def start(self) -> None:
        """Starts the tracer if it is not already started."""
        if self._tracer is None:
            return
        if self._is_started:
            return
        self._tracer.start()
        self._is_started = True
        self._is_stopped = False

    def stop(self, out_file: Union[str, Path] = "") -> None:
        """
        Stops the tracer if it is running and saves the trace data to the specified output file.

        Args:
            out_file (str | Path, optional): The file path where the trace data should be saved.
                If not provided, the trace data will not be saved.
        Returns:
            None
        """

        if self._tracer is None:
            return
        if self._is_started:
            self._tracer.stop()
            self._is_stopped = True
        self._is_started = False
        if out_file:
            if isinstance(out_file, Path):
                out_file = str(out_file)
            self._tracer.save(output_file=out_file)

    @property
    def is_started(self) -> bool:
        """Gets if the tracer is started."""
        return self._is_started

    @property
    def is_stopped(self) -> bool:
        """Gets if the tracer is stopped."""
        return self._is_stopped

    @property
    def tracer(self) -> VizTracer:
        """Gets the tracer object."""
        if self._tracer is None:
            raise ValueError("VizTracer not found")
        return self._tracer

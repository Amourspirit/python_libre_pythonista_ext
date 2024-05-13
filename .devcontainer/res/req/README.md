# Requirements

If you have any pip requirements that need to be installed in the container then create a file called `requirements.txt` (if it does not exist) in this directory and add our requirements in a standard manor.
The requirements will be installed globally when the container is built via `pip install -r requirements.txt`.

Generally speaking this is not necessary as any dependencies set in the `pyproject.toml` file will be installed automatically by Poetry. The current entries in the `requirements.txt` file are only there build tools that may be used with your project but are not required for the project to run.

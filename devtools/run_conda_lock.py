#!/usr/bin/env python3

#  Copyright (c) 2022 Mira Geoscience Ltd.
#
#  This file is part of geoapps.
#
#  geoapps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

import os
import subprocess
from contextlib import contextmanager
from pathlib import Path

env_file_variables_section_ = """
variables:
  KMP_WARNINGS: 0
"""


@contextmanager
def print_execution_time(name: str = ""):
    from datetime import datetime

    start = datetime.now()
    try:
        yield
    finally:
        duration = datetime.now() - start
        message_prefix = f" {name} -" if name else ""
        print(f"--{message_prefix} execution time: {duration}")


def create_multi_platform_lock(py_ver: str, platform: str = None):
    print(f"# Create multi-platform lock file for Python {py_ver}")
    platform_option = f"-p {platform}" if platform else ""
    with print_execution_time(f"conda-lock for {py_ver}"):
        subprocess.run(
            f"conda-lock lock --mamba --no-micromamba -f pyproject.toml -f env-python-{py_ver}.yml {platform_option} --lockfile conda-py-{py_ver}-lock.yml",
            env=dict(os.environ, PYTHONUTF8="1"),
            shell=True,
            check=True,
            stderr=subprocess.STDOUT,
        )


def per_platform_env(py_ver: str, full=True, dev=False, suffix=""):
    print(
        f"# Create per platform Conda env files for Python {py_ver} ({'WITH' if dev else 'NO'} dev dependencies) "
    )
    dev_dep_option = "--dev-dependencies" if dev else "--no-dev-dependencies"
    dev_suffix = "-dev" if dev else ""
    extras_option = "--extras full" if full else ""
    subprocess.run(
        (
            f"conda-lock render {dev_dep_option} {extras_option} -k env"
            f" --filename-template conda-py-{py_ver}-{{platform}}{dev_suffix}{suffix}.lock conda-py-{py_ver}-lock.yml"
        ),
        env=dict(os.environ, PYTHONUTF8="1"),
        shell=True,
        check=True,
        stderr=subprocess.STDOUT,
    )
    platform_glob = "*-64"
    for lock_env_file in Path.cwd().glob(
        f"conda-py-{py_ver}-{platform_glob}{dev_suffix}{suffix}.lock.yml"
    ):
        with open(lock_env_file, "a") as f:
            f.write(env_file_variables_section_)


def config_conda():
    subprocess.run(
        "conda config --set channel_priority strict",
        shell=True,
        check=True,
        stderr=subprocess.STDOUT,
    )


if __name__ == "__main__":
    config_conda()
    with print_execution_time(f"run_conda_lock"):
        for py_ver in ["3.9", "3.8", "3.7"]:
            create_multi_platform_lock(py_ver)
            per_platform_env(py_ver, dev=False)
            per_platform_env(py_ver, dev=True)

        # for simpeg with Python 3.9
        per_platform_env("3.9", full=False, dev=False, suffix="-simpeg")

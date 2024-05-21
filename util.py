import os
import shutil
import subprocess
import sys
import tempfile
import uuid

import yaml

from data import Configuration

app_config = None


def read_config(config_file) -> Configuration:
    global app_config
    if app_config is None:
        with open(config_file, 'r') as file:
            app_config = Configuration(**yaml.safe_load(file))
    return app_config


def run_command(command):
    print("Executing Command:", command)
    subprocess.run(command, shell=True, stdout=sys.stdout, stderr=sys.stderr,
                   cwd=os.path.dirname(os.path.realpath(__file__)))


def create_tmp_file(src_path, package_type) -> str:
    tmp_path = os.path.join(tempfile.gettempdir(), "maven-repo-mirror-tmp-" + uuid.uuid4().hex + "."
                            + (package_type if package_type != "pom" else "xml"))
    shutil.copy2(src_path, tmp_path)
    return tmp_path

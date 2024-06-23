import os
import shutil
import subprocess
import tempfile
import uuid
from collections import defaultdict
from string import Template

import yaml

from data import Configuration

app_config = None


def read_config(config_file=None) -> Configuration:
    global app_config
    if app_config is None:
        with open(config_file, 'r') as file:
            app_config = Configuration(**yaml.safe_load(file))
    return app_config


def run_command(command):
    print("Executing Command:", command)
    cmd_proc = subprocess.run(command, shell=True, capture_output=True, check=False, text=True,
               cwd=os.path.dirname(os.path.realpath(__file__)), timeout=120)
    if int(cmd_proc.returncode) != 0:
        print(cmd_proc.stdout)
        print(cmd_proc.stderr)


def create_tmp_file(src_path, package_type) -> str:
    tmp_path = os.path.join(tempfile.gettempdir(), "maven-repo-mirror-tmp-" + uuid.uuid4().hex + "." + package_type)
    shutil.copy2(src_path, tmp_path)
    return tmp_path


def expand_env_var(posix_expr):
    env = defaultdict(lambda: '')
    env.update(os.environ)
    return Template(posix_expr).substitute(env)

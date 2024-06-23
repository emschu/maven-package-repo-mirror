#!/usr/bin/env python
import argparse
import os
import re
import sys
import urllib.request
from os import path
from os.path import expanduser
from typing import List
from xml.dom import minidom

from data import MirrorDefinition
from util import run_command, create_tmp_file, read_config, expand_env_var


def run_mirror(mirror: MirrorDefinition, package: str, artifact_version: str):
    """
    Method to execute a mirror definition of the given configuration

    :param mirror:
    :param package:
    :param artifact_version:
    :return:
    """
    print(f"Fetching artifact version {artifact_version} from repository '{mirror.fromURL}'")

    # download
    download_package(mirror, package, artifact_version)

    # publish
    if mirror.enableRemoteSync and mirror.toURL != "local":
        publish_package(mirror, package, artifact_version)


def download_package(mirror, package, artifact_version):
    """
    Download packages from source remote repository to local and considering classifiers..

    :param mirror:
    :param package:
    :param artifact_version:
    :return:
    """
    # download jar package
    for package_type in ["jar", "pom"]:
        artifact = f"{package}:{artifact_version}:{package_type}"
        maven_get_package(mirror, artifact)

    # download classifiers
    for classifier in mirror.classifier:
        if ":" in classifier:
            package_type = classifier[classifier.index(":") + 1:]
            classifier = classifier[:classifier.index(":")]
        else:
            package_type = "jar"

        artifact = f"{package}:{artifact_version}:{package_type}:{classifier}"
        maven_get_package(mirror, artifact)


def maven_deploy_package(artifact_version: str, mirror: MirrorDefinition,
                         package: str, package_type: str, target_settings_xml: str,
                         tmp_file: str, appendix: str = ""):
    script_dir_path = os.path.dirname(os.path.realpath(__file__))
    target_settings_xml = mirror.toMavenSettings

    if str(target_settings_xml).startswith("./"):
        target_settings_xml = path.join(script_dir_path, target_settings_xml.removeprefix("./"))
    else:
        target_settings_xml = path.realpath(target_settings_xml)

    cmd = (f"mvn org.apache.maven.plugins:maven-deploy-plugin:{read_config().mavenDeployPluginVersion}:deploy-file "
           f"-s \"{target_settings_xml}\" "
           f"-Durl=\"{mirror.toURL}\" "
           f"-Dartifact=\"{package}:{artifact_version}\" "
           f"-Dtransitive={mirror.transitive} "
           f"-Dpackaging={package_type} "
           f"-Dfile=\"{tmp_file}\" "
           f"-DrepositoryId={mirror.toRepositoryId} {appendix}")
    run_command(cmd)


def maven_get_package(mirror, artifact):
    script_dir_path = os.path.dirname(os.path.realpath(__file__))
    source_settings_xml = mirror.fromMavenSettings
    if str(source_settings_xml).startswith("./"):
        source_settings_xml = path.join(script_dir_path, source_settings_xml.removeprefix("./"))
    else:
        source_settings_xml = path.join(source_settings_xml)
    cmd = (f"mvn org.apache.maven.plugins:maven-dependency-plugin:{read_config().mavenDependencyPluginVersion}:get "
           f"-s \"{source_settings_xml}\" "
           f"-DrepoUrl=\"{mirror.fromURL}\" "
           f"-Dartifact=\"{artifact}\" "
           f"-Dtransitive={mirror.transitive} "
           f"-DremoteRepositories={mirror.fromMavenRepositoryId}::default::{mirror.fromURL}")
    run_command(cmd)


def publish_package(mirror, package, artifact_version):
    """
    Method to publish a jar version of an artifact to a remote repository including the configured classifiers.

    :param artifact_version:
    :param mirror:
    :param package:
    :return:
    """
    package_path = package.replace(".", os.path.sep).replace(":", os.path.sep)
    base_artifact_path = path.join(expanduser("~"), ".m2", "repository", package_path, artifact_version)
    artifact_name = package[package.index(":") + 1:]
    local_jar_path = path.join(base_artifact_path, artifact_name + "-" + artifact_version + ".jar")

    for package_type in ["pom", "jar"]:
        tmp_file = create_tmp_file(local_jar_path, "jar")
        try:
            maven_deploy_package(artifact_version, mirror, package, package_type, tmp_file)
        finally:
            os.remove(tmp_file)
    # publish classifiers
    for classifier in mirror.classifier:
        # "jar" is default package type
        if ":" in classifier:
            package_type = classifier[classifier.index(":") + 1:]
            classifier = classifier[:classifier.index(":")]
        else:
            package_type = "jar"

        classifier_artifact_name = package[package.index(":") + 1:].replace(".jar", f"{classifier}.{package_type}")
        local_jar_path = path.join(base_artifact_path,
                                   classifier_artifact_name + "-" + artifact_version + "." + package_type)
        tmp_file = create_tmp_file(local_jar_path, package_type)
        try:
            maven_deploy_package(artifact_version, mirror, package, package_type,
                                 tmp_file, f"-Dclassifier={classifier}")
        finally:
            os.remove(tmp_file)
    print("\n")


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-config", "-c", required=True, help="path to config file")
    args = argument_parser.parse_args()

    config = read_config(args.config)
    # TODO validate config

    for mirror in config.mirrors:
        # merge defaults with config
        default_copy = config.defaults.copy()
        default_copy.update(**mirror)

        if "packages" not in default_copy:
            print("Missing 'packages' in mirror configuration")
            sys.exit(1)

        print("Configuration", mirror, "\n")
        mirror = MirrorDefinition(**default_copy)

        for package in mirror.packages:
            versions_to_fetch = fetch_available_versions(mirror, package)

            print("Fetch ", len(versions_to_fetch), " versions:", versions_to_fetch)

            for artifact_version in versions_to_fetch:
                run_mirror(mirror, package, artifact_version)

    print("Sync OK.")
    sys.exit(0)


def fetch_available_versions(mirror: MirrorDefinition, package) -> List[str]:
    """
    Calls maven-metadata.xml at the remote repository and parses version nodes.
    Optional filtering of found version strings enabled.

    :param mirror:
    :param package:
    :return:
    """

    package_path = package.replace('.', '/').replace(':', '/')
    metadata_file_url = f'{mirror.fromURL}/{package_path}/maven-metadata.xml'
    req = urllib.request.Request(metadata_file_url)
    if len(mirror.customHeader) > 0:
        for i in mirror.customHeader:
            req.add_header(i, expand_env_var(mirror.customHeader[i]))

    # fetch metadata file and read version tags, this could be repository vendor specific
    print("Starting request to maven-metadata.xml: ", metadata_file_url)

    try:
        with urllib.request.urlopen(req, timeout=5) as metadata_file:
            file_content = metadata_file.read().decode('utf-8')
            file = minidom.parseString(file_content)
            version_tags = file.getElementsByTagName('version')

            # conditional version pattern filtering
            if mirror.versionFilterPattern is not None and len(mirror.versionFilterPattern) > 0:
                version_pattern = re.compile(mirror.versionFilterPattern)
                filtered_version_tags = list(
                    filter(lambda tag: version_pattern.match(tag.firstChild.data), version_tags))
            else:
                filtered_version_tags = list(version_tags)

            versions_to_fetch = sorted(filtered_version_tags, key=lambda v: v.firstChild.data)
    except Exception as e:
        print("Error fetching maven-metadata.xml: ", e)
        sys.exit(1)

    versions = []
    for version_node in versions_to_fetch:
        if version_node.nodeType != version_node.ELEMENT_NODE:
            continue
        versions.append(version_node.firstChild.data)

    # consider sync depth
    if mirror.syncDepth > 0:
        return versions[-int(mirror.syncDepth):]
    return versions


if __name__ == "__main__":
    main()

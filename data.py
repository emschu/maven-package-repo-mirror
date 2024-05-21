from typing import List
from dataclasses import dataclass


@dataclass
class DefaultMirrorDefinition(dict):
    fromMavenSettings: str
    fromMavenRepositoryId: str
    toMavenSettings: str
    toRepositoryId: str
    classifier: List[str]
    packages: List[str]
    customHeader: dict[str, str]
    types: str
    enableRemoteSync: bool
    transitive: bool
    versionFilterPattern: str
    syncDepth: int


@dataclass
class MirrorDefinition(DefaultMirrorDefinition):
    fromURL: str
    toURL: str

    def __getitem__(self, item):
        return self.__dict__[item]


class Configuration(dict):
    defaults: DefaultMirrorDefinition
    mirrors: List[MirrorDefinition]
    mavenDependencyPluginVersion: str
    mavenDeployPluginVersion: str

    def __init__(self, **entries):
        super().__init__()
        self.__dict__.update(entries)

    def __getitem__(self, item):
        return self.__dict__[item]

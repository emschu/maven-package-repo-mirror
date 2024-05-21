# maven-repo-mirror

Mirror packages of a remote Maven repository to your local repository
(usually in `~/.m2/`) or to another remote Maven repository.

How it works: 
  - This tool executes native `mvn` commands using `maven-dependency-plugin:get`
and `maven-deploy-plugin:deploy-file` in standalone mode - without using a project's `pom.xml`.
  - Fine-grained configuration options in `config.yml` (+ documentation).
  - Run multiple mirror scenarios at once

Tested with GitLab Maven Repository and AWS CodeArtifact with Python 3.11+.

**Quality:** `Alpha`

## Getting started

### Requirements

- `mvn`
- Install `pyyaml`:

```console
python -m pip install --user pyyaml
```

### Configure mirror settings

Copy and edit `config.yml`.

#### Authentication

- You need to setup authentication to the source repository via a `customHeaders` configuration property, e.g. by
  defining an `Authorization` header.
- You can provide authentication for source and target repository using `settings.xml` files.

Evaluate that connections to remote repositories are working.

### Run

```console
python mirror.py -c your_config_file.yml
```

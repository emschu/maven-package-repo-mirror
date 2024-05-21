# maven-repo-mirror

Mirror packages of a remote Maven repository to your local repository
(usually in `~/.m2/`) or to another remote maven repository.

How it works: This tool executes native `mvn` commands using `maven-deploy-plugin:deploy-file`
and `maven-deploy-plugin:deploy-file`.

Fine-grained configuration options in `config.yml` (+ documentation).

Tested with GitLab Maven Repository and AWS CodeArtifact.

Quality: Alpha

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
  defining a `Authorization` header
- You can provide authentication for source and target repository with `settings.xml` files

### Run

```console
python mirror.py -c your_config.yml
```

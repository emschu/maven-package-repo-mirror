# maven-package-repo-mirror

Python command line script to mirror packages of a remote Maven repository to your local repository
(`~/.m2/`) or to another remote target.

How it works: 
  - This tool executes native `mvn` commands using `maven-dependency-plugin:get`
and `maven-deploy-plugin:deploy-file` in standalone mode - without using a project's `pom.xml`.
  - Fine-grained configuration options in `config.yml` (+ documentation).
  - Run multiple mirror scenarios at once
  - So far tested with GitLab Maven Repository and AWS CodeArtifact with Python 3.11+.


**Quality:** `Alpha`


## Getting started

### Requirements

- `mvn`
- Install `pyyaml`:

```console
python -m pip install --user pyyaml
```

### Configure mirror settings

Copy [`example_config.yml`](./example_config.yml) file and define your own package mirror settings.

#### Authentication

- You can setup authentication to the source repository to fetch `maven-matadata.xml` via a `customHeaders` configuration property, e.g. by
  defining an `Authorization` header. See examples in [`example_config.yml`](./example_config.yml).
- You can use `${env_var}`-syntax in `customHeaders` to use environment variables
- You can provide authentication for source and target repository using `settings.xml` files of Maven.

Evaluate that connections to remote repositories are working.

### Run

```console
python mirror.py -c your_config_file.yml
```

License: GPLv3

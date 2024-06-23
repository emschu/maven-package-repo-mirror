# maven-package-repo-mirror

Python command line script to mirror packages of a remote Maven repository to your local repository
(`~/.m2/`) or to another remote target.

How it works: 
  - This tool executes `mvn` commands using `maven-dependency-plugin:get`
and `maven-deploy-plugin:deploy-file` in standalone mode - without using a project's `pom.xml`.
  - Fine-grained configuration options: See examples in [`example_config.yml`](./example_config.yml).
  - Run multiple mirror scenarios sequentially.
  - Useful in migration, backup or development scenarios.
  - So far tested with GitLab Maven Repository and AWS CodeArtifact with Python 3.11+.

**Quality:** `Alpha`


## Getting started

Get this repository.

### Requirements

- `mvn`
- Install `pyyaml`: `python -m pip install --user pyyaml`


### Configure Maven Mirror Settings

Copy [`example_config.yml`](./example_config.yml) file and define your own package mirror settings.

#### Authentication

- You can setup authentication to the source repository to fetch `maven-matadata.xml` via a `customHeaders` configuration property, e.g. by
  defining an `Authorization` header. See examples in [`example_config.yml`](./example_config.yml).
- You can use `${env_var}`-syntax in `customHeaders` to use environment variables
- You can provide authentication for source and target repository using `settings.xml` files of Maven.

Evaluate that connections to remote repositories are working.

## Run

```console
python mirror.py -c your_config_file.yml
```

### Contributing

License: GPL v3

Contributions are welcome!

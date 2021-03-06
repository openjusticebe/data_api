[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/openjusticebe)
[![Generic badge](https://img.shields.io/badge/Open-Justice-green.svg)](https://shields.io/)
<p align="center">
  <a href="https://openjustice.be">
    <img alt="logo Openjustice.be" src="https://raw.githubusercontent.com/openjusticebe/ui-assets/main/svg/OpenJustice.be_clear.svg" width="120" />
  </a>
</p>
<h1 align="center">
  Openjustice.be
</h1>

[OpenJustice.be](https://openjustice.be) is a non-profit legaltech aiming to open up access to legal knowledge (court decisions, law, doctrine, ...) and instill a true digital-native culture in the world of belgian justice digitalisation.

# Data API
Data API is the internal data exchange API for the OpenJustice platform.

It offers a Rest API, documented via OpenAPI, and some document display abilities.

This API can already :
- Create a new document
- Access and display a document through personal or public links
- Allow for updating and management of documents
- Allow login/logout for administrators, moderators and users
- Provide access to collections of documents

In the future, it should be able to:
- Provide search

## Installation
Clone the repository to your directory of choice:
```bash
> git clone https://github.com/openjusticebe/data_api.git
> cd data_api
```

Once in the root directory, you can run the API with docker (for testing) or using poetry (for development).

```bash
# docker
> docker build -t "api" ./  && docker run --rm -it -p 5000:5000 api

# poetry
> poetry install
```

### Poetry installation
Poetry installs a local, isolated python environment, to avoid conflicts with your system's python modules. See [here](https://python-poetry.org/docs/).

A recent [python](https://www.python.org/downloads/) version (>=3.7) will also be needed.

## Usage
```bash
# Run locally in debug mode
> poetry run api --debug

```

These local URI's provide interaction and documentation for the endpoint

* http://127.0.0.1:5000 for root
* http://127.0.0.1:5000/docs for OpenAPI documentation

For testing the HTML template (which can be run without a database, see below), a specific endpoint is provided:

* http://127.0.0.1:5000/test

#### Database access
A database will be needed to provide full functionality. If run in debug mode (with the `--debug` flag), the API will
launch even if no database can be found.

See the  `ressources/` directory for database schemas (Postgresql >=12).

### Configuration:
See `config_default.toml` file to create a local `config.toml` file for the API to use.

```bash
# Run locally in debug mode with a config file.
> poetry run api --config config.toml --debug
```

## Roadmap
2. Move HTML rendering to API clients (no need for html templates in this api)
3. Add search !


## Contribution
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.fr.html)

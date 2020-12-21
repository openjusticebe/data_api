# Data API
Data API is the internal data exchange API for the OpenJustice platform.

It offers a Rest API, documented via OpenAPI, and some document display abilities.

This API can already :
- Create a new document
- Access and display a document through personal or public links

In the future, it should be able to:
- Provide search
- Allow for updating and management of documents

## Installation
Deployment is through docker or poetry

```bash
# docker
> docker build -t "api" ./  && docker run --rm -it -p 5000:5000 api

# poetry
> poetry install
```

## Usage
```bash
# Run locally in debug mode
> poetry run api --debug

```

These local URI's provide interaction and documentation for the endpoint

* http://127.0.0.1:5000 for root
* http://127.0.0.1:5000/docs for OpenAPI documentation

#### Database access
A database will be needed to provide full functionality. If run in debug mode, the API will
launch even if no database can be found.

See the  `ressources/` directory for database schemas (Postgresql >=12).

### Configuration:
See `config_default.toml` file to create a local `config.toml` file for the API to use.

```bash
# Run locally in debug mode with a config file.
> poetry run api --config config.toml --debug
```

## Roadmap
1. Provide full support for the OpenJustice data interactions
2. Move HTML rendering to API clients (no need for html templates in this api)
3. Add search !


## Contribution
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPLv3](https://www.gnu.org/licenses/gpl-3.0.fr.html)

## OpenJustice data API
Simple api to interact with the OpenJustice data layer

 It offers Rest API, documented via OpenAPI.

### Configuration

### Usage
Deployment is through docker or poetry

```bash
# docker
> docker build -t "api" ./  && docker run --rm -it -p 5000:5000 api

# poetry
> poetry install
> poetry run api
```

Then check these local URI's:

* http://127.0.0.1:5000 for root
* http://127.0.0.1:5000/docs for OpenAPI documentation

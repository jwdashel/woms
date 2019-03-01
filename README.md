# NYPR Whats-On

[![CircleCI](https://circleci.com/gh/nypublicradio/whats-on-microservice.svg?style=shield&circle-token=ab4db778d6d598290695e95c023a2e545c04c03f)](https://circleci.com/gh/nypublicradio/whats-on-microservice)
[![Test Coverage](https://api.codeclimate.com/v1/badges/6f523200a95b5e0245c8/test_coverage)](https://codeclimate.com/repos/5c7989afb5da79604d009bb8/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/6f523200a95b5e0245c8/maintainability)](https://codeclimate.com/repos/5c7989afb5da79604d009bb8/maintainability)

The NYPR "whats-on" service accepts XML from the NexGen/DAVID radio systems
and keeps information about what's currently playing in a key:value store.

## Development

- Requires `Python 3.6+`

### Getting Started

Clone the Repo
```sh
git clone git@github.com:nypublicradio/whats-on-microservice
cd whats-on-microservice
```

Install the Requirements
```sh
python -m venv ~/.virtualenvs/whats-on
. ~/.virtualenvs/whats-on/bin/activate

pip install -e .
python setup.py test_requirements
```

### Running Tests

```sh
pytest
```

## Configuration

:warning: No configuration is required for local development or tests.

### Legend

| **Symbol**     | **Translation** |
| -------------- | --------------- |
| :white_circle: | Not required.   |
| :red_circle:   | Required.       |

### Values

| **Required**   | **Config Value** | **Description**                                              |
| -------------- | ---------------- | ------------------------------------------------------------ |
| :red_circle:   | `DYNAMODB_TABLE` | The DynamoDB table to store values.                          |
| :white_circle: | `URL_PREFIX`     | API requests must be prefixed with this [Default: /whats-on] |
| :white_circle: | `RELEASE`        | Release to report to Sentry [Default: None]                  |
| :white_circle: | `ENV`            | Environment to report to Sentry [Default: None]              |
| :white_circle: | `SENTRY_DSN`     | URL for reporting uncaught exceptions [Default: None].       |

:warning: The IAM execution role for the Lambda must be able to read/write from the specified DynamoDB.

## Deployment

### Overview
There are two deployment environments, **demo** and **prod**.
Both environments are arranged in the same architecture, which is maintained [here](https://github.com/nypublicradio/terraform/tree/master/whats-on).

1. The project is tested via [CircleCI](https://circleci.com/gh/nypublicradio/whats-on-microservice/).
2. If tests pass, the Lambda zip is built and pushed to AWS.

### Demo

The **demo** environment is for staging work.

Any commit to the `master` branch will trigger a demo deployment.

### Prod

The **prod** environment is for versioned releases.

To release to **prod** create a release via [GitHub](https://github.com/nypublicradio/whats-on-microservice/releases).

The release format is `v<Major>.<Minor>.<Fix>`.

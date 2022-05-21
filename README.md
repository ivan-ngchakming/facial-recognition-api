# Facial Recognition Database Management System

Back-end for <https://github.com/ivan-ngchakming/facial-recognition-web>

Serving on <https://facial-recognition-api.ivan0313.tk/>


## Introduction

Facial Recognition Database Management System (FRDMS) is a facial recognition system made for everyone.

Powered by python and react, and packaged into a single executable that can be used by anyone with zero dependencies required.


## Contributing

### First time setup

Create virtual environment using pipenv

Install pre-commit hooks

```sh
pre-commit install
```

Create a copy of `.env.example`, rename to `.env` and fill in corresponding values

```bash
DB_HOST=
DB_PORT=5432
DB_NAME=facial-recognition
DB_USERNAME=
DB_PASSWORD=
```

Run db migrations

```bash
flask db upgrade
```

### API Documentation

https://documenter.getpostman.com/view/19469395/Uyxoi4MN

### Run Production

```bash
gunicorn -w 4 server:app
```

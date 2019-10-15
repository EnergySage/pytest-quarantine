# How to contribute

## Getting started

[Fork and clone](https://help.github.com/en/articles/fork-a-repo) this repository.

Create and activate a virtual environment:

```
$ cd pytest-quarantine

$ python3 -m venv venv

$ source venv/bin/activate
```

Install this package and its dependencies for development:

```
$ pip install -e .[dev]

$ pre-commit install --install-hooks
```

## Developing

Activate your virtual environment:

```
$ source venv/bin/activate
```

Run all the tests (in all supported Python versions) and code style checks:

```
$ tox
```

Run all the tests with Python 3.7:

```
$ tox -e py37
```

Run all the code style checks:

```
$ tox -e check
```

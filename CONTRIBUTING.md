# How to contribute

## Getting started

[Fork and clone](https://help.github.com/en/articles/fork-a-repo) this repository.

Create and activate a [virtual environment](https://docs.python.org/3/tutorial/venv.html):

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

This will install:

- [pytest](https://docs.pytest.org/en/latest/), [coverage.py](https://coverage.readthedocs.io/en/latest/), and [tox](https://tox.readthedocs.io/en/latest/) to run the tests
- [black](https://black.readthedocs.io/en/stable/) to format the code
- [flake8](http://flake8.pycqa.org/en/latest/) to identify coding errors and check code style
- [pydocstyle](http://www.pydocstyle.org/en/latest/) to check docstring style
- [pre-commit](https://pre-commit.com/) to check code quality on every commit

## Developing

Activate your virtual environment:

```
$ source venv/bin/activate
```

Run the tests:

```
$ pytest
```

Run the code quality checks:

```
$ tox -e check
```

Run the tests in all supported Python versions, and the code quality checks:

```
$ tox
```

**NOTE**: This requires having multiple versions of Python installed on your system (see the [tox configuration](./tox.ini) for the list). [pyenv](https://github.com/pyenv/pyenv) is a good tool for that.

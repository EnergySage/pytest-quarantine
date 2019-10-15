# How to contribute

## Getting started

[Fork and clone](https://help.github.com/en/articles/fork-a-repo) this repository.

Install [tox](https://tox.readthedocs.io/en/latest/) on your system (for example, with [pipx](https://pipxproject.github.io/pipx/)):

```
$ pipx install tox
```

Run all the tests and linters:

```
$ tox
```

Run just the tests with Python 3.7:

```
$ tox -e py37
```

Run just the linters:

```
$ tox -e check
```

Create and activate a virtual environment for regular development:

```
$ tox -e venv

$ source venv/bin/activate
```

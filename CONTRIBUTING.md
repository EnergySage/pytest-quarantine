# How to contribute

Thanks for your interest in improving this project! These guidelines attempt to make the process easier and more enjoyable.

## General guidelines

Everyone interacting with this project is expected to follow the [Code of Conduct](./CODE_OF_CONDUCT.md).

Submit questions, bug reports, and feature requests in the [issue tracker](https://github.com/bhrutledge/pytest-quarantine/issues). Please be as descriptive as you can. For bug reports, please include information about your local environment, the steps to reproduce the bug, and any relevant command-line output.

Submit improvements to code and documentation via [pull requests](https://github.com/bhrutledge/pytest-quarantine/pulls). Unless it’s a small/quick fix, pull requests should reference an open issue that’s been discussed. This helps ensure that your contribution is aligned with the goals of this project.

During development, use the provided tools to check for consistent style, coding errors, and test coverage. These checks and the tests are run automatically on every pull request via [Travis](https://travis-ci.com/bhrutledge/pytest-quarantine), [AppVeyor](https://ci.appveyor.com/project/bhrutledge/pytest-quarantine), and [Codecov](https://codecov.io/gh/bhrutledge/pytest-quarantine). In general, only pull requests with passing tests and checks will be merged.

## Setting up a development environment

- [Fork and clone](https://help.github.com/en/articles/fork-a-repo) this repository.

- Create and activate a [virtual environment](https://docs.python.org/3/tutorial/venv.html):

    ```
    $ cd pytest-quarantine

    $ python3 -m venv venv

    $ source venv/bin/activate
    ```

- Install this package and its dependencies for development:

    ```
    $ pip install -e .[dev]

    $ pre-commit install --install-hooks
    ```

    This will install:

    - [pytest](https://docs.pytest.org/en/latest/) and [coverage.py](https://coverage.readthedocs.io/en/latest/) to run the tests
    - [black](https://black.readthedocs.io/en/stable/) to format the code
    - [flake8](http://flake8.pycqa.org/en/latest/) to identify coding errors and check code style
    - [pydocstyle](http://www.pydocstyle.org/en/latest/) to check docstring style
    - [pre-commit](https://pre-commit.com/) to run the formatters and linters on every commit
    - [tox](https://tox.readthedocs.io/en/latest/) to run common development tasks

## During development

- Activate your virtual environment:

    ```
    $ source venv/bin/activate
    ```

- Run the tests:

    ```
    $ pytest
    ```

- Run the tests and generate a coverage report:

    ```
    $ tox -e py,coverage
    ```

    Please add or update tests to ensure the coverage doesn’t drop.

- Run the formatters and linters:

    ```
    $ tox -e check
    ```

    These checks are also run on every commit via [pre-commit hooks](./.pre-commit-config.yaml). Please fix any failures before committing.

- Run the tests in all supported Python versions, generate a coverage report, and run the checks:

    ```
    $ tox
    ```

    This requires having multiple versions of Python installed on your system (see the [tox configuration](./tox.ini) for the list); [pyenv](https://github.com/pyenv/pyenv) is a good tool for that. However, this is also run for every pull request via continuous integration, so it’s okay to skip it.

## Making a release

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [PEP 440](https://www.python.org/dev/peps/pep-0440/), and uses [setuptools_scm](https://pypi.org/project/setuptools-scm/) to manage versions via `git` tags.

- Checkout and update `master`

    ```
    $ git checkout master
    $ git pull upstream
    ```

- Pick a version number (e.g. `1.0.1`) and create a new branch:

    ```
    $ version=1.0.1 branch=release-$version
    $ git checkout -b $branch
    ```

- Run the release pipeline and fix any failures (except the version):

    ```
    $ tox -e release
    ```

- Update the [changelog](./CHANGELOG.md)

- Push the branch, open a PR, and wait for CI to pass

    ```
    $ git push -u origin HEAD
    ```

- Checkout `master` and merge the branch

    ```
    $ git checkout master
    $ git merge --squash $branch
    $ git commit
    ```

- Tag the release, and verify the signature:

    ```
    $ git tag -s -m "Preparing release $version" $version
    $ git tag -v $version
    ```

- Push `master` and the new tag:

    ```
    $ git push upstream
    $ git push upstream $version
    ```

- Review the release on [GitHub](https://github.com/bhrutledge/pytest-quarantine/releases)

- Run the release pipeline to upload to [TestPyPI](https://test.pypi.org/project/pytest-quarantine/):

    ```
    $ tox -e release
    ```

- If it looks good on TestPyPI, run the release pipeline to upload to [PyPI](https://pypi.org/project/pytest-quarantine/):

    ```
    $ tox -e release pypi
    ```

- 🚀 🎉

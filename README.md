# pytest-quarantine

[![PyPI version](https://img.shields.io/pypi/v/pytest-quarantine.svg)](https://pypi.org/project/pytest-quarantine)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-quarantine.svg)](https://pypi.org/project/pytest-quarantine)
[![Linux build status](https://img.shields.io/travis/com/EnergySage/pytest-quarantine?logo=travis)](https://travis-ci.com/EnergySage/pytest-quarantine)
[![Windows build status](https://img.shields.io/appveyor/ci/EnergySage/pytest-quarantine?logo=appveyor)](https://ci.appveyor.com/project/EnergySage/pytest-quarantine)
[![Test coverage](https://img.shields.io/codecov/c/github/EnergySage/pytest-quarantine?logo=codecov)](https://codecov.io/gh/EnergySage/pytest-quarantine)

A plugin for [pytest](https://github.com/pytest-dev/pytest) to manage expected test failures.

## Features

Save the list of failing tests, so that they can be automatically marked as expected failures on future test runs.

### Why?

You've got a test suite; nicely done! Unfortunately, for completely understandable reasons, a lot of the tests are failing. Someday, you and/or your team will get those tests to pass. For now, though, what you really want is to draw a line in the sand and avoid new test failures. Unfortunately, it's hard to tell when they're introduced because the test suite is already failing. You could get the test suite to pass by applying [`pytest.mark.xfail`](http://doc.pytest.org/en/latest/skipping.html#xfail) to the existing failures, but there are *so many* of them.

With this plugin, you can save all of existing failures to a file (the quarantine). On future test runs, this plugin will automatically apply `pytest.mark.xfail` to the quarantined tests. Then, the test suite will pass, and any new failures will cause it to fail.

## Requirements

- Python 2.7 or 3.5+
- pytest 4.6 or newer

## Installation

Via [pip](https://pypi.org/project/pip/) from [PyPI](https://pypi.org/project/pytest-quarantine) in an active [virtual environment](https://docs.python.org/3/tutorial/venv.html):

```
$ pip install pytest-quarantine
```

## Usage

Run your test suite and save the failing tests to `quarantine.txt`:

```
$ pytest --save-quarantine=quarantine.txt
============================= test session starts ==============================
...
collected 1380 items

...

---------------------- 661 items saved to quarantine.txt -----------------------
============== 629 failed, 719 passed, 32 error in 312.56 seconds ==============
```

Add `quarantine.txt` to your version control system.

Run your test suite with the quarantined tests marked as expected failures:

```
$ pytest --quarantine=quarantine.txt
============================= test session starts ==============================
...
collected 1380 items
added mark.xfail to 661 of 661 items from quarantine.txt

...

================== 719 passed, 661 xfailed in 300.51 seconds ===================
```

When the expected failures eventually pass (i.e., they get counted as `xpassed`), they can be removed manually from `quarantine.txt`, or automatically using `--save-quarantine`. Note that the latter will overwrite the contents of the quarantine, so it's best to only use it when running the entire test suite.

## Getting help

Please submit questions, bug reports, and feature requests in the [issue tracker](https://github.com/EnergySage/pytest-quarantine/issues).

## Contributing

Improvements to the code and documentation are greatly appreciated. See [How to contribute](https://github.com/EnergySage/pytest-quarantine/blob/master/CONTRIBUTING.md) for details.

## Code of conduct

Everyone interacting with this project is expected to follow the [Contributor Covenant](https://github.com/EnergySage/pytest-quarantine/blob/master/CODE_OF_CONDUCT.md).

## License

Distributed under the terms of the [MIT](http://opensource.org/licenses/MIT) license.

## Acknowledgements

This project was initially developed at [EnergySage](https://www.energysage.com/about/who-we-are) to aid our migration to Python 3. We hope other people find it helpful.

The name was inspired by the [quarantine feature](https://confluence.atlassian.com/bamboo/quarantining-failing-tests-289276886.html) of the Bamboo CI/CD service. [Pros and Cons of Quarantined Tests](https://marklapierre.net/pros-cons-quarantined-tests/) is a good introduction to the concept (not related to this project).

The repository was generated with [Cookiecutter](https://github.com/audreyr/cookiecutter) using the [cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin) template. The layout and tooling has been heavily modified since then, but it was very helpful to start.

Some other helpful resources were:

- [Starting an Open Source Project | Open Source Guides](https://opensource.guide/starting-a-project/)
- [Testing & Packaging | Hynek Schlawack](https://hynek.me/articles/testing-packaging/)
- [Maintaining a Python Project When It’s Not Your Job | Hynek Schlawack](https://hynek.me/talks/python-foss/)
- [Python Testing with pytest | Brian Okken | The Pragmatic Bookshelf](https://pragprog.com/book/bopytest/python-testing-with-pytest)
- [Developing better test suites for pytest plugins | Raphael Pierzina](https://raphael.codes/blog/test-suites-for-pytest-plugins/)
- [GitHub search](https://github.com/search) for examples from `org:pytest-dev org:pypa org:pycqa org:pallets org:encode`

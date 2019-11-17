# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Require quarantine path on command line ([#30](https://github.com/EnergySage/pytest-quarantine/issues/30))

### Fixed

- --save-quarantine can overwrite test files ([#29](https://github.com/EnergySage/pytest-quarantine/issues/29))

## [1.2.0] - 2019-11-13

### Changed

- Only save failed tests (not skipped) to quarantine ([#27](https://github.com/EnergySage/pytest-quarantine/pull/27))
- Write empty quarantine when all tests pass ([#28](https://github.com/EnergySage/pytest-quarantine/pull/28))

## [1.1.0] - 2019-11-11

### Added

- Report size of quarantine ([#20](https://github.com/EnergySage/pytest-quarantine/pull/20))
- Use attrs for readability ([#23](https://github.com/EnergySage/pytest-quarantine/pull/23))

### Changed

- Refactor plugin ([#18](https://github.com/EnergySage/pytest-quarantine/pull/18))
- Show UsageError for missing quarantine file ([#19](https://github.com/EnergySage/pytest-quarantine/pull/19))
- Refactor tests ([#21](https://github.com/EnergySage/pytest-quarantine/pull/21))
- Don't show quarantine stats with quiet option ([#22](https://github.com/EnergySage/pytest-quarantine/pull/22))
- Update docs ([#24](https://github.com/EnergySage/pytest-quarantine/pull/24))

## [1.0.0] - 2019-11-03

### Added

- Features, usage, etc. in README ([#15](https://github.com/EnergySage/pytest-quarantine/pull/15))
- Plugin functionality and tests ([#16](https://github.com/EnergySage/pytest-quarantine/pull/16))
- More tests ([#17](https://github.com/EnergySage/pytest-quarantine/pull/17))

## [0.0.3] - 2019-11-02

### Changed

- Use GitHub CLI for release

## [0.0.2] - 2019-11-01

### Changed

- Transfer to EnergySage

## [0.0.1] - 2019-10-22

### Changed

- Tweak contributing guidelines

## [0.0.0] - 2019-10-21

### Added

- Initial project structure, tooling, and contributing guidelines

[Unreleased]: https://github.com/EnergySage/pytest-quarantine/compare/1.2.0...HEAD
[1.2.0]: https://github.com/EnergySage/pytest-quarantine/releases/tag/1.1.0
[1.1.0]: https://github.com/EnergySage/pytest-quarantine/releases/tag/1.1.0
[1.0.0]: https://github.com/EnergySage/pytest-quarantine/releases/tag/1.0.0
[0.0.3]: https://github.com/EnergySage/pytest-quarantine/releases/tag/0.0.3
[0.0.2]: https://github.com/EnergySage/pytest-quarantine/releases/tag/0.0.2
[0.0.1]: https://github.com/EnergySage/pytest-quarantine/releases/tag/0.0.1
[0.0.0]: https://github.com/EnergySage/pytest-quarantine/releases/tag/0.0.0

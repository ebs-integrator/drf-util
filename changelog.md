# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.0.19] - 2019-12-23
### Added
- Triple Search function in ElasticUtil
- Triple Search query generator for Triple search function 

### Changed
- Function gt can now extract from a list with dicts values and added separator option for func parameters
- CommonModel doesn't update date_updated each time changes are made

## [0.0.20] - 2019-12-26
### Changed
- Function gt can now extract from a mongo engine Document
- Elasticsearch and mongoengine are not requirements now

## [0.0.21] - 13-01-2020
### Added
- [Await Process Decorator](https://github.com/iurii-ebs/drf-util/commit/fbe693d3b5aabedc0594a8c2c6f5f346a8091b4d#diff-6ccbb3dab6897856ba86fe421ccd584bR73)
- [Browser Headers](https://github.com/iurii-ebs/drf-util/commit/fbe693d3b5aabedc0594a8c2c6f5f346a8091b4d#diff-ab3a5ae228e9c73ee208114a62856078R3)

## [0.0.22] - 14-01-2020
### Hotfix
- [FAKE_BROWSER_HEADERS bug fixed](https://github.com/iurii-ebs/drf-util/commit/24bf468746b6c320c5f966e5df4a64fca17fdc82)

### [0.0.23] - 27-01-2020
### Hotfix
- [gt function map for all_key fix](https://github.com/elasmd/drf-util/commit/6f877c1560d633863115ef315f3b1aab1d0866bd)
# Change Log

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).
 
 
## [0.0.6] - 2023-01-22

### Fixed
 
- CLI autocomplete now works again after adding support for "single-letter" command-shortcuts.

### Added

- Added a set of missing attributes to the Raindrop API model type, eg. file, cache etc. Only significant attribute missing is `highlights`


## [0.0.5] - 2023-01-21

### Changed

- Moved internal module name to match that of package name. Since we couldn't use raindroppy as a package name on PyPI due to similarities with existing packages (one of which was for a *crypto* package), we renamed this package to raindrop-io-py. In concert, the internal module is now **raindropiopy**:

```python
from raindroiopy.api import API
```

### Added

- Added support and use of [Vulture](https://github.com/jendrikseipp/vulture) for dead-code analysis (not in pre-commit through due to conflict with ruff's McCabe complexity metric)
 
### Fixed

- Fixed sample file upload specification in examples/create_raindrop_file.py.

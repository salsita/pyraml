# [PyRAML](https://github.com/salsita/pyraml) <a href='https://github.com/salsita'><img align='right' title='Salsita' src='https://www.google.com/a/cpanel/salsitasoft.com/images/logo.gif?alpha=1' /></a>

[RAML (REST API Markup Language)](http://raml.org/) enhanced loader, parameter converter, and API wrapper.

[![Latest Version](https://pypip.in/version/PyRAML/badge.svg)]
(https://pypi.python.org/pypi/PyRAML/)
[![Downloads](https://pypip.in/download/PyRAML/badge.svg)]
(https://pypi.python.org/pypi/PyRAML/)
[![Supported Python versions](https://pypip.in/py_versions/PyRAML/badge.svg)]
(https://pypi.python.org/pypi/PyRAML/)
[![License](https://pypip.in/license/PyRAML/badge.svg)]
(https://pypi.python.org/pypi/PyRAML/)


## Supported Platforms

* [Python](http://www.python.org/) >= 2.6, 3.3


## Get Started

Install using [pip](https://pip.pypa.io/) or [easy_install](http://pythonhosted.org/setuptools/easy_install.html):
```bash
pip install PyRAML
easy_install PyRAML
```

Optionally, you can specify `yaml` or `raml` extras to install related dependencies:
```bash
pip install "PyRAML[yaml,raml]"
easy_install "PyRAML[yaml,raml]"
```

## Features

- Load [RAML](http://raml.org/) API specification stored in any of supported markup languages using [PyDataLoader](https://github.com/salsita/pydataloader).
  - Support [YAML](http://yaml.org/) using [PyYAML](http://pyyaml.org/wiki/PyYAML).
  - Support [RAML](http://raml.org/) using [pyraml-parser](https://github.com/an2deg/pyraml-parser).
  - Support [JSON](http://json.org/) using [Python 2.6+ json module](https://docs.python.org/2/library/json.html), or [Python 3.x json module](https://docs.python.org/3/library/json.html).
- Provide extensible API model with access to resources and methods.
- Provide extensible parameter converter and validator.

## Changelog

### 0.1.4

#### Features

- Initial release.

#### Fixes

- PyPI package structure.

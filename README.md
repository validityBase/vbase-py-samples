# vbase-py-samples

vBase Python Samples

-   Python 3.8+ support

---

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Introduction

The vBase platform enables distributed computing using untrusted 3rd party data.
Consumers can perform calculations on externally-managed data and models
with the same confidence and assurances as on internal artifacts.

The following samples illustrate common solutions built on top of the vBase library and services.

## Setup

### Install the vbase-py library

- Clone the `vbase-py` repository `https://github.com/validityBase/vbase-py.git`.
  - `vbase-py` is the Python library for interacting with the ChronoCloud (vBase) environment. 
  It is required by most command-line tools and data science workflows.
  - At the time of this limited release, the repository is private. 
  It can be cloned using GitHub Desktop or another authenticated solution.
  - This guide assumes the repository has been cloned to the local path `~/validityBase/vbase-py`.
- Install the `vbase-py` Python package from the cloned repository:
```commandline
pip install ~/validityBase/vbase-py
```

### Configure vBase access

If you have previously configured vBase access, for instance when using the `vbase-py-tools` package,
you can re-use those settings by copying `.env` file to the `vbase-py-samples` folder.
If this is your first time working with vBase, you should configure new settings.

If this is your first time accessing vBase, please install the `vbase-py-tools` package 
and follow the setup instructions using the `config_env` script provided in that package. 

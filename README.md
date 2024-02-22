# vbase-py-samples

vBase Python Samples

-   Python 3.8+ support

---

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Introduction

The vBase platform enables distributed computing using untrusted 3rd party data.
Consumers can perform calculations on externally managed data and models
with the same confidence and assurances as on internal artifacts.

The following samples illustrate common solutions built on top of the vBase library and services.

## Setup

### Install vbase-py

Install the vBase Python SDK:
```commandline
pip install git+https://github.com/validityBase/vbase-py.git@main
```

### Configure vBase access

Please contact vBase for help configuring your environment and to obtain an API key.
An API key provides simple managed access to commitment services
without the need to worry about blockchains and cryptocurrency.

If you have previously configured vBase access, for instance when using the `vbase-py-tools` package,
you can re-use those settings by copying `.env` file to the `vbase-py-samples` folder.
If this is your first time working with vBase, you should configure new settings.
If this is your first time accessing vBase, please install the `vbase-py-tools` package
and follow the setup instructions using the `config_env` script provided in that package. 

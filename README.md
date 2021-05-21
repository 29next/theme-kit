# 29 Next Theme Kit

Theme Kit is a cross-plaform command line tool to build and maintain storefront themes on the 29 Next platform.

### Installation

Theme Kit is a python package available on [PyPi](https://pypi.org/project/next-theme-kit/)

If you already have `python` and `pip`, install with the following command:

```
pip install next-theme-kit
```

#### Mac OSX Requirements
See how to install `python` and `pip` with [HomeBrew](https://docs.brew.sh/Homebrew-and-Python#python-3x). Once you have completed this setp you can install using the `pip` instructions above.

#### Windows Requirements
See how to install `python` and `pip` with [Chocolatey](https://python-docs.readthedocs.io/en/latest/starting/install3/win.html). Once you have completed this setp you can install using the `pip` instructions above.

#### Updating Theme Kit

Udpate to the latest version of Theme Kit with the following command:
```
pip install next-theme-kit --upgrade
```

### Usage
Available commands:
* ntk pull
* ntk watch


#### Pull theme files to your local machine
Pull a theme from your store into your directory and create a config.yml file"
```
ntk pull -a={{ api_key }} -t={{ theme_id }} -s={{ store_url }}
```

With an existing config.yml in the current directory can simply use:
```
ntk pull
```

#### Watch for files changes and sync

```
ntk watch
```

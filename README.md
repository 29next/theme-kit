<!-- Badges -->
[![PyPI Version][pypi-v-image]][pypi-v-link]
[![Build Status][GHAction-image]][GHAction-link]

# 29 Next Theme Kit

Theme Kit is a cross-platform command line tool to build and maintain storefront themes on the 29 Next platform.

### Installation

Theme Kit is a python package available on [PyPi](https://pypi.org/project/next-theme-kit/)

If you already have `python` and `pip`, install with the following command:

```
pip install next-theme-kit
```

#### Mac OSX Requirements
See how to install `python` and `pip` with [HomeBrew](https://docs.brew.sh/Homebrew-and-Python#python-3x). Once you have completed this step you can install using the `pip` instructions above.

#### Windows Requirements
See how to install `python` and `pip` with [Chocolatey](https://python-docs.readthedocs.io/en/latest/starting/install3/win.html). Once you have completed this step you can install using the `pip` instructions above.

#### Updating Theme Kit

Update to the latest version of Theme Kit with the following command:
```
pip install next-theme-kit --upgrade
```

### Usage
With the package installed, you can now use the commands inside your theme directory and work on a storefront theme.

**Available Commands**
* `ntk init` - initialize a new theme
* `ntk list` - list all available themes
* `ntk checkout` - checkout an existing theme
* `ntk pull` - download existing theme or theme file
* `ntk push` - push current theme state to store
* `ntk watch` - watch for local changes and automatically push changes to store

#### Init
Initialize a new theme which will create the theme on a store and create an initial config.yml file

```
ntk init
```
##### Required flags without config.yml
| Short | Long | Description|
|--- | --- | --- |
| -a | --apikey | API Key used to connect to the store.|
| -s | --store | Full domain of the store. |
| -n | --name | Name of the new theme |


#### List
List all themes installed on the theme.
```
ntk list
```
##### Required flags without config.yml
| Short | Long | Description|
|--- | --- | --- |
| -a | --apikey | API Key used to connect to the store.|
| -s | --store | Full domain of the store. |


#### Checkout
Checkout a theme from your store to pull it into your directory.
```
ntk checkout
```
##### Required flags without config.yml
| Short | Long | Description|
|--- | --- | --- |
| -a | --apikey | API Key used to connect to the store.|
| -s | --store | Full domain of the store. |
| -t | --theme_id | ID of the theme. |

#### Pull
Pull a theme from your store to into your directory.
```
ntk pull
```
##### Required flags without config.yml
| Short | Long | Description|
|--- | --- | --- |
| -a | --apikey | API Key used to connect to the store.|
| -s | --store | Full domain of the store. |
| -t | --theme_id | ID of the theme. |


#### Push
Push all theme files from your local directory to the store.
```
ntk push
```
##### Required flags without config.yml
| Short | Long | Description|
|--- | --- | --- |
| -a | --apikey | API Key used to connect to the store.|
| -s | --store | Full domain of the store. |
| -t | --theme_id | ID of the theme. |


#### Watch
Watch for file changes and additions in your local directory and automatically push them to the store.
```
ntk watch
```
##### Required flags without config.yml
| Short | Long | Description|
|--- | --- | --- |
| -a | --apikey | API Key used to connect to the store.|
| -s | --store | Full domain of the store. |
| -t | --theme_id | ID of the theme. |


<!-- Badges -->
[pypi-v-image]: https://img.shields.io/pypi/v/next-theme-kit.svg
[pypi-v-link]: https://pypi.org/project/next-theme-kit/
[GHAction-image]: https://github.com/29next/theme-kit/actions/workflows/test.yml/badge.svg?branch=master
[GHAction-link]: https://github.com/29next/theme-kit/actions?query=event%3Apush+branch%3Amaster

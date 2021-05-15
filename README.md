# Next theme kit

Theme Kit is a cross-platform command line tool that you can use to build themes. To get up and running quickly with Theme Kit.

## How to setup

- Run on Python3 - [How to install Python 3.7 on Ubuntu](https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/)
- Install virtualenv & python packages
```
sudo apt-get install python3-pip
sudo pip3 install virtualenv 

virtualenv -p python3 venv

# activate
source venv/bin/activate

# install python packages
pip install -e .
```

## How to make python entry points

```python
python setup.py develop --user
```

## How to run commands

- #### pull command

```python
# In first time, need to specific api_key, theme_id and store_url, then script will generate config.yml
ntk pull -a={{ api_key }} -t={{ theme_id }} -s={{ store_url }}

# After that can use command without params like this
ntk pull
```

- #### watch command
```python
ntk watch
```

## How to run tests

```python
python setup.py test
```

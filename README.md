# Prime theme kit

Theme Kit is a cross-platform command line tool that you can use to build Prime themes. To get up and running quickly with Theme Kit.

## How to setup

- Run on Python3 - [How to install Python 3.7 on Ubuntu](https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/)
- Install virtualenv & python packages
```
sudo apt-get install python3-pip
sudo pip3 install virtualenv 
virtualenv venv
virtualenv -p python3 venv

# activate
source venv/bin/activate

# install python packages
pip install -r requirements.txt
```

## How to make python entry points

```python
python setup.py develop --user
```

## How to run commands

- #### pull command

```python
# In first time
./ntk.py pull -a={{ api key }} -t={{ theme id }} -s={{ store url }}

ntk pull -a={{ api key }} -t={{ theme id }} -s={{ store url }}

# pull templates with the old theme id
./ntk.py pull

ntk pull
```

- #### watch command
```python
./ntk.py watch

ntk watch
```

## How to run tests

```python
python -m unittest -v -b
```

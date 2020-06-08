# Django-Forum
Basic forum web application made with Django

## Development set-up
```
git clone https://github.com/johnhh2/django-forum.git
```

### Virtual environment

#### Install:
```
cd django-forum
virtualenv -p python3.6 venv/
```
#### Activate:
```
source venv/bin/activate
```

### Dependencies

#### Back-end dependencies
Once in the virtual environment, download the poetry package manager
```
pip install poetry
```
If this fails, run
```
sudo pip install --upgrade setuptools pip
sudo apt-get install python2.7-dev libffi-dev libssl-dev
pip install poetry
```
Next, use poetry to download the project dependencies
```
poetry install
```

#### Front-end dependencies
```
npm install
```
### Set up database
```
python manage.py makemigrations
python manage.py migrate
```

### Run the test server
```
python manage.py runserver 127.0.0.1:8000
```

### Access the test server
Use a browser to go to [127.0.0.1:8000](http://127.0.0.1:8000)

## Easy shell access
A simple python program written to help run forum-related commands in a manage.py shell
```
$ python manage.py shell
>>> from imports import *
```

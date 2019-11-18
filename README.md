# A Social Blogging Application (API)

Flask is very flexible, it has no certain pattern of a project folder structure.

Our folder structure is app based structure, which means things are grouped by application.

Each folder is an application. This pattern is used by default in Django. It doesn't mean this pattern is better, you need to choose a folder structure depending on your project. And sometime, you will have to use a mixed pattern.

# Requirements
python 3.5 or higher;

# Installation

## Create an environment
Create a project folder and a venv folder within:

``` bash
$ python3 -m venv venv
```

# Install dependencies
Now, you will need to set up virtual environment that will keep the application and its dependencies isolated from the main system.

Next run the following command with the name of your temporary virtual environment.

``` bash
$ source venv/bin/activate
```

Now, run following command to install Flask dependency inside it:

``` bash
$ pip install -r requirements/dev.txt
```

# Usage

Run this command to run the built-in web server and access the application in your browser at http://localhost:8000:

```shell
$ python3 manage.py runserver
```

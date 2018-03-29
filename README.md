# Neighborhood Grub System

The Neighborhood Grub System is a social kitchen platform for connecting people
who love to cook and people who love to eat in a community.

# Requirements

These instructions have been verified to work on 64-bit Ubuntu 16.04. The
requirements are:

1. Python 3.4 or greater (3.5.2 preferred).
2. The Python package manager pip.
3. The virtual environment builder virtualenv.

# Installation Instructions

Clone the repository
```
git clone https://github.com/mdrahman1472/Neighborhood-Grub-System.git
```
Change directory to the local git repository
```
cd ngs
```
Set up a virtual environment
```
virtualenv env
```
Activate the virtual environment
```
source env/bin/activate
```
Install the Python dependencies
```
pip install -r requirements.txt
```
Change directory to the Django project directory
```
cd django-project
```
Add the `config.py` file with the API key.

Make the SQL migrations.
```
python manage.py makemigrations accounts dishes
```
Apply the migrations.
```
python manage.py migrate
```
Populate the database with mock data
```
python scripts/manage_dummy_data.py load
```
Run the dev server
```
python manage.py runserver 127.0.0.1:8000
```
The NGS web application will be running and accessible at 127.0.0.1:8000

# Dummy Data

Dummy data for the project is contained in the file
`ngs/scripts/manage_dummy_data.py`. The information for each dummy user is
contained in this script, including their passwords.

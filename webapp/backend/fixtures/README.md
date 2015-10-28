# Django Fixtures

This directory contains sample data to populate the database for development purposes.

To use them, you need to do the following things:
* Be sure you have initialized the database
* Be sure you have run all the necessary migrations
* Populate the database with objects with the following order:
    * `python manage.py loaddata users.yaml`
    * `python manage.py loaddata tokens.yaml`
    * `python manage.py loaddata lambda_instances.yaml`
    * `python manage.py loaddata servers.yaml`
    * `python manage.py loaddata applications.yaml`

# Central ~okeanos Lambda on Demand(LoD) Service Application

## Description
In the current directory you can find the Django backend(`app` and `backend` directories) and the Ember frontend(`frontend` directory) of the centralized ~okeanos LoD Service.

## Backend
The backend is a Django application that uses Celery as a Task Queue. The different tasks can all be found inside `backend/events.py` file. This application provides an API for both the clients that post statistical information and the clients that read these information.

## Frontend
The frontend is an Ember.js application. It uses the API provided by the backend to display the proper statistical data.

#!/bin/bash

source ./venv/bin/activate
export FLASK_APP=flaskr
export FLASK_ENV=developmen
export FLASK_DEBUG=1
flask run --host=0.0.0.0 --port=8080

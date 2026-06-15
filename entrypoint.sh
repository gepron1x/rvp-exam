#!/bin/bash

flask db upgrade
python init_db.py

exec gunicorn --bind 0.0.0.0:5000 run:app
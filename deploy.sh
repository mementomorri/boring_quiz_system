#! /usr/bin/bash
echo 'Starting gunicorn server'
gunicorn --config gunicorn_conf.py app:app
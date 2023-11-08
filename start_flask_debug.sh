#!/bin/bash
source .venv/bin/activate
cd homesens
export FLASK_APP=homesens.py
export FLASK_DEBUG=True
# flask run
# flask run --host=0.0.0.0
python -m flask run --host=0.0.0.0

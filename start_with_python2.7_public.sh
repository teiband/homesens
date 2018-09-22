export FLASK_APP=/home/pi/workspace/homesens/homesens/homesens.py
export FLASK_DEBUG=true
# enable to find own files or modules within package
export PYTHONPATH=/home/pi/workspace/homesens/homesens
python -m flask run --host=0.0.0.0

# map-game-full

After cloning this repository, run the following lines to start the development server:

source map-game-full/bin/activate

cd map-game-full

pip install -r requirements.txt 

Wait for these reuqirements to all install

sudo apt-get install gstreamer-1.0

export FLASK_APP=app

python -m flask run

Now, the code should be running on your localhost:5000 ! If you wish to run it on a different port, for example 8080, run the line:

export FLASK_RUN_PORT=8080

before running "python -m flask run"

If you encounter any errors, feel free to reach out.


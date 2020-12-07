# map-game-full

For best results, you should run this from a Linux-based OS (VirtualBox VMs work fine) or on Mac. As of now, sound does not work when running on Windows. If you wish to run on Windows, use WSL for the installation process.

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


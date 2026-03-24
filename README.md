# Suyuan-MeLi-VOT
Suyuan MeLi VOT Dr.VOT Project

## Notes
This code is built up by combining 3 different older projects, as such it is pretty badly coded at the moment. Some file paths are hardcoded within the scripts, others are adaptive, it will not work out of the box of other peoples setups!

The project itself require Python 3.12, newest versions break some of the audio processing so make sure you're running this in Python 3.12. I recommend using [pyenv](https://github.com/pyenv/pyenv) for version management if you don't already have something in place.

The codes are written with the goal of preparing audio for Dr.VOT, however Dr.VOT itself is abandonware that will not work out of the box! As such, I have hyperlinked to a fork of the project which will work out of the box below.

## Dr.VOT Setup
The github page for my personal Dr.VOT fork can be found [here](https://github.com/SebastianoJGV/PersonalDr.VOTFork). If you don't have access it may give you a 404 error, reach out to me and I can add you as a contributor since its a private repository!

You need Python 3.9 specifically for this, again I recommend using a `pyenv local 3.9` function once cd'd into your Dr.VOT installation to ensure the code is running within python 3.9.

Here is the exact venv code I use to setup Dr.VOT personally, exclude the third line if you've already installed the requirements before

```
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 
```
To run Dr.VOT once your input files have been placed in `Dr.VOT/Data/raw`, open your terminal and cd to your Dr.VOT installation, then run `./run_script.sh`. Depending on the installation `run_script.sh` may not have execute permissions, so add permissions based off of your OS if necessary. (`chmod +x ./run_script.sh`)

This should fix the error package not found: boltons error that pops up if you don't have this specific version of setuptools installed.

## The Code
Its not great code, and not exactly heavily commented. At the very least know that they are designed to be used sequentially. `plosiveisolater.py` is the first file, `audioIsolation.py` is the second, and `csvMerger.py` can be used once you have the CSV files from `plosiveisolater.py` in one directory per language.


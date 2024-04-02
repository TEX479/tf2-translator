# Overview
[Setup](#setup)

# idk how to name this section
This program automatically reads the TeamFortress2-chat and translates all the messages that you recieve using google translator. Completely automated. This program is meant to be run alongside tf2 on a second monitor, but do with it what you want. It is easily expandable (as it is built in python (a programming language that is easy to learn (mostly))) and I will add features that I think are helpful, if I can be bothered to get back to coding. I might take suggestions, but this is just a little project I threw together within 3 days, so don't expect too much from me. I will probably be "active" on this tool untill I stop caring about tf2, or I get busy with anything else.

# Features
- automated translation of the chat using googletranslator
- chat filtering, to not show spam from common botnames
- built in message line that can be used to chat before properly connecting to the game
- automated message splitting (for messages sent using the program; since tf2 has a limit of 127 characters per message)
- "library spam" (a way to automatically send long multi-message texts)
- probably some other stuff too...

# Setup
The following setup is a description on what to do to get this tool running on linux. I do not have any expecience with windows and will not add support without enough demand. I will not try to stop this tool from working on windwows. It might, it might not, so just give it a try.\
\
To run this program, you need to have python version 3.11 or higher. (Lower versions have not been checked, but might work.) To get python, just go to the [official website](https://www.python.org/), if you don't have it already. Assuming you are on linux you probably have python. To check, type
```console
python --version
```
in your terminal of choice.\
\
Next up you will need to install a few librarys, if they are not already present on your system.\
You'll need `tkinter`, which at least on debian based systems can be installed using the command
```console
sudo apt-get install python3-tk
```
Other than tkinter, there are just python librarys left to install using `pip`: <!-- The packages you need are the following: -->
```
pip3 install rcon googletrans==3.1.0a0
```
(Note: Technically any version of `googletrans` could be used, but i encountered a rare error on my machine that is not present in the version specified. If you want, you can use the newer version, but I don't know if it will spit out the same errors as it did for me.)\
\
Finally to run the program, either type
```
python3 translator.py
```
in a terminal in the same directory as the script, or if you don't want to type the command every time into a terminal, do
```console
chmod +x translator.py
```
and execute the script as if it was a binary. (So you can basically rightclick it and click execute.)\
\
\
Now that the script is ready to be run, you only need to add the following to your TF2 launch options, if you haven't already:
```
-conclearlog -condebug
```
Now you are ready to go.\
\
**IMPORTANT:** If your tf2 installation **IS NOT** in the following folder, you have to edit the code and change the path in line 22 (if I didn't change that already (idk if I'll forgt to update the README.md when I add/remove some lines.). But you'll just have to see for yourself) to your own `Team Fortress 2` folder.\
Path that the code is using: `~/.steam/steam/steamapps/common/Team Fortress 2/`\
If your path is for example `/media/username/external_drive/SteamLibrary/steamapps/common/Team Fortress 2/`, you need to set the path to this one.

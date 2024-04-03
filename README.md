# Overview
- [random rambeling](#idk-how-to-name-this-section)
- [Features](#features)
- [Setup](#setup)
- [Customization](#customization)

# idk how to name this section
This program automatically reads the TeamFortress2-chat and translates all the messages that you recieve using google translator. Completely automated. This program is meant to be run alongside tf2 on a second monitor, but do with it what you want. It is easily expandable (as it is built in python (a programming language that is easy to learn (mostly))) and I will add features that I think are helpful, if I can be bothered to get back to coding. I might take suggestions, but this is just a little project I threw together within 3 days, so don't expect too much from me. I will probably be "active" on this tool untill I stop caring about tf2, or I get busy with anything else.

# Features
- automated translation of the chat using googletranslator
- chat filtering, to not show spam from common botnames
- built in message line that can be used to chat before properly connecting to the game
- automated message splitting (for messages sent using the program; since tf2 has a limit of 127 characters per message)
- "library spam" (a way to automatically send long multi-message texts)
- custom message coloring
- bad looks (but in dark mode )
- probably some other stuff too...

# Setup
The following setup is a description on what to do to get this tool running on linux. I do not have any expecience with windows and will not add support without enough demand. I will not try to stop this tool from working on windwows. It might, it might not, so just give it a try.\
\
Firstly you'll want to download this project. This can be done using the command
```console
git pull https://github.com/TEX479/tf2-translator.git
```
or by clicking the green `Code` icon on the top right of the file-browser, and then clicking `Download ZIP`.
\
Next, to run this program, you need to have python version 3.11 or higher. (Lower versions have not been checked, but might work.) To get python, just go to the [official website](https://www.python.org/), if you don't have it already. Assuming you are on linux you probably have python. To check, type
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
Other than tkinter, there are just python librarys left to install using `pip` (if not installed already get it [here](https://pip.pypa.io/en/stable/installation/)):
```console
pip3 install rcon googletrans==3.1.0a0
```
(Note: Technically any version of `googletrans` could be used, but i encountered a rare error on my machine that is not present in the version specified. If you want, you can use the newer version, but I don't know if it will spit out the same errors as it did for me.)\
\
Finally to run the program, either type
```console
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
Next, add the following lines to your `autoexec.cfg` inside your `Team Fortress 2/tf/cfg/` folder. If the file doesn't exist, create it. Replace `<password>` with a somewhat secret password (it can't contain any of these characters: `'";` (that might not be all of them, so just don't use the most crazy password)).
```
ip 0.0.0.0
rcon_password <password>
net_start
```
Change `<password>` in this projects `cfg/rcon_passwd.cfg`-file to your secret password you set in `Team Fortress 2/tf/cfg/autoexec.cfg`.
\
Now you are (probably) ready to go.\
\
**IMPORTANT:** If your tf2 installation **IS NOT** in the following folder, you have to edit the code and change the path in line 22 (if I didn't change that already (idk if I'll forgt to update the README.md when I add/remove some lines.). But you'll just have to see for yourself) to your own `Team Fortress 2` folder.\
Path that the code is using: `~/.steam/steam/steamapps/common/Team Fortress 2/`\
If your path is for example `/media/username/external_drive/SteamLibrary/steamapps/common/Team Fortress 2/`, you need to set the path to this one.\
\
**IMPORTANT 2:** The way the `net_start` launch option works, you will not be able to host a local server in this tf2-instance, you will still be able to join community and official servers though. (Idk which messages of the bots from Training you would want to translate anyway ;D)

# Customization
The program includes some customization features, for example colored messages or multimessage-scripts. This section will explain how to use these features.

## Colored Names
To use namecolouring, copy the desired names (seperated using new-lines, so `\n` so the ASCII-character 10) into `cfg/custom_colors.cfg`. Next, add a space, a hashtag and the desired color as 6-digit hexadecimal number. As an example, the line `TEX_479 #00FFFF` is already present in the file.

## Multimessage Scripts
For this feature, you can add textfiles into the `cfg/` folder. The files must end with `.msg` and need at least one other character in the filename to be read on execution of the program.\
Upon pressing the corresponding button in the `chat-spam` menu in the menu bar, the contents of the file will be sent line by line. If a line is longer than 127 characters (the tf2 message length limit), the program will split the line on the last possible whitespace.\
Note that `example.msg` is the only filename ending with `.msg` that will not be shown in the menubar, as it is only for demonstration purposes.

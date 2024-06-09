# Overview
- [random rambeling](#idk-how-to-name-this-section)
- [Features](#features)
- [Setup](#setup)
- [Customization](#customization)
- [How it works](#how-it-works)
- [reccomended software](#reccomended-software)

# idk how to name this section
This program automatically reads the TeamFortress2-chat and translates all the messages that you recieve using google translator. Completely automated. This program is meant to be run alongside tf2 on a second monitor, but do with it what you want. It is easily expandable (as it is built in python (a programming language that is easy to learn (mostly))) and I will add features that I think are helpful, if I can be bothered to get back to coding. I might take suggestions, but this is just a little project I threw together within 3 days, so don't expect too much from me. I will probably be "active" on this tool untill I stop caring about tf2, or I get busy with anything else.

# Features
- automated translation of the chat using googletranslator
- chat filtering, to not show spam from common botnames
- built in message line that can be used to chat before properly connecting to the game, or to run console commands with the message prefix `/`
- automated message splitting (for messages sent using the program; since tf2 has a limit of 127 characters per message)
- "chat spam" (a way to automatically send long multi-message texts)
- custom message coloring
- bad looks (but in dark mode)
- probably some other stuff too...

# Setup
The following setup is a description on what to do to get this tool running on linux. I do not have any expecience with windows and will not add support without enough demand (**EDIT: someone asked for an executable for windows, so I made a somewhat stable build for windows**). I will not try to stop this tool from working on windwows. It might, it might not, so just give it a try.\
\
To use this program, one can either [run the source code](#running-the-code) or [run a pre-compiled binary](#using-the-binary-executable) that can be run immediately.

## running the Code
### Get the Code
Firstly you'll want to download this project. This can be done using the command
```console
git pull https://github.com/TEX479/tf2-translator.git
```
or by clicking the green `Code` icon on the top right of the file-browser, and then clicking `Download ZIP`.

### Get the dependencies
Next, to run this program, you need to have python version 3.11 or higher. (Lower versions have not been checked, but might work.) To get python, just go to the [official website](https://www.python.org/), if you don't have it already. Assuming you are on linux you probably have python. To check, run
```console
python --version
```
in your terminal of choice.\
Next up you will need to install a few librarys, if they are not already present on your system.\
You'll need `tkinter`, which at least on debian based systems can be installed using the command
```console
sudo apt-get install python3-tk
```
Other than tkinter, there are just python librarys left to install using `pip` (if not installed already get it [here](https://pip.pypa.io/en/stable/installation/)):
```console
pip install -r requirements.txt
```
<!-- (Note: Technically any version of `googletrans` could be used, but i encountered a rare error on my machine that is not present in the version specified. If you want, you can use the newer version, but I don't know if it will spit out the same errors as it did for me.)\ -->

### Run the code
Finally to run the program, either type
```console
python3 main.py
```
in a terminal in the same directory as the script, or if you don't want to type the command every time into a terminal, do
```console
chmod +x main.py
```
and execute the script as if it was a binary. (So you can basically rightclick it and click execute.)\
\
Now, the only thing left to do is [setting up Team Fortress 2](#setup-team-fortress-2).

## using the binary executable
Download the [latest release](https://github.com/TEX479/tf2-translator/releases/tag/0.1.0) for your operating system (mac-os will not be supported, do not even think about asking me to do it). Extract the `.zip` file to some place you can remember. To run the translator, just run it like you would run any other program.\
\
Now, the only thing left to do is [setting up Team Fortress 2](#setup-team-fortress-2).

## Setup Team Fortress 2
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
Change `<password>` in this projects `cfg/rcon_passwd.cfg`-file (!!!create it if it doesn't exist yet!!!) to your secret password you set in `Team Fortress 2/tf/cfg/autoexec.cfg`.
\
Now you are (probably) ready to go.

## Some Notes
**IMPORTANT 1:** If your tf2 installation **IS NOT** in the following folder, you have to edit the code and change the path in line 22 (if I didn't change that already (idk if I'll forgt to update the README.md when I add/remove some lines.). But you'll just have to see for yourself) to your own `Team Fortress 2` folder.\
Path that the code is using: `~/.steam/steam/steamapps/common/Team Fortress 2/`\
If your path is for example `/media/username/external_drive/SteamLibrary/steamapps/common/Team Fortress 2/`, you need to set the path to this one.\
\
**IMPORTANT 2:** The way the `net_start` launch option works, you will not be able to host a local server in this tf2-instance, you will still be able to join community and official servers though. (Idk which messages of the bots from Training you would want to translate anyway ;D). Basically, the `map <map_name>` command will be a little broken.

# Customization
The program includes some customization features, for example colored messages or multimessage-scripts. This section will explain how to use these features.

## Colored Names
To use namecolouring, copy the desired names (seperated using new-lines, so `\n` so the ASCII-character 10) into `cfg/custom_colors.cfg`. Next, add a space, a hashtag and the desired color as 6-digit hexadecimal number. As an example, the line `TEX_479 #00FFFF` is already present in the file.

## Multimessage Scripts
For this feature, you can add textfiles into the `cfg/` folder. The files must end with `.msg` and need at least one other character in the filename to be read on execution of the program.\
Upon pressing the corresponding button in the `chat-spam` menu in the menu bar, the contents of the file will be sent line by line. If a line is longer than 127 characters (the tf2 message length limit), the program will split the line on the last possible whitespace.\
Note that `example.msg` is the only filename ending with `.msg` that will not be shown in the menubar, as it is only for demonstration purposes.

## Ignoring Spam from Bots
Disclaimer: This feature is only name-based chat filtering. It does not actually detect bots, so bots with random names will be able to bypass this filtering system *for now*. The filter works by checking if the name of a person who sent a message can be matched to any know regular expression for botnames.
### How to set it up
You will need to add/edit the file `cfg/botnames.cfg`. In this file, every line is a seperate entry for a botname. Or to be more precise, its "regular expression".\
A guide of how regular expressions work can be found [**here**](https://www.w3schools.com/python/python_regex.asp). The important parts of this article are the sections `Metacharacters`, `Special Sequences` and `Sets`.\
An [example file](cfg/botnames.cfg) with some common botnames is present in the current version of this programms `cfg`-folder.

# How it works
This tool reads the messages that are shown in the console and filters them to only use chat-messages. To do this, it simply looks for lines that have the following character formation in it: ` :  `. A whitespace, followed by a column and two more whitespaces. This is the only pattern (that I know of) that can be used to easily distinguish chat messages from regular console-output. It also filters out messages like `<...> joined the game`.\
After getting all the messages, they are passed along to the translator library, converted to english text and shown in the textbox.\
To write messages or to use the "message-scripts", the tool connects to your tf2 instance using ["rcon"](https://developer.valvesoftware.com/wiki/Source_RCON_Protocol) and sends commands like `say "<your message>"`.\
\
That pretty much explains how the tool interfaces your tf2 client. If you have any questions remaining, you can try to ask me, but google will probably help you way quicker.

# Reccomended Software
This is a list of tools that can help out a lot.

### [botkicker (by Bash-09)](https://github.com/Bash-09/tf2-bot-kicker-gui).
This program is meant to keep track of bots & cheaters, automatically call them out when they join and start votekicks as soon as possible.\
Another neat feature is the automated bot-marking using "regular expression matching".

### [MegaAntiCheat](https://github.com/MegaAntiCheat)
Allthough [MegaAntiCheat](https://github.com/MegaAntiCheat) (or "MAC" for short) is still in beta, it already has some great features such as, but not limited to the automated vote-calls on bots. As MAC is not fully released yet, there are still some features left to be added (mostly the "masterbase").

### [Team Fortress 2 ;)](https://store.steampowered.com/app/440/Team_Fortress_2/)
Well duh. The Translator is meant to interface the game, so if it is not present, this tool has no purpose.

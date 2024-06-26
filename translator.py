#!/usr/bin/env python3

import threading
from icecream import ic
import rcon.source as rcon
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog
from googletrans import Translator
from googletrans.models import Translated, Detected
import time
import os
import re
from multiprocessing import Pool
import time
import textwrap
import platform

class backend():
    def __init__(self, host:str, port:int, passwd:str, tf2_path:str|None=None) -> None:
        self.HOST = host
        self.PORT = port
        self.PASSWORD = passwd
        if tf2_path == None:
            self.tf2_path = "~/.steam/steam/steamapps/common/Team Fortress 2"
        else:
            os.path.normpath(tf2_path)
            self.tf2_path = tf2_path
        
        try:
            self.tf2_path = os.path.expanduser(self.tf2_path)
        except Exception as e:
            print(e)
            self.tf2_path = ""

        self.names_trusted:list[str] = []
        self.names_muted:list[str] = []

        self.known_messages = []
        self.__known_log_length:int = 0

        if os.path.exists(f"{self.tf2_path}/tf/console.log"):
            ...
            #with open(f"{self.tf2_path}tf/console.log", "rb") as f:
            #    content = f.read()
            #self.__known_log_length = max(len(content)-100000, 0)
        else:
            raise FileNotFoundError(f"Could not open 'console.log'. Is the TeamFortress2 directory set properly?")
        
        self.bot_names_re = self.import_botnames()
        self.reload_rcon()

    def reload_rcon(self) -> None:
        try:
            self.client = rcon.Client(host=self.HOST, port=self.PORT, passwd=self.PASSWORD)
            self.client.connect(True)
        except Exception as e:
            print(f"An error occured while connecting to the game using rcon:\t{e}")

    def import_botnames(self, path:str= "cfg/botnames.cfg") -> list[str]:
        if not os.path.exists(path):
            return []
        
        with open(path, "rb") as f:
            content = f.read()
        
        content = content.decode(encoding="utf-8", errors="replace")
        
        #names = re.sub("\n\n+", "\n", content).split("\n")
        names = content.split("\n")
        for i in range(names.count("")):
            names.remove("")
        return names
    
    def bot_name(self, name:str) -> bool:
        for name2mute in self.names_muted:
            if name2mute in name:
                return True
        for pattern in self.bot_names_re:
            re_value = re.search(pattern, name)
            if re_value != None:
                return True
        return False

    def _auto_add_mutes(self, message:str) -> None:
        message_name = message.split(" :  ")[0]
        bot_names = []
        for name_trusted in self.names_trusted:
            if not (name_trusted in message_name):
                continue
            if not (" :  Bots joining " in message):
                continue
            message_split = re.split("teams?: ", message, 1)
            if len(message_split) == 1:
                '''
                in automated messages, there has to be either of the following string-slices:
                "team: ", "teams: "
                if they aren't there, we can't be sure the message should be processed
                '''
                return
            
            message_split = message_split[-1]
            if message_split[-1] == ".":
                message_split = message_split[:-1]
            bot_names = message_split.split(", ")
            break
        if bot_names == []:
            return
        
        for bot_name in bot_names:
            if not (bot_name in self.names_muted):
                self.names_muted.append(bot_name)

    def _get_messages(self, message:str) -> str:
        spliced = message.split(" :  ")
        message_start = spliced[0]
        
        if self.bot_name(message_start):
            return ""
        
        message_2translate = " :  ".join(spliced[1:])
        message_translated = self.translate(message_2translate)

        new = ""

        #if message_2translate != message_translated:
        #    new += "(" + self.detect(message_2translate)[0] + "->en) "
        new += message_start + " :  " + message_translated
        return new

    def get_messages(self) -> list[str]:
        messages = self._read_messages()

        # THIS is the correct place to add_mutes(), since access to global variables is broken inside multiprocessing
        for message in messages:
            self._auto_add_mutes(message)
        
        if platform.system() != "Windows":
        #start_time = time.process_time()
            with Pool(16) as p:
                try:
                    messages = p.map(self._get_messages, messages)
                except Exception as e:
                    print(e)
        #end_time = time.process_time()
        #time_diff = end_time - start_time
        #print(f"CPU Execution time: {time_diff} seconds")
        else:
            for i in range(len(messages)):
                messages[i] = self._get_messages(messages[i])

        ammount_of_junk = messages.count("")
        for i in range(ammount_of_junk):
            messages.remove("")
        
        return messages

    def _read_messages(self) -> list[str]:
        if not os.path.exists(f"{self.tf2_path}/tf/console.log"):
            print("could not find console.log")
            return []
        
        with open(f"{self.tf2_path}/tf/console.log", "rb") as f:
            content = f.read()

        h = len(content)
        if h < self.__known_log_length:
            self.__known_log_length = 0
        content = content[self.__known_log_length:]
        self.__known_log_length = h

        #content = content.decode("utf-8")
        
        content_messages = [] #[line if " :  " in line else "" for line in content.split("\n")]
        for line in content.split(b"\n"):
            if b" :  " in line:
                try:
                    line2 = line.decode("utf-8")
                except:
                    line2 = str(line)[2:-1].replace("\\n", "\n").replace("\\'", "'")
                content_messages.append(line2)
        
        return content_messages

    def translate(self, message:str) -> str:
        '''
        only translates a string, doesn't take the name out or anything, so only the message-part of the message should get passed to this funktion
        '''
        translator = Translator()
        try:
            translated_message = translator.translate(message)
        except:
            return message
        if type(translated_message) == Translated:
            return translated_message.text
        else:
            return message
        
    def detect(self, message:str) -> tuple[str, float | int]:
        translator = Translator()
        try:
            detection = translator.detect(message)
        except:
            return "-1", 0
        if type(detection) == Detected:
            lang = detection.lang
            conf = detection.confidence
            if type(lang) != str:
                lang = "-1"
            if (type(conf) != float) and (type(conf) != int):
                conf = 0
            return lang, conf
        else:
            return "-1", 0

    def rcon_run(self, command:str) -> str:
        '''
        runs command on the rcon-server
        '''
        try:
            response = self.client.run(command)
            return response
        except Exception as e1:
            try:
                self.reload_rcon()
                response = self.client.run(command)
                return response
            except Exception as e2:
                return str(e1) + "\n#########\n" + str(e2)


class GUI():
    def __init__(self) -> None:
        self.run_updateloop = True
        self.keep_scrolling = True
        self.__first_ever = True
        self.gui_running = False
        self.right_monitor = False
        self.command_prefix = "/"
        self.bulk_message_delay = 2 #in seconds
        self.exit_bool = False
        #self.CRLF = platform.system() == "Windows"

        if os.path.exists("./cfg/rcon_passwd.cfg"):
            #print("found cfg/rcon_passwd.cfg")
            with open("./cfg/rcon_passwd.cfg", "r") as f:
                content = f.read()
            if content[-1] == "\n":
                content = content[:-1]
            if content[-1] == "\r":
                content = content[-1]
            self.rcon_passwd = content
            #print(f"{self.rcon_passwd=}")
        else:
            print(f'File not found: ./cfg/rcon_passwd.cfg; requesting password...')
            self.set_rconpw()

        if os.path.exists("./cfg/tf2dir.cfg"):
            #print("found cfg/rcon_passwd.cfg")
            with open("./cfg/tf2dir.cfg", "r") as f:
                content = f.read()
            if content[-1] == "\n":
                content = content[:-1]
            if content[-1] == "\r":
                content = content[-1]
            self.tf2dir = content
            if not os.path.exists(self.tf2dir):
                self.set_tf2dir()
            #print(f"{self.rcon_passwd=}")
        else:
            print(f'File not found: ./cfg/tf2dir.cfg; requesting path...')
            self.set_tf2dir()
        
        self.custom_colors = self.import_custom_colors_cfg()

        self.backend = backend(host="127.0.0.1", port=27015, passwd=self.rcon_passwd, tf2_path=self.tf2dir)
        self.backend.names_trusted = [name for name in self.custom_colors]

    def set_rconpw(self) -> None:
        self.rcon_passwd = simpledialog.askstring("Set rcon password", "What is your current rcon password?")
        if self.rcon_passwd != None:
            with open("cfg/rcon_passwd.cfg", "w") as f:
                f.write(self.rcon_passwd)
        #self.backend.PASSWORD = self.rcon_passwd
        #self.backend.reload_rcon()
    
    def set_tf2dir(self) -> None:
        tf2dir = filedialog.askdirectory(mustexist=True, title="Location of the folder \"Team Fortress 2\"")
        self.tf2dir = tf2dir
        with open("cfg/tf2dir.cfg", "w") as f:
            f.write(tf2dir)
        #self._reload_backend()

    def say_message_script(self, name) -> None:
        if not os.path.exists(f"./cfg/{name}.msg"):
            self.write_message_to_board(f'message "{name}" not found.')
            return

        with open(f"./cfg/{name}.msg", "r") as f:
            contents = f.read()
        messages = contents.split("\n")
        empty_count = messages.count("")
        for i in range(empty_count):
            messages.remove("")

        messages_shortend = []
        for msg in messages:
            msgs_short = textwrap.wrap(msg, 127, break_long_words=False)
            for msg_short in msgs_short:
                messages_shortend.append(msg_short)

        sending = threading.Thread(target=lambda messages=messages: self.rcon_send_messages(messages))
        sending.start()

    def import_custom_colors_cfg(self) -> dict[str, str]:
        if not(os.path.exists("./cfg/custom_colors.cfg")):
            return {}
        
        with open("./cfg/custom_colors.cfg", "r") as f:
            contents = f.read()
        
        list2return = {}
        for line in contents.split("\n"):
            if len(line.split(" ")) < 2:
                continue
            name = " ".join(line.split(" ")[:-1])
            color = line.split(" ")[-1]
            list2return[name] = color

        return list2return

    def import_custom_messages(self) -> list[str]:
        files = os.listdir("./cfg")
        files_filtered:list[str] = []
        for file in files:
            if len(file) < 5:
                continue
            if file[-4:] != ".msg":
                continue
            if file == "example.msg":
                continue
            files_filtered.append(file)
        files_filtered = [file[:-4] for file in files_filtered]
        return files_filtered

    def create_gui(self) -> None:
        self.main_window = tk.Tk()
        self.main_window.title("Chat-Translator")
        height:int = 500
        width = 570
        offset = 1920 if self.right_monitor else 0
        self.main_window.geometry(f"{width}x{height}+{offset+1100+250}+0")
        self.main_window.protocol("WM_DELETE_WINDOW", self.stop)
        #self.main_window.overrideredirect(True)

        self.text_box = scrolledtext.ScrolledText(self.main_window, wrap=tk.WORD, background="#202020")
        self.text_box.pack(expand=True, fill='both')
        self.text_box.configure(state="disabled")

        for name in self.custom_colors:
            self.text_box.tag_config(name, foreground=self.custom_colors[name])
        self.text_box.tag_config("rest", foreground="#FFFFFF")


        self.menubar = tk.Menu(self.main_window, background="#202020", foreground="#FFFFFF")
        self.filemenu = tk.Menu(self.menubar, tearoff=0, background="#202020", foreground="#FFFFFF")
        self.filemenu.add_command(label="reload", command=self._reload_backend)
        self.filemenu.add_command(label="reload rcon", command=self.backend.reload_rcon)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.stop)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.configmenu = tk.Menu(self.menubar, tearoff=0, background="#202020", foreground="#FFFFFF")
        self.configmenu.add_command(label="set rcon password", command=self.set_rconpw)
        self.configmenu.add_command(label="set TF2 directory", command=self.set_tf2dir)
        self.menubar.add_cascade(label="config", menu=self.configmenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0, background="#202020", foreground="#FFFFFF")
        custom_messages = self.import_custom_messages()
        for message in custom_messages:
            self.helpmenu.add_command(label=message, command=lambda message=message: self.say_message_script(message))
        self.menubar.add_cascade(label="chat-spam", menu=self.helpmenu)

        self.main_window.config(menu=self.menubar)

        self.chat_box_var = tk.StringVar(self.main_window, "")
        self.chat_box = tk.Entry(self.main_window, width=50, textvariable=self.chat_box_var, background="#202020", foreground="#FFFFFF")
        self.chat_box.pack(fill='both')
        self.chat_box.bind('<Return>', self._say_in_chat, add=None)

    def _say_in_chat(self, event:tk.Event) -> None:
        msg = self.chat_box_var.get()
        self.chat_box_var.set("")

        if msg.replace(" ", "") == "":
            return
        
        if len(msg) > 1:
            if msg[0] == self.command_prefix and msg[1] == self.command_prefix:
                msg = msg[1:]
            elif msg[0] == self.command_prefix:
                rcon_output = self.backend.rcon_run(msg[1:])
                if rcon_output != "":
                    self.write_message_to_board(rcon_output)
                return

        msg = msg.replace("\"", "'")

        if len(msg) < 128:
            self.backend.rcon_run("say \"" + msg + "\"")
            return
        #print("msg too long. splitting.....")
        lines = textwrap.wrap(msg, 127, break_long_words=False)
        
        sending = threading.Thread(target=lambda lines=lines: self.rcon_send_messages(lines))
        sending.start()

    def stop(self) -> None:
        '''
        gets executed on pressing the "x" to close the window;
        ends all loops concerning the gui and delets itself
        '''
        #self.save_playerlist()
        self.run_updateloop = False
        self.exit_bool = True
        self.main_window.destroy()

    def write_message_to_board(self, message:str) -> None:
        if self.exit_bool:
            return
        self.text_box.configure(state="normal")
        messages = message.split("\n")
        for msg in messages:
            for name in self.custom_colors:
                if name in msg.split(" :  ")[0]:
                    self.text_box.insert("end", ("\n" if not self.__first_ever else "") + msg, name)
                    break
            else:
                self.text_box.insert("end", ("\n" if not self.__first_ever else "") + msg, "rest")
            self.__first_ever = False
        if self.keep_scrolling:
            self.text_box.yview('end')
        self.text_box.configure(state="disabled")

    def start(self) -> None:
        if not self.gui_running:
            self.create_gui()
            self.gui_running = True
        
        write_loop = threading.Thread(target=self.translation_loop)
        write_loop.start()
        self.main_window.mainloop()

    def translation_loop(self) -> None:
        while self.run_updateloop:
            time.sleep(5)
            messages = self.backend.get_messages()
            if len(messages) > 0:
                string2write = "\n".join(messages)
                self.write_message_to_board(string2write)

    def _reload_backend(self) -> None:
        self.backend = backend(host="127.0.0.1", port=27015, passwd=self.rcon_passwd, tf2_path=self.tf2dir)
        self.text_box.configure(state="normal")
        self.text_box.delete('1.0', tk.END)
        self.text_box.configure(state="disabled")
        self.__first_ever = True

    def rcon_send_messages(self, messages:list[str]) -> None:
        for msg in messages:
            self.backend.rcon_run("say \"" + msg + "\"")
            time.sleep(self.bulk_message_delay)

system = platform.system()
print(f"{system=}")
gui = GUI()
gui.start()

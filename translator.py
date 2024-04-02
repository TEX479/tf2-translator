#!/usr/bin/env python3

import threading
from icecream import ic
import rcon.source as rcon
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from googletrans import Translator
from googletrans.models import Translated, Detected
import time
import os
import re
from multiprocessing import Pool
import time
import textwrap

class backend():
    def __init__(self, host:str, port:int, passwd:str):
        self.HOST = host
        self.PORT = port
        self.PASSWORD = passwd
        self.tf2_path = "/home/tex/.steam/steam/steamapps/common/Team Fortress 2/"
        self.known_messages = []
        self.__known_log_length:int = 0

        if os.path.exists(f"{self.tf2_path}tf/console.log"):
            with open(f"{self.tf2_path}tf/console.log", "rb") as f:
                content = f.read()
            #self.__known_log_length = max(len(content)-100000, 0)
        
        bot_names = ["DELTATRONIC", "DELTATR0NIC", "DELTATRONC", "DELTATR0NC",
                          "HEXATRONIC", "HEXATR0NIC", "OMEGATRONIC", "OMEGATR0NIC", "TWILIGHT SPARKLE"]
        
        #expands the botnames to regular expressions for multiple variations
        self.bot_names_re = []
        self.re_metachars = ["[", "]", "\\", ".", "^", "$", "*", "+", "?", "{", "}", "|", "(", ")"]
        for name in bot_names:
            name_re = ""
            for character in name:
                if character in self.re_metachars:
                    name_re += "\\"
                name_re += character + ".*"
            self.bot_names_re.append(name_re)
    
    def bot_name(self, name:str):
        for pattern in self.bot_names_re:
            re_value = re.search(pattern, name)
            if re_value != None:
                return True
        return False

    def _get_messages(self, message:str):
        spliced = message.split(" :  ")
        #print(spliced)
        spliced = [spliced[0], " :  ".join(spliced[1:])]
        message_start = spliced[0]
        
        if self.bot_name(message_start):
            #print(f"Got message from a bot. (name '{message_start}' matched a re) skipping...")
            return ""
        
        message_2translate = spliced[1]
        message_translated = self.translate(message_2translate)

        new = ""

        #if message_2translate != message_translated:
        #    new += "(" + self.detect(message_2translate)[0] + "->en) "
        #print(spliced)
        new += message_start + " :  " + message_translated
        #print(new)
        return new

    def get_messages(self):
        messages = self._read_messages()
        #start_time = time.process_time()
        with Pool(16) as p:
            try:
                messages = p.map(self._get_messages, messages)
            except:
                pass
        #end_time = time.process_time()
        #time_diff = end_time - start_time

        #print(f"CPU Execution time: {time_diff} seconds")

        ammount_of_junk = messages.count("")
        for i in range(ammount_of_junk):
            messages.remove("")
        
        return messages

    def _read_messages(self) -> list[str]:
        if not os.path.exists(f"{self.tf2_path}tf/console.log"):
            return [""]
        
        with open(f"{self.tf2_path}tf/console.log", "rb") as f:
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
        
        #print(content_messages)
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

    def rcon_run(self, command:str):
        '''
        runs command on the rcon-server
        '''
        try:
            with rcon.Client(self.HOST, port=self.PORT, passwd=self.PASSWORD) as client:
                response = client.run(command)
            return response
        except Exception as e:
            #ic(e)
            return ""


class GUI():
    def __init__(self) -> None:
        self.run_updateloop = True
        self.keep_scrolling = True
        self.__first_ever = True
        self.gui_running = False
        self.right_monitor = False
        self.command_prefix = "/"
        self.bulk_message_delay = 2

        self.backend = backend(host="127.0.0.1", port=27015, passwd="mac_rcon")

    def say_message_script(self, name):
        if not os.path.exists(f"/home/tex/VSCode/Python/games/tf2/chat_translator/cfg/{name}.msg"):
            self.write_message_to_board(f'message "{name}" not found.')
            return

        with open(f"/home/tex/VSCode/Python/games/tf2/chat_translator/cfg/{name}.msg", "r") as f:
            contents = f.read()
        messages = contents.split("\n")
        empty_count = messages.count("")
        for i in range(empty_count):
            messages.remove("")

        sending = threading.Thread(target=lambda messages=messages: self.rcon_send_messages(messages))
        sending.start()

    def create_gui(self):
        self.main_window = tk.Tk()
        self.main_window.title("Chat-Translator")
        height:int = 500
        width = 1920*2 - (3020 + 250)
        offset = 1920 if self.right_monitor else 0
        self.main_window.geometry(f"{width}x{height}+{offset+1100+250}+0")
        self.main_window.protocol("WM_DELETE_WINDOW", self.stop)
        

        self.text_box = scrolledtext.ScrolledText(self.main_window, wrap=tk.WORD, background="#202020")
        self.text_box.pack(expand=True, fill='both')
        self.text_box.configure(state="disabled")
        self.text_box.tag_config("TEX_479", foreground="#00FFFF")
        self.text_box.tag_config("Honigbi3ne", foreground="#FFFF00")
        self.text_box.tag_config("rest", foreground="#FFFFFF")
    

        self.menubar = tk.Menu(self.main_window)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="reload", command=self._reload_backend)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.stop)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="not kicking innocents", command=lambda: self.say_message_script("not_kicking_innocents"))
        self.helpmenu.add_command(label="cheating not hacking", command=lambda: self.say_message_script("cheating_not_hacking"))
        self.helpmenu.add_command(label="i dont cheat", command=lambda: self.say_message_script("i_dont_cheat"))
        self.menubar.add_cascade(label="chat-spam", menu=self.helpmenu)

        self.main_window.config(menu=self.menubar)

        self.chat_box_var = tk.StringVar(self.main_window, "")
        self.chat_box = tk.Entry(self.main_window, width=50, textvariable=self.chat_box_var)
        self.chat_box.pack(fill='both')
        self.chat_box.bind('<Return>', self._say_in_chat, add=None)

    def _say_in_chat(self, event):
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

    def stop(self):
        '''
        gets executed on pressing the "x" to close the window;
        ends all loops concerning the gui and delets itself
        '''
        #self.save_playerlist()
        self.run_updateloop = False
        self.main_window.destroy()

    def write_message_to_board(self, message:str):
        self.text_box.configure(state="normal")
        messages = message.split("\n")
        for msg in messages:
            if "TEX_479" in msg.split(" :  ")[0]:
                self.text_box.insert("end", ("\n" if not self.__first_ever else "") + msg, "TEX_479")
            elif "Honigbi3ne" in msg.split(" :  ")[0]:
                self.text_box.insert("end", ("\n" if not self.__first_ever else "") + msg, "Honigbi3ne")
            else:
                self.text_box.insert("end", ("\n" if not self.__first_ever else "") + msg, "rest")
            self.__first_ever = False
        if self.keep_scrolling:
            self.text_box.yview('end')
        self.text_box.configure(state="disabled")

    def start(self):
        if not self.gui_running:
            self.create_gui()
            self.gui_running = True
        
        write_loop = threading.Thread(target=self.translation_loop)
        write_loop.start()
        self.main_window.mainloop()

    def translation_loop(self):
        while self.run_updateloop:
            time.sleep(5)
            messages = self.backend.get_messages()
            if len(messages) > 0:
                string2write = "\n".join(messages)
                self.write_message_to_board(string2write)

    def _reload_backend(self):
        self.backend = backend(host="127.0.0.1", port=27015, passwd="mac_rcon")
        self.text_box.configure(state="normal")
        self.text_box.delete('1.0', tk.END)
        self.text_box.configure(state="disabled")

    def rcon_send_messages(self, messages:list[str]):
        for msg in messages:
            self.backend.rcon_run("say \"" + msg + "\"")
            time.sleep(self.bulk_message_delay)

gui = GUI()
gui.start()

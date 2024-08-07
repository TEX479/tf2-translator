#!/usr/bin/env python3

import threading
from icecream import ic
import rcon.source as rcon
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog
import time
import os
import re
from multiprocessing import Pool
import time
import textwrap
import platform
from backend import backend


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
            if len(content) != 0:
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
            if len(content) != 0:
                if content[-1] == "\n":
                    content = content[:-1]
                if content[-1] == "\r":
                    content = content[-1]
                self.tf2dir = content
            else:
                self.tf2dir = None
            if self.tf2dir == None or not os.path.exists(self.tf2dir):
                self.set_tf2dir(reload=False)
            #print(f"{self.rcon_passwd=}")
        else:
            print(f'File not found: ./cfg/tf2dir.cfg; requesting path...')
            self.set_tf2dir(reload=False)
        
        self.custom_colors = self.import_custom_colors_cfg()

        self.backend = backend(host="127.0.0.1", port=27015, passwd=self.rcon_passwd, tf2_path=self.tf2dir)
        self.backend.names_trusted = [name for name in self.custom_colors]

        self.theme_default = {"main.bg": "#202020", "main.fg": "#FFFFFF"}

    def set_rconpw(self) -> None:
        self.rcon_passwd = simpledialog.askstring("Set rcon password", "What is your current rcon password?")
        if self.rcon_passwd != None:
            with open("cfg/rcon_passwd.cfg", "w") as f:
                f.write(self.rcon_passwd)
        #self.backend.PASSWORD = self.rcon_passwd
        #self.backend.reload_rcon()
    
    def set_tf2dir(self, reload=False) -> None:
        tf2dir = filedialog.askdirectory(mustexist=True, title="Location of the folder \"Team Fortress 2\"")
        self.tf2dir = tf2dir
        with open("cfg/tf2dir.cfg", "w") as f:
            f.write(tf2dir)
        if reload:
            self._reload_backend()

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

    def _init_theme(self) -> None: # -> dict[str, str]:
        self.change_theme(path="cfg/current.theme")
        
    def load_theme(self, path:str|None=None) -> dict[str, str] | None:
        if path == None:
            path = filedialog.askopenfilename(filetypes=[("theme-file", ".theme")], initialdir="cfg/")
        #ic(path)
        if not os.path.exists(path):
            if path == "cfg/current.theme":
                return self.theme_default
            return None
        
        try:
            with open(path, "r") as f:
                content = f.read()
            lines = content.replace("\r", "").split("\n")
            theme = {}
            for line in lines:
                name = line.split(": ")[0]
                content = ": ".join(line.split(": ")[1:])
                if name == "":
                    continue
                theme[name] = content
            return theme
        except Exception as exception:
            print("An error occured while loading the theme:")
            ic(exception)
            return None

    def save_theme(self, theme:dict[str, str], path:str|None=None) -> None:
        if path == None:
            print("Save-dialog not implemented. ignoring...")

        content = ""
        for name in theme:
            if name != "": #and theme[name] != "":
                content += f"{name}: {theme[name]}\n"
        
        try:
            with open(path, "w") as f:
                f.write(content)
        except Exception as exception:
            print("An error occured during the process of saving the theme:")
            ic(exception)
            return

    def change_theme(self, path:str|None=None) -> None:
        theme = self.load_theme(path=path)
        if theme == None:
            return
        
        self.apply_theme(theme=theme, theme_defaulting=True)
        self.save_theme(theme=theme, path="cfg/current.theme")

    def create_gui(self) -> None:
        bgc = "#303446" #background colour; old style: '#202020'
        fgc = "#c6d0f5" #foreground colour; old style: '#FFFFFF'
        self.main_window = tk.Tk()
        self.main_window.title("Chat-Translator")
        height:int = 500
        width = 570
        offset = 1920 if self.right_monitor else 0
        self.main_window.geometry(f"{width}x{height}+{offset+1100+250}+0")
        self.main_window.protocol("WM_DELETE_WINDOW", self.stop)
        #self.main_window.overrideredirect(True)

        self.text_box = scrolledtext.ScrolledText(self.main_window, wrap=tk.WORD, background=bgc)
        self.text_box.pack(expand=True, fill='both')
        self.text_box.configure(state="disabled")

        for name in self.custom_colors:
            self.text_box.tag_config(name, foreground=self.custom_colors[name])
        self.text_box.tag_config("rest", foreground=fgc)


        self.menubar = tk.Menu(self.main_window, background=bgc, foreground=fgc)
        self.filemenu = tk.Menu(self.menubar, tearoff=0, background=bgc, foreground=fgc)
        self.filemenu.add_command(label="reload", command=self._reload_backend)
        self.filemenu.add_command(label="reload rcon", command=self.backend.reload_rcon)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.stop)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.configmenu = tk.Menu(self.menubar, tearoff=0, background=bgc, foreground=fgc)
        self.configmenu.add_command(label="set rcon password", command=self.set_rconpw)
        self.configmenu.add_command(label="set TF2 directory", command=lambda: self.set_tf2dir(reload=True))
        self.configmenu.add_command(label="change theme", command=self.change_theme)
        self.menubar.add_cascade(label="config", menu=self.configmenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0, background=bgc, foreground=fgc)
        custom_messages = self.import_custom_messages()
        for message in custom_messages:
            self.helpmenu.add_command(label=message, command=lambda message=message: self.say_message_script(message))
        self.menubar.add_cascade(label="chat-spam", menu=self.helpmenu)

        self.main_window.config(menu=self.menubar)

        self.chat_box_var = tk.StringVar(self.main_window, "")
        self.chat_box = tk.Entry(self.main_window, width=50, textvariable=self.chat_box_var, background=bgc, foreground=fgc)
        self.chat_box.pack(fill='both')
        self.chat_box.bind('<Return>', self._say_in_chat, add=None)

        self._init_theme()

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

    def change_colours(self) -> None:
        #self.text_box.configure(background="#888888")
        self.apply_theme(theme={"main.bg": "#FFFFFF", "main.fg": "#000000"})

    def apply_theme(self, theme:dict[str, str], theme_defaulting:bool=True) -> None:
        '''
        `theme: dict`
        theme is a dict which binds color-strings such as "red" or "#00FFFF" to certain strings
        `main` will be applied first, every other change specified will be applied afterwards

        currently supported names for binding:
        |name|applies to|
        |-|-|
        |`main.bg`|background of the entire app|
        |`main.fg`|foreground of the entire app|
        |`textbox.bg`|background of the text box|
        |`textbox.fg`|foreground of the text box|
        |`entry.bg`|background of the entry box|
        |`entry.fg`|foreground of the entry box|
        |`menubar.bg`|background of the menubar|
        |`menubar.fg`|foreground of the menubar|
        |`menuentry.bg`|background of every menubar-entry|
        |`menuentry.fg`|foreground of every menubar-entry|
        '''
        ic(theme)

        if "main.bg" in theme:
            self.text_box.configure(background=theme["main.bg"])
            self.chat_box.configure(background=theme["main.bg"])
            self.menubar.configure(background=theme["main.bg"])
            self.filemenu.configure(background=theme["main.bg"])
            self.configmenu.configure(background=theme["main.bg"])
            self.helpmenu.configure(background=theme["main.bg"])
        elif theme_defaulting:
            self.text_box.configure(background=self.theme_default["main.bg"])
            self.chat_box.configure(background=self.theme_default["main.bg"])
            self.menubar.configure(background=self.theme_default["main.bg"])
            self.filemenu.configure(background=self.theme_default["main.bg"])
            self.configmenu.configure(background=self.theme_default["main.bg"])
            self.helpmenu.configure(background=self.theme_default["main.bg"])
        if "main.fg" in theme:
            #self.text_box.configure(foreground=theme["main.fg"])
            self.text_box.tag_config("rest", foreground=theme["main.fg"])
            self.chat_box.configure(foreground=theme["main.fg"])
            self.menubar.configure(foreground=theme["main.fg"])
            self.filemenu.configure(foreground=theme["main.fg"])
            self.configmenu.configure(foreground=theme["main.fg"])
            self.helpmenu.configure(foreground=theme["main.fg"])
        elif theme_defaulting:
            #self.text_box.configure(foreground=self.theme_default["main.fg"])
            self.text_box.tag_config("rest", foreground=self.theme_default["main.fg"])
            self.chat_box.configure(foreground=self.theme_default["main.fg"])
            self.menubar.configure(foreground=self.theme_default["main.fg"])
            self.filemenu.configure(foreground=self.theme_default["main.fg"])
            self.configmenu.configure(foreground=self.theme_default["main.fg"])
            self.helpmenu.configure(foreground=self.theme_default["main.fg"])
        
        if "textbox.bg" in theme:
            self.text_box.configure(background=theme["textbox.bg"])
        #elif theme_defaulting:
        #    self.text_box.configure(background=self.theme_default["textbox.bg"])
        if "textbox.fg" in theme:
            #self.text_box.configure(foreground=theme["textbox.fg"])
            self.text_box.tag_config("rest", foreground=theme["textbox.fg"])
        #elif theme_defaulting:
        #    self.text_box.configure(foreground=self.theme_default["textbox.fg"])
        #    self.text_box.tag_config("rest", foreground=self.theme_default["textbox.fg"])

        if "entry.bg" in theme:
            self.chat_box.configure(background=theme["entry.bg"])
        #elif theme_defaulting:
        #    self.chat_box.configure(background=self.theme_default["entry.bg"])
        if "entry.fg" in theme:
            self.chat_box.configure(foreground=theme["entry.fg"])
        #elif theme_defaulting:
        #    self.chat_box.configure(foreground=self.theme_default["entry.fg"])
        
        if "menubar.bg" in theme:
            self.menubar.configure(background=theme["menubar.bg"])
        #elif theme_defaulting:
        #    self.menubar.configure(background=self.theme_default["menubar.bg"])
        if "menubar.fg" in theme:
            self.menubar.configure(foreground=theme["menubar.fg"])
        #elif theme_defaulting:
        #    self.menubar.configure(foreground=self.theme_default["menubar.fg"])
        
        if "menuentry.bg" in theme:
            self.filemenu.configure(background=theme["menuentry.bg"])
            self.configmenu.configure(background=theme["menuentry.bg"])
            self.helpmenu.configure(background=theme["menuentry.bg"])
        #elif theme_defaulting:
        #    self.filemenu.configure(background=self.theme_default["menuentry.bg"])
        #    self.configmenu.configure(background=self.theme_default["menuentry.bg"])
        #    self.helpmenu.configure(background=self.theme_default["menuentry.bg"])
        if "menuentry.fg" in theme:
            self.filemenu.configure(foreground=theme["menuentry.fg"])
            self.configmenu.configure(foreground=theme["menuentry.fg"])
            self.helpmenu.configure(foreground=theme["menuentry.fg"])
        #elif theme_defaulting:
        #    self.filemenu.configure(foreground=self.theme_default["menuentry.fg"])
        #    self.configmenu.configure(foreground=self.theme_default["menuentry.fg"])
        #    self.helpmenu.configure(foreground=self.theme_default["menuentry.fg"])


if __name__ == "__main__":
    system = platform.system()
    print(f"{system=}")
    gui = GUI()
    gui.start()

from googletrans import Translator
from googletrans.models import Translated, Detected
import os, re, platform
from icecream import ic
import rcon.source as rcon
from multiprocessing import Pool

class backend():
    def __init__(self, host:str, port:int, passwd:str, tf2_path:str|None=None) -> None:
        self.HOST = host
        self.PORT = port
        self.PASSWORD = passwd
        if tf2_path == None or tf2_path == "":
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
            ...
            #os.remove("cfg/tf2dir.cfg")
            #raise FileNotFoundError(f"Could not open 'console.log'. Is the 'Team Fortress 2' directory set properly? Resetting 'cfg/tf2dir.cfg'...\nPlease relaunch the programm.")
        
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
            return ["backendError :  Could not find 'console.log'. Did you run the game with the '-condebug -conclearlog' launch options? Is the path set correctly?"]
        
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
            if (b" :  " in line) and not (b"  :  " in line):
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
        '''
        detects the language of `message`
        '''
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

#!/usr/bin/env python
##
# Cman IRC Bot
##
# Copyright 2013 Carter Hinsley
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##
import os
import sys
import socket
import subprocess
from random import randint

if (len(sys.argv) == 1):
    print("No server specified.")
    exit()

class Utils:
    @classmethod
    def get_username(cls, message):
        return message[1:message.find("!")].lower()
    @classmethod
    def notify_user(cls, user, message):
        meta["sock"].send("NOTICE %s :%s\r\n" % (user, message))
    @classmethod
    def respond(cls, message):
        for line in message.split("\n"):
            meta["sock"].send("PRIVMSG %s :%s: %s\r\n" % (meta["data"].split(' ')[2], meta["user"], line))
        print("Said: \"%s\"" % message)
    @classmethod
    def swaggify(cls, users):
        for user in users.split(","):
            meta["sock"].send("PRIVMSG Swagbot :%s\r\n" % user)
            print("Swagged %s" % user)

meta = {}
meta["botname"]  = "Swaglord"
meta["data"]     = ""
meta["message"]  = ""
meta["user"]     = ""
meta["server"]   = sys.argv[2]
meta["sock"]     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
meta["channels"] = sys.argv[3:]
meta["userinfo"] = {}
meta["swagees"] = sys.argv[1]



#Connect to IRC server
try:
    meta["sock"].connect((meta["server"], 6667))
except:
    print("\nERROR: Connection could not be established.")
    exit()
print("\nConnection established with %s on port 6667." % meta["server"])

#Change nickname
meta["sock"].send("USER %s 0 * :%s\r\nNICK %s\r\n" % (meta["botname"], os.getlogin(), meta["botname"]))
#Main loop
while (1):
    meta["data"] = meta["sock"].recv(1024)
    for line in meta["data"].split("\r\n"):
        try:
            if (line != ''):
                print(line)
                if (line[:5] == "PING "):
                    meta["sock"].send("PONG "+line[5:]+"\r\n")
                if (line.split(' ')[1] == "001"):
                    meta["sock"].send("MODE "+meta["botname"]+" +B\r\n"+''.join(["JOIN %s\r\n" % channel for channel in meta["channels"]]))
                else:
                    Utils.swaggify(meta["swagees"])
        except:
            pass
#!/usr/bin/env python
##
# Tobbot IRC Bot
##
# Copyright 2015 Carter Hinsley
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
            meta["sock"].send(("PRIVMSG %s :%s: %s\r\n" % (meta["data"].split(' ')[2], meta["user"], line)).encode("utf-8"))
        print("Said: \"%s\"" % message)

meta = {}
meta["botname"]  = "tobbot"
meta["owners"]   = ["xnil", "xnull", "xnool", "xinihil", "carolyn", "carolny", "starbuck"]
meta["data"]     = ""
meta["message"]  = ""
meta["user"]     = ""
meta["server"]   = sys.argv[1]
meta["sock"]     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
meta["channels"] = sys.argv[2:]

##########
#COMMANDS
def bash(cmd):
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, close_fds = True)
    output = p.stdout.read().decode("utf-8").rstrip('\n')
    if len(output.split('\n')) > 3:
        output = "Output consumes too many lines."
    if (output == ''):
        output = "Success."
    Utils.respond(output)
#COMMANDS
##########

#Connect to IRC server
try:
    meta["sock"].connect((meta["server"], 6667))
except:
    print("\nERROR: Connection could not be established.")
    exit()
print("\nConnection established with %s on port 6667." % meta["server"])

#Change nickname
meta["sock"].send(("USER %s 0 * :%s\r\nNICK %s\r\n" % (meta["botname"], meta["owners"][0], meta["botname"])).encode("utf-8"))
#Main loop
while (1):
    meta["data"] = meta["sock"].recv(1024).decode("utf-8")
    for line in meta["data"].split("\r\n"):
        try:
            if (line != ''):
                print(line)
                if (line[:5] == "PING "):
                    meta["sock"].send(("PONG "+line[5:]+"\r\n").encode("utf-8"))
                if (line.split(' ')[1] == "001"):
                    meta["sock"].send(("MODE "+meta["botname"]+" +B\r\n"+''.join(["JOIN %s\r\n" % channel for channel in meta["channels"]])).encode("utf-8"))
                #If receiving PRIVMSG from a user
                if (line.split(' ')[1] == "PRIVMSG"):
                    meta["user"] = Utils.get_username(line)
                    meta["message"] = line[line.find(":", 1)+1:].rstrip()
                    if meta["user"] in meta["owners"]:
                        if meta["message"].startswith("#"):
                            bash(meta["message"][1:])
                        elif meta["message"].startswith(meta["botname"]):
                            command = ' '.join(meta["message"].split(' ')[1:])
                            meta["sock"].send(("%s\r\n" % command).encode("utf-8"))
        except:
            pass

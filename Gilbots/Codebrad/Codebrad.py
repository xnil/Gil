#!/usr/bin/env python
##
# CodeBrad IRC Bot
##
# Copyright (C) 2012 by Carter Hinsley
# All Rights Reserved.
##
import os
import sys
import socket
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

meta = {}
meta["botname"]  = "CodeBrad"
meta["data"]     = ""
meta["message"]  = ""
meta["user"]     = ""
meta["server"]   = sys.argv[1]
meta["sock"]     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
meta["channels"] = sys.argv[2:]
meta["userinfo"] = {}

##########
#COMMANDS
def interpret(lang, code):
    lang = {
        "ada"         : "7",
        "bash"        : "28",
        "bf"          : "12",
        "brainfuck"   : "12",
        "c"           : "11",
        "c#"          : "27",
        "c++"         : "1",
        "c++0x"       : "44",
        "c99"         : "34",
        "clj"         : "111",
        "clojure"     : "111",
        "clisp"       : "32",
        "d"           : "102",
        "erlang"      : "36",
        "f#"          : "124",
        "fortran"     : "5",
        "go"          : "114",
        "hs"          : "21",
        "haskell"     : "21",
        "java"        : "10",
        "java7"       : "55",
        "js"          : "35",
        "javascript"  : "35",
        "lua"         : "26",
        "node"        : "56",
        "node.js"     : "56",
        "obj-c"       : "43",
        "objective-c" : "43",
        "ocaml"       : "8",
        "pascal"      : "2",
        "perl"        : "3",
        "php"         : "29",
        "pike"        : "19",
        "prolog"      : "15",
        "py"          : "4",
        "python"      : "4",
        "py3"         : "116",
        "python3"     : "116",
        "ruby"        : "17",
        "scala"       : "39",
        "ss"          : "33",
        "scheme"      : "33",
        "smalltalk"   : "23",
        "sql"         : "40",
        "tcl"         : "38",
        "vb.net"      : "101"
    }[lang.lower()]
    code = code.replace("\\r", "\\\\r").replace("\\n", "\\\\n")
    #Scheme
    if (lang == "33"):
        try:
            f = open("scheme.pre")
            prefix = f.read()
            f.close()
        except:
            prefix = ""
        code = "%s\n(display %s)" % (prefix, code)
    #C++
    if (lang == "1"):
        code = "#include <iostream>\n#include <string>\nusing namespace std;\nint main() {%s}" % code
    #C
    if (lang == "11"):
        code = "#include <stdio.h>\nint main() {%s}" % code
    params = urllib.urlencode({"lang":lang, "code":code})
    f = urllib.urlopen("http://cdh473.com/ideone/", params)
    output = [line.lstrip() for line in f.read().split("\n")]
    time = output[output.index('["time"]=>')+1]
    time = time[time.find('(')+1:-1]
    stdout = output[output.index('["output"]=>')+1]
    if (stdout.endswith('"')):
        stdout = stdout[stdout.find('"')+1:-1]
    else:
        stdout = stdout[stdout.find('"')+1:]
    if (len(stdout) > 300):
        stdout = "%s..." % stdout[:300]
    Utils.respond("%ss> %s" % (time, stdout))
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
meta["sock"].send("USER %s 0 * :%s\r\nNICK %s\r\n" % (meta["botname"], "cdh473", meta["botname"]))
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
                #If receiving PRIVMSG from a user
                if (line.split(' ')[1] == "PRIVMSG"):
                    meta["user"] = Utils.get_username(line)
                    meta["message"] = line[line.find(":", 1)+1:].rstrip().split(' ')
                    if meta["message"][0].startswith("#!"):
                        try:
                            interpret(meta["message"][0][2:], (' '.join(meta["message"][1:])))
                        except KeyError:
                            Utils.respond(["Huh?", "What?"][randint(0,1)])
        except:
            pass
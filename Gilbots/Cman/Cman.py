#!/usr/bin/env python
##
# Cman IRC Bot
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

meta = {}
meta["botname"]  = "Cman"
meta["data"]     = ""
meta["message"]  = ""
meta["user"]     = ""
meta["server"]   = sys.argv[1]
meta["sock"]     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
meta["channels"] = sys.argv[2:]
meta["userinfo"] = {}

##########
#COMMANDS
def c_(*arg):
    includes = ["<string.h>"]
    code = ''.join(["#include "+x+"\n" for x in includes]) + "#include <stdlib.h>\n#include <stdio.h>\nint main(void) {%s return EXIT_SUCCESS;}" % arg
    f = open("./temp.c", 'w')
    f.write(code)
    f.close()
    p = subprocess.Popen("gcc %s -o %s" % (os.path.abspath("temp.c"), os.path.abspath("temp")), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    output = p.stdout.read()
    if (output):
        Utils.respond(output.rstrip())
    else:
        p = subprocess.Popen("./temp", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        output = p.stdout.read().rstrip('\n')
        if (output == ''):
            output = "Success."
        Utils.respond(output)
        os.remove(os.path.abspath("temp"))
    os.remove(os.path.abspath("temp.c"))
def cpp_(*arg):
    includes = ["<iostream>", "<stdio.h>"]
    code = ''.join(["#include "+x+"\n" for x in includes]) + "using namespace std;\nint main() {%s return 0;}" % arg
    f = open("./temp.cpp", 'w')
    f.write(code)
    f.close()
    p = subprocess.Popen("g++ %s -o %s" % (os.path.abspath("temp.cpp"), os.path.abspath("temp")), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    output = p.stdout.read()
    if (output):
        Utils.respond(output.rstrip())
    else:
        p = subprocess.Popen("./temp", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        output = p.stdout.read().rstrip('\n')
        if (output == ''):
            output = "Success."
        Utils.respond(output)
        os.remove(os.path.abspath("temp"))
    os.remove(os.path.abspath("temp.cpp"))
def csharp_(*arg):
    includes = ["System"]
    code = ''.join(["using "+x+";\n" for x in includes]) + "class MainClass { public static void Main() {%s}}" % arg
    f = open("./temp.cs", 'w')
    f.write(code)
    f.close()
    p = subprocess.Popen("mono %s -o %s" % (os.path.abspath("temp.cs"), os.path.abspath("temp")), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    output = p.stdout.read()
    if (output):
        Utils.respond(output.rstrip())
    else:
        p = subprocess.Popen("./temp", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        output = p.stdout.read().rstrip('\n')
        if (output == ''):
            output = "Success."
        Utils.respond(output)
        os.remove(os.path.abspath("temp"))
    os.remove(os.path.abspath("temp.cs"))
def node_(*arg):
    code = arg
    f = open("./temp.js", 'w')
    f.write(code)
    f.close()
    p = subprocess.Popen("node ./temp.js", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    output = p.stdout.read()
    Utils.respond(output.rstrip())
    os.remove(os.path.abspath("temp.js"))
def python_(*arg):
    code = arg
    f = open("./temp.py", 'w')
    f.write(code)
    f.close()
    p = subprocess.Popen("python ./temp.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    output = p.stdout.read()
    Utils.respond(output.rstrip())
    os.remove(os.path.abspath("temp.py"))
commands = {"c":c_, "cpp":cpp_, "c++":cpp_, "c#":csharp_, "cs":csharp_, "csharp":csharp_, "node":node_, "js":node_, "python":python_, "py":python_}
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
                #If receiving PRIVMSG from a user
                if (line.split(' ')[1] == "PRIVMSG"):
                    meta["user"] = Utils.get_username(line)
                    meta["message"] = line[line.find(":", 1)+1:].rstrip().split(' ')
                    if meta["message"][0].startswith("#!"):
                        try:
                            commands[meta["message"][0][2:].lower()](' '.join(meta["message"][1:]))
                        except KeyError:
                            Utils.respond(["Huh?", "What?"][randint(0,1)])
        except:
            pass
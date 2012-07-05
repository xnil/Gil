#!/usr/bin/env python
##
#Gil IRC Bot
##
#Copyright (C) 2012 by Carter Hinsley
#All Rights Reserved.
##
import os
import sys
import time
import socket
import urllib
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
        meta["sock"].send("PRIVMSG %s :%s: %s\r\n" % (meta["data"].split(' ')[2], meta["user"], message))
        print("Said: \"%s\"" % message)
    @classmethod
    def glub(cls):
        Utils.respond(["Glub.", "Glubbub Glub.", "Glubbety Glubbuby Glub.", "Glub Glubbety."][randint(0,3)])

meta = {}
meta["botname"]  = "Gil"
meta["data"]     = ""
meta["message"]  = ""
meta["user"]     = ""
meta["server"]   = sys.argv[1]
meta["sock"]     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
meta["channels"] = sys.argv[2:]
meta["blockquoters"] = {}
meta["userinfo"] = {}
#Load users
for user in [f for f in os.listdir("./") if os.path.isfile(os.path.join("./", f)) and f.endswith(".user")]:
    f = open("./%s" % user)
    meta["userinfo"][user[:-5]] = f.read()
    f.close()

##########
#COMMANDS
def add_(*arg):
    if len(arg) >= 1:
        info = ' '.join(arg)
        f = open("./%s.user" % meta["user"].lower(), 'w')
        f.write(info)
        f.close()
        meta["userinfo"][meta["user"].lower()] = info
        Utils.glub()
def help_(*arg):
    if len(arg) == 0:
        Utils.respond("Commands: %s" % ', '.join([x for x in commands]))
        Utils.respond("say \""+meta["botname"]+" help <commandname>\" for help with a specific command.")
    else:
        target = arg[0].lower()
    if target == "add":
        Utils.notify_user(meta["user"], "Command `add <info>`: Used to store personal info.")
    if target == "help":
        Utils.notify_user(meta["user"], "Command `help [command]`: Displays help on a command. If no command is specified, displays command list.")
    if target == "info":
        Utils.notify_user(meta["user"], "Command `info <user>`: Displays personal info for <user>.")
    if target == "join":
        Utils.notify_user(meta["user"], "Command `join <#channel> [#channel] [#channel]...`: Tells %s to join all of the listed channels.")
    if target == "quote":
        Utils.notify_user(meta["user"], "Command `quote <quote>`: Submits <quote> to the Awfulnet QDB (http://awfulnet.org/quotes).")
    if target == "quotebegin":
        Utils.notify_user(meta["user"], "Command `quotebegin`")
        Utils.notify_user(meta["user"], "Example:")
        Utils.notify_user(meta["user"], "gil quotebegin")
        Utils.notify_user(meta["user"], "<quote line 1>")
        Utils.notify_user(meta["user"], "<quote line 2>")
        Utils.notify_user(meta["user"], "quoteend")
        Utils.notify_user(meta["user"], "Submits a multiline quote to the Awfulnet QDB (http://awfulnet.org/quotes). If you mess up, replace \"quoteend\" with \"quotediscard\" and start over.")
def info_(*arg):
    if len(arg) != 0:
        who = arg[0].lower()
        if (who in meta["userinfo"]):
            Utils.notify_user(meta["user"], "%s: %s" % (who, meta["userinfo"][who]))
        else:
            Utils.notify_user(meta["user"], "Invalid target \"%s\"." % who)
def join_(*arg):
    meta["sock"].send(''.join(["JOIN %s\r\n" % channel for channel in arg if channel.startswith("#")]))
    Utils.glub()
def quote_(*arg):
    """Works with QdbS. You may modify this function to get it to work with other sites using QdbS by simply changing the URL."""
    if len(arg) >= 1:
        quote = ' '.join(arg)
        params = urllib.urlencode({"do":"add", "quote":quote})
        #Change the following URL to change the quote submission destination
        q = urllib.urlopen("http://awfulnet.org/quotes/index.php", params)
        q.close()
        Utils.glub()
def quotebegin_(*arg):
    """Similar to `quote_` but used for multiline quotes."""
    meta["blockquoters"][meta["user"]] = ""
commands = {"add":add_, "help":help_, "info":info_, "join":join_, "quote":quote_, "quotebegin":quotebegin_}
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
    try:
        meta["data"] = meta["sock"].recv(512)
        if (meta["data"] != ''):
            print(meta["data"])
        if (meta["data"][:5] == "PING "):
            meta["sock"].send("PONG "+meta["data"][5:]+"\r\n")
        if ("\nPING " in meta["data"]):
            meta["sock"].send("PONG "+meta["data"][meta["data"].find("\nPING ")+7:]+"\r\n")
        if (meta["data"].split(' ')[1] == "001"):
            meta["sock"].send("MODE "+meta["botname"]+" +B\r\n"+''.join(["JOIN %s\r\n" % channel for channel in meta["channels"]]))
        #If receiving PRIVMSG from a user
        if (meta["data"].split(' ')[1] == "PRIVMSG"):
            meta["user"] = Utils.get_username(meta["data"])
            meta["message"] = meta["data"][meta["data"].find(":", 1)+1:].rstrip().split(' ')
            if meta["user"] in meta["blockquoters"]:
                if meta["message"][0] == "quoteend":
                    quote_(meta["blockquoters"][meta["user"]])
                    del meta["blockquoters"][meta["user"]]
                elif meta["message"][0] == "quotediscard":
                    del meta["blockquoters"][meta["user"]]
                    Utils.respond("Glub...")
                else:
                    meta["blockquoters"][meta["user"]] += ' '.join(meta["message"])+'\n'
            elif meta["message"][0].lower().startswith(meta["botname"].lower()):
                try:
                    commands[meta["message"][1].lower()](*meta["message"][2:])
                except KeyError:
                    Utils.respond(["Glub?", "Glubbuby Glubbub?"][randint(0,1)])
        elif (meta["data"].split(' ')[1] == "JOIN"):
            meta["user"] = Utils.get_username(meta["data"])
            Utils.notify_user(meta["user"], "Hi, %s! Welcome to %s!" % (meta["user"], meta["data"].rstrip().split(' ')[2][1:]))
    except:
        pass
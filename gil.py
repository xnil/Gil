#!/usr/bin/env python
##
# Gil IRC Bot
##
# Copyright (C) 2012 by Carter Hinsley
# All Rights Reserved.
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
    def glub(cls):
        Utils.respond(["Glub.", "Glubbub Glub.", "Glubbety Glubbuby Glub.", "Glub Glubbety."][randint(0,3)])
    @classmethod
    def notify_user(cls, user, message):
        meta["sock"].send("NOTICE %s :%s\r\n" % (user, message))
    @classmethod
    def respond(cls, message):
        meta["sock"].send("PRIVMSG %s :%s: %s\r\n" % (meta["data"].split(' ')[2], meta["user"], message))
        print("Said: \"%s\"" % message)
    @classmethod
    def spit_quote(cls, params):
        if isinstance(params, dict):
            params = urllib.urlencode(params)
        q = urllib.urlopen(meta["quotedburl"]+"?%s" % params)
        tmp = q.read()
        q.close()
        tmp_i = tmp.find("<p class=\"quote\">")
        tmp = tmp[tmp_i:tmp.find("</p>", tmp_i)]
        quote = tmp[tmp.find("<br />")+6:].replace("\n", "").split("<br />")
        print quote
        if quote == [""]:
            Utils.notify_user(meta["user"], "Invalid quote index.")
        else:
            Utils.notify_user(meta["user"], "Quote %s:" % tmp[tmp.find("<u>")+3:tmp.find("</u>")])
            for line in quote:
                Utils.notify_user(meta["user"], line.lstrip().rstrip().replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"").replace("&nbsp;", "  "))

meta = {}
meta["botname"]  = "Gil"
meta["data"]     = ""
meta["message"]  = ""
meta["user"]     = ""
meta["quotedburl"] = "http://awfulnet.org/quotes/index.php"
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
    if target == "i":
        Utils.notify_user(meta["user"], "Command `i ... love ... you`: Causes Gil to respond with \"<nick>: I glub you too!\"")
    if target == "info":
        Utils.notify_user(meta["user"], "Command `info <user>`: Displays personal info for <user>.")
    if target == "join":
        Utils.notify_user(meta["user"], "Command `join <#channel> [#channel] [#channel]...`: Tells %s to join all of the listed channels.")
    if target == "spitfact":
        Utils.notify_user(meta["user"], "Command `spitfact`: Spits out a random fact.")
    if target == "spitquote":
        Utils.notify_user(meta["user"], "Command `spitquote [quoteID]`: Spits out a random quote. If [quoteID] is provided, spits out the indicated quote.")
    if target == "quote":
        Utils.notify_user(meta["user"], "Command `quote <quote>`: Submits <quote> to the Awfulnet QDB ("+meta["quotedburl"]+").")
    if target == "quotebegin":
        Utils.notify_user(meta["user"], "Command `quotebegin`")
        Utils.notify_user(meta["user"], "Example:")
        Utils.notify_user(meta["user"], "gil quotebegin")
        Utils.notify_user(meta["user"], "<quote line 1>")
        Utils.notify_user(meta["user"], "<quote line 2>")
        Utils.notify_user(meta["user"], "quoteend")
        Utils.notify_user(meta["user"], "Submits a multiline quote to the Awfulnet QDB ("+meta["quotedburl"]+"). If you mess up, replace \"quoteend\" with \"quotediscard\" and start over.")
def i_(*arg):
    if "love" in [x.lower() for x in arg] and arg[-1].lower().startswith("you"):
        Utils.respond("I glub you too!")
    else:
        raise KeyError
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
def spitfact_(*arg):
    q = urllib.urlopen("http://randomfactgenerator.net/")
    tmp = q.read()
    q.close()
    tmp_i = tmp.find("<div id='z'>")
    print("yus!")
    tmp = tmp[tmp_i+12:tmp.find("<br/>", tmp_i)]
    Utils.notify_user(meta["user"], tmp)
def spitquote_(*arg):
    if len(arg) == 0:
        Utils.spit_quote({"p":"random"})
    else:
        params = arg[0].lstrip("#")
        Utils.spit_quote(params)
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
commands = {"add":add_, "help":help_, "i":i_, "info":info_, "join":join_, "spitfact":spitfact_, "spitquote":spitquote_, "quote":quote_, "quotebegin":quotebegin_}
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
                    if meta["user"] in meta["blockquoters"]:
                        if meta["message"][0] == "quoteend":
                            quote_(meta["blockquoters"][meta["user"]])
                            del meta["blockquoters"][meta["user"]]
                        elif meta["message"][0] == "quotediscard":
                            del meta["blockquoters"][meta["user"]]
                            Utils.respond("Glub...")
                        elif meta["blockquoters"][meta["user"]].count("\n") == 12:
                            del meta["blockquoters"][meta["user"]]
                            Utils.respond("Glub... (Quote discarded, too long)")
                        else:
                            meta["blockquoters"][meta["user"]] += ' '.join(meta["message"])+'\n'
                    elif meta["message"][0].lower().startswith(meta["botname"].lower()):
                        try:
                            commands[meta["message"][1].lower()](*meta["message"][2:])
                        except KeyError:
                            Utils.respond(["Glub?", "Glubbuby Glubbub?"][randint(0,1)])
                elif (line.split(' ')[1] == "JOIN"):
                    meta["user"] = Utils.get_username(line)
                    Utils.notify_user(meta["user"], "Hi, %s! Welcome to %s!" % (meta["user"], line.rstrip().split(' ')[2][1:]))
        except:
            pass
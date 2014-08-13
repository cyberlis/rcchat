# -*- coding: utf-8 -*-
from org.bukkit.event import EventPriority
from org.bukkit.event.player import PlayerChatEvent
from org.bukkit.event.player import PlayerJoinEvent
from time import time
from net.milkbowl.vault.economy import Economy
from org.bukkit import ChatColor
from io import open as ioopen
import os.path as path
import os
import json
from org.bukkit.command import ConsoleCommandSender
import re
from org.bukkit.event.player import PlayerQuitEvent

class ChatListener(PythonListener):
    def __init__(self, plugin):
        self.plugin = plugin
        self.msgTime = {}  #this var contains players and their time delay
        PythonListener.__init__(self) # never forget to do this!
        
    @PythonEventHandler(PlayerQuitEvent, EventPriority.NORMAL)
    def onPlayerQuit(self, event):
        pl = event.getPlayer()
        if pl.getName() in self.msgTime:
            del self.msgTime[pl.getName()]
            
         
    @PythonEventHandler(PlayerChatEvent, EventPriority.NORMAL)        
    def onPlayerChat(self, event):
        pl = event.getPlayer()
        if pl.isOp():
            return
        self.config = self.plugin.getPluginCfg()
        allplayers = list(event.getRecipients())
        if self.config["localChat"] == True:
            if event.getMessage()[0] == "*":
                econ = None
                econProvider = server.getServicesManager().getRegistration(Economy)
                if econProvider:
                    econ = econProvider.getProvider()
                else:
                    pl.sendMessage(ChatColor.translateAlternateColorCodes("&", self.config["noEcoMsg"]))
                if econ:
                    if econ.getBalance(pl.getName()) >= self.config["msgCost"]:
                        econ.withdrawPlayer(pl.getName(), self.config["msgCost"])
                        event.setMessage(event.getMessage()[1:])
                        event.setFormat(ChatColor.translateAlternateColorCodes("&", self.config["globalPrefix"]) + event.getFormat())
                        return
                    else:
                        pl.sendMessage(ChatColor.translateAlternateColorCodes("&", self.config["noMoneyMsg"] % str(self.config["msgCost"])))
                        event.setCancelled(True)
                        return
            if event.getMessage()[0] <> "!":
                for reciver in allplayers:
                    if self.checkRadius(pl.getLocation(), reciver.getLocation()) == False and not reciver.isOp() and not reciver.hasPermission("rcchat.seelocalchat"):
                        event.getRecipients().remove(reciver)
                event.setFormat(ChatColor.translateAlternateColorCodes("&", self.config["localPrefix"]) + event.getFormat())
                return
            else:
                if pl.hasPermission("rcchat.nomsgdelay"):
                    event.setMessage(event.getMessage()[1:])
                    event.setFormat(ChatColor.translateAlternateColorCodes("&",self.config["globalPrefix"]) + event.getFormat())
                    return
                if pl.getName() in self.msgTime:
                    delay = self.config["msgDelay"]
                    for group in self.config["permissionsGroups"]:
                        if pl.hasPermission("rcchat." + group):
                            delay = self.config["permissionsGroups"][group]
                    if time() - self.msgTime[pl.getName()] < delay:
                        pl.sendMessage(ChatColor.translateAlternateColorCodes("&", self.config["noEnoughTime"] % unicode(int(delay - (time() - self.msgTime[pl.getName()])))))
                        event.setCancelled(True)
                        return
                    else:
                        self.msgTime[pl.getName()] = time()
                        event.setMessage(event.getMessage()[1:])
                        event.setFormat(ChatColor.translateAlternateColorCodes("&",self.config["globalPrefix"]) + event.getFormat())
                        return
                else:
                    self.msgTime[pl.getName()] = time()
                    event.setMessage(event.getMessage()[1:])
                    event.setFormat(ChatColor.translateAlternateColorCodes("&",self.config["globalPrefix"]) + event.getFormat())
        
    def checkRadius(self, plpos1, plpos2):
        if plpos1 == plpos2:
            return True
        if plpos1.getWorld() != plpos2.getWorld():
            return False
        return plpos1.distance(plpos2) <= self.config["msgRadius"]
        
        
class MainClass(PythonPlugin):
            
    def onEnable(self):
        self.loadConfig()
        pm = self.getServer().getPluginManager()
        self.listener = ChatListener(self)
        pm.registerEvents(self.listener, self)
        print "[RCchat] enabled"
        
    def onDisable(self):
        print "[RCchat] disabled"

    def onCommand(self, sender, command, label, args):
        if args[0] == "reload" and (sender.isOp() or isinstance(sender, ConsoleCommandSender)):
            self.loadConfig()
            print "RCchat config reloaded"
            return True
        return False
    
    
    def loadConfig(self):
        """ Loads plugin config
            Uses json to store config because i dont like yml
        """
        
        #default config
        self.pluginCfg = {"localChat":True, "msgRadius":150, "msgDelay":60, 
                          "msgCost":100, 
                          "noEcoMsg":u"&4[RCchat] Eco doesnt work.Install Vault.", 
                          "noMoneyMsg":u"&9[RCchat]&f Not enough money. You need %s $",
                          "noEnoughTime":u"&9[RCchat]&f You write to global chat too fast. Please wait %s sec. or write '*message' to use chargeable message for global chat",
                          "globalPrefix":"&9[G]&f", 
                          "localPrefix":"&9[L]&f",
                          "permissionsGroups":{"prem":30, "vip":40}
                          }
        name = self.description.getName()
        if path.exists("plugins/" + name) and path.isdir("plugins/" + name):
            if path.exists("plugins/" + name + "/config.json"):
                f = ioopen("plugins/" + name + "/config.json", "r", encoding="utf-8")
                self.pluginCfg = json.load(f)
                f.close()
            else:
                f = ioopen("plugins/" + name + "/config.json", "w", encoding="utf-8")
                f.write(unicode(json.dumps(self.pluginCfg, indent=4, ensure_ascii=False)))
                f.close()
        else:
            os.mkdir("plugins/" + name)
            f = ioopen("plugins/" + name + "/config.json", "w", encoding="utf-8")
            f.write(unicode(json.dumps(self.pluginCfg, indent=4, ensure_ascii=False)))
            f.close()
    def getPluginCfg(self):
        return self.pluginCfg

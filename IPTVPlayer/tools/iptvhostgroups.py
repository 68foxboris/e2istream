# -*- coding: utf-8 -*-

#
#
# @Codermik release, based on @Samsamsam's E2iPlayer public.
# Released with kind permission of Samsamsam.
# All code developed by Samsamsam is the property of the Samsamsam and the E2iPlayer project,  
# all other work is © E2iStream Team, aka Codermik.  TSiPlayer is © Rgysoft, his group can be
# found here:  https://www.facebook.com/E2TSIPlayer/
#
# https://www.facebook.com/e2iStream/
#
#

#

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, byteify, GetConfigDir, GetHostsList, IsHostEnabled
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostsGroupItem
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads, dumps as json_dumps
###################################################

###################################################
# FOREIGN import
###################################################
import codecs
from os import path as os_path, remove as os_remove
###################################################


class IPTVHostsGroups:
    def __init__(self):
        printDBG("IPTVHostsGroups.__init__")
        self.lastError = ''
        self.GROUPS_FILE = GetConfigDir('iptvplayerhostsgroups.json')
        
        # groups
        self.PREDEFINED_GROUPS = ["userdefined", "moviesandseries", "cartoonsandanime", "music", "sport", "live", "documentary", "science", \
                                  "polish", "english", "german", "french", "russian", "hungarian", "arabic", "greek", "latino", "italian","swedish","balkans","others"]
        self.PREDEFINED_GROUPS_TITLES = {"userdefined":      "User defined", 
                                         "moviesandseries":  "Movies and series",
                                         "cartoonsandanime": "Cartoons and anime",
                                         "music":            "Music",
                                         "sport":            "Sport",
                                         "live":             "Live",
                                         "documentary":      "Documentary",
                                         "science":          "Science",
                                         "polish":           "Polish",
                                         "english":          "English",
                                         "german":           "German",
                                         "french":           "French",
                                         "russian":          "Russian",
                                         "hungarian":        "Hungarian",
                                         "arabic":           "Arabic",
                                         "greek":            "Greek",
                                         "latino":           "Latino",
                                         "italian":          "Italian",
                                         'swedish':          "Swedish",
                                         "balkans":          "Balkans",
                                         "others":           "Others",
                                        }
        
        self.LOADED_GROUPS = []
        self.LOADED_GROUPS_TITLES = {}
        self.LOADED_DISABLED_GROUPS = []
        
        self.CACHE_GROUPS = None
        
        # hosts
        self.PREDEFINED_HOSTS = {}
        self.PREDEFINED_HOSTS['userdefined']      = ['favourites']
        self.PREDEFINED_HOSTS['moviesandseries']  = ['yifytv','solarmovie','mythewatchseries','thewatchseriesto','classiccinemaonline','seriesonline', 'filma24hdcom', 'allboxtv', \
                                                     'tfarjocom','kinox','filmativa','cartoonhd','putlockertvto','123movieshd','movs4ucom','filmovizijastudio','forjatn']
        self.PREDEFINED_HOSTS['cartoonsandanime'] = ['cartoonhd','watchcartoononline']
        self.PREDEFINED_HOSTS['sport']            = ['bbcsport','twitchtv','ourmatchnet','watchwrestling','hoofootcom']
        self.PREDEFINED_HOSTS['live']             = ['youtube','liveleak','twitchtv']
        self.PREDEFINED_HOSTS['documentary']      = ['mythewatchseries','thewatchseriesto','seriesonline','dailymotion','ororotv']
        self.PREDEFINED_HOSTS['science']          = ['dailymotion','ororotv']
        
        self.PREDEFINED_HOSTS['polish']           = ['youtube','twitchtv','allboxtv']
        self.PREDEFINED_HOSTS['english']          = ['youtube','musicbox','liveleak','twitchtv','bbciplayer','bbcsport','itvcom','cartoonhd','watchcartoononline','seriesonline','mythewatchseries', \
                                                     'thewatchseriesto','ororotv','yifytv','classiccinemaonline','solarmovie','putlockertvto','123movieshd','filmativa','dailymotion', 'filma24hdcom', \
                                                     'ourmatchnet','watchwrestlinguno','hoofootcom','dailymotion','ororotv','movs4ucom','filmovizijastudio','forjatn']
        self.PREDEFINED_HOSTS['german']           = ['youtube','twitchtv','dailymotion','spiegeltv','ardmediathek','kinox']
        self.PREDEFINED_HOSTS['french']           = ['youtube','twitchtv','dailymotion','tsiplayer', 'tfarjocom','tfarjocom']
        self.PREDEFINED_HOSTS['russian']          = ['youtube','twitchtv','dailymotion']
        self.PREDEFINED_HOSTS['hungarian']        = ['youtube','twitchtv','dailymotion']
        self.PREDEFINED_HOSTS['arabic']           = ['youtube','twitchtv','movs4ucom','dailymotion','tsiplayer']
        self.PREDEFINED_HOSTS['greek']            = ['youtube','twitchtv','dailymotion']
        self.PREDEFINED_HOSTS['latino']           = ['youtube','twitchtv','dailymotion']
        self.PREDEFINED_HOSTS['italian']          = ['youtube','twitchtv','dailymotion']
        self.PREDEFINED_HOSTS['swedish']          = ['youtube','twitchtv','dailymotion']
        self.PREDEFINED_HOSTS['balkans']          = ['youtube','twitchtv','filma24hdcom','filmativa','filmovizijastudio','dailymotion']
        self.PREDEFINED_HOSTS['music']            = ['youtube','musicbox','musicmp3ru']      
        self.PREDEFINED_HOSTS['others']           = ['youtube','liveleak','twitchtv','dailymotion']
        
        self.LOADED_HOSTS = {}
        self.LOADED_DISABLED_HOSTS = {}
        self.CACHE_HOSTS = {}
        
        self.ADDED_HOSTS = {}
        
        self.hostListFromFolder = None
        self.hostListFromList = None
        
    def _getGroupFile(self, groupName):
        printDBG("IPTVHostsGroups._getGroupFile")
        return GetConfigDir("iptvplayer%sgroup.json" % groupName)
        
    def getLastError(self):
        return self.lastError
        
    def addHostToGroup(self, groupName, hostName):
        printDBG("IPTVHostsGroups.addHostToGroup")
        hostsList = self.getHostsList(groupName)
        self.ADDED_HOSTS[groupName] = []
        if hostName in hostsList or hostName in self.ADDED_HOSTS[groupName]:
            self.lastError = _('This host has been added already to this group.')
            return False
        self.ADDED_HOSTS[groupName].append(hostName)
        return True
        
    def flushAddedHosts(self):
        printDBG("IPTVHostsGroups.flushAddedHosts")
        for groupName in self.ADDED_HOSTS:
            if 0 == len(self.ADDED_HOSTS[groupName]): continue
            newList = list(self.CACHE_HOSTS[groupName])
            newList.extend(self.ADDED_HOSTS[groupName])
            self.setHostsList(groupName, newList)
        self.ADDED_HOSTS = {}
        
    def getGroupsWithoutHost(self, hostName):
        groupList = self.getGroupsList()
        retList = []
        for groupItem in groupList:
            hostsList = self.getHostsList(groupItem.name)
            if hostName not in hostsList and hostName not in self.ADDED_HOSTS.get(groupItem.name, []):
                retList.append(groupItem)
        return retList
        
    def getHostsList(self, groupName):
        printDBG("IPTVHostsGroups.getHostsList")
        if groupName in self.CACHE_HOSTS:
            return self.CACHE_HOSTS[groupName]
    
        if self.hostListFromFolder == None:
            self.hostListFromFolder = GetHostsList(fromList=False, fromHostFolder=True)
        if self.hostListFromList == None: 
            self.hostListFromList = GetHostsList(fromList=True, fromHostFolder=False)
        
        groupFile = self._getGroupFile(groupName)
        self._loadHosts(groupFile, groupName, self.hostListFromFolder, self.hostListFromFolder)
        
        hosts = []
        for host in self.LOADED_HOSTS[groupName]:
            if IsHostEnabled(host):
                hosts.append(host)
        
        for host in self.PREDEFINED_HOSTS.get(groupName, []):
            if host not in hosts and host not in self.LOADED_DISABLED_HOSTS[groupName] and host in self.hostListFromList and host in self.hostListFromFolder and IsHostEnabled(host):
                hosts.append(host)
                
        self.CACHE_HOSTS[groupName] = hosts
        return hosts
        
    def setHostsList(self, groupName, hostsList):
        printDBG("IPTVHostsGroups.setHostsList groupName[%s], hostsList[%s]" % (groupName, hostsList))
        # hostsList - must be updated with host which were not disabled in this group but they are not 
        # available or they are disabled globally
        outObj = {"version":0, "hosts":hostsList, "disabled_hosts":[]}
        
        #check if some host from diabled one has been enabled
        disabledHosts = []
        for host in self.LOADED_DISABLED_HOSTS[groupName]:
            if host not in hostsList:
                disabledHosts.append(host)
        
        # check if some host has been disabled
        for host in self.CACHE_HOSTS[groupName]:
            if host not in hostsList and host in self.PREDEFINED_HOSTS.get(groupName, []):
                disabledHosts.append(host)
        
        outObj['disabled_hosts'] = disabledHosts
        
        self.LOADED_DISABLED_HOSTS[groupName] = disabledHosts
        self.CACHE_HOSTS[groupName] = hostsList
        
        groupFile = self._getGroupFile(groupName)
        return self._saveHosts(outObj, groupFile)
        
    def _saveHosts(self, outObj, groupFile):
        printDBG("IPTVHostsGroups._saveHosts")
        ret = True
        try:
            data = json_dumps(outObj)
            self._saveToFile(groupFile, data)
        except Exception:
            printExc()
            self.lastError = _("Error writing file \"%s\".\n") % self.GROUPS_FILE
            ret = False
        return ret
        
    def _loadHosts(self, groupFile, groupName, hostListFromFolder, hostListFromList):
        printDBG("IPTVHostsGroups._loadHosts groupName[%s]" % groupName)
        predefinedHosts = self.PREDEFINED_HOSTS.get(groupName, [])
        hosts = []
        disabledHosts = []
        
        ret = True
        if os_path.isfile(groupFile):
            try:
                data = self._loadFromFile(groupFile)
                data = json_loads(data)
                for item in data.get('disabled_hosts', []):
                    # we need only information about predefined hosts which were disabled
                    if item in predefinedHosts and item in hostListFromList:
                        disabledHosts.append(str(item))
                
                for item in data.get('hosts', []):
                    if item in hostListFromFolder:
                        hosts.append(item)
            except Exception:
                printExc()
        
        self.LOADED_HOSTS[groupName] = hosts
        self.LOADED_DISABLED_HOSTS[groupName] = disabledHosts
        
    def getGroupsList(self):
        printDBG("IPTVHostsGroups.getGroupsList")
        if self.CACHE_GROUPS != None:
            return self.CACHE_GROUPS
        self._loadGroups()
        groups = list(self.LOADED_GROUPS)
        
        for group in self.PREDEFINED_GROUPS:
            if group not in self.LOADED_GROUPS and group not in self.LOADED_DISABLED_GROUPS:
                groups.append(group)
        
        groupList = []
        for group in groups:
            title = self.PREDEFINED_GROUPS_TITLES.get(group, '')
            if title == '': title = self.LOADED_GROUPS_TITLES.get(group, '')
            if title == '': title = group.title()
            item = CHostsGroupItem(group, _(title))
            groupList.append(item)
        self.CACHE_GROUPS = groupList
        return groupList
        
    def getPredefinedGroupsList(self):
        printDBG("IPTVHostsGroups.getPredefinedGroupsList")
        groupList = []
        for group in self.PREDEFINED_GROUPS: 
            title = self.PREDEFINED_GROUPS_TITLES[group]
            item = CHostsGroupItem(group, title)
            groupList.append(item)
        return groupList
        
    def setGroupList(self, groupList):
        printDBG("IPTVHostsGroups.setGroupList groupList[%s]" % groupList)
        # update disabled groups
        outObj = {"version":0, "groups":[], "disabled_groups":[]}
        
        for group in self.PREDEFINED_GROUPS:
            if group not in groupList:
                outObj['disabled_groups'].append(group)
        
        for group in groupList:
            outObj['groups'].append({'name':group})
            if group in self.LOADED_GROUPS_TITLES:
                outObj['groups']['title'] = self.LOADED_GROUPS_TITLES[group]
                
        return self._saveGroups(outObj)
        
    def _saveGroups(self, outObj):
        printDBG("IPTVHostsGroups._saveGroups")
        ret = True
        try:
            data = json_dumps(outObj)
            self._saveToFile(self.GROUPS_FILE, data)
        except Exception:
            printExc()
            self.lastError = _("Error writing file \"%s\".\n") % self.GROUPS_FILE
            ret = False
        return ret
        
    def _loadGroups(self):
        printDBG("IPTVHostsGroups._loadGroups")
        self.LOADED_GROUPS = []
        self.LOADED_DISABLED_GROUPS = []
        self.LOADED_GROUPS_TITLES = {}
        
        groups = []
        titles = {}
        disabledGroups = []
        
        ret = True
        if os_path.isfile(self.GROUPS_FILE):
            try:
                data = self._loadFromFile(self.GROUPS_FILE)
                data = json_loads(data)
                for item in data.get('disabled_groups', []):
                    # we need only information about predefined groups which were disabled
                    if item in self.PREDEFINED_GROUPS:
                        disabledGroups.append(str(item))
                
                for item in data.get('groups', []):
                    name = str(item['name'])
                    groups.append(name)
                    if 'title' in item: titles[name] = str(item['title'])
            except Exception:
                printExc()
        
        self.LOADED_GROUPS = groups
        self.LOADED_DISABLED_GROUPS = disabledGroups 
        self.LOADED_GROUPS_TITLES = titles
        
    def _saveToFile(self, filePath, data, encoding='utf-8'):
        printDBG("IPTVHostsGroups._saveToFile filePath[%s]" % filePath)
        with codecs.open(filePath, 'w', encoding, 'replace') as fp:
            fp.write(data)
            
    def _loadFromFile(self, filePath, encoding='utf-8'):
        printDBG("IPTVHostsGroups._loadFromFile filePath[%s]" % filePath)
        with codecs.open(filePath, 'r', encoding, 'replace') as fp:
            return fp.read()
        
        
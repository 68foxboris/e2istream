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

from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc

import re
from Components.config import config, ConfigSelection, getConfigListEntry
from Screens.MessageBox import MessageBox

def gettytul():
    return 'E2iStream Info'


class E2iStreamInfo(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history':'E2iStream', 'cookie':'E2iStream.cookie1'})
        self.USER_AGENT = self.cm.getDefaultHeader()['User-Agent']    
        self.HEADER = {'User-Agent': self.USER_AGENT, 'Accept': 'text/html', 'Accept-Encoding':'gzip, deflate', 'Referer':'', 'Origin':''}
        self.defaultParams = {'header':self.HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}
        self.DEFAULT_ICON_URL = 'http://softrix.co.uk/istream/resources/e2istream.png'
        self.import_str    =''    

    def mainCategories(self):
        color='\c00??????'
        # Latest Changes
        title_='Latest Changes'
        img_='http://softrix.co.uk/istream/resources/e2istream.png'
        params = {'category' : 'latest','title':color+title_,'desc':'Whats new in this update?','icon':img_} 
        self.addDir(params)
        # Known Issues    
        title_='Known Issues'
        img_='http://softrix.co.uk/istream/resources/e2istream.png'
        params = {'category' : 'Issues','title':color+title_,'desc':'Known and outstanding issues','icon':img_} 
        self.addDir(params) 
        # Credits   
        title_='Credits / Thanks'
        img_='http://softrix.co.uk/istream/resources/e2istream.png'
        params = {'category' : 'Credits','title':color+title_,'desc':'Talented people helping to keep this project alive.','icon':img_} 
        self.addDir(params)    
        #Contact Details   
        title_='Contact Details'
        img_='http://softrix.co.uk/istream/resources/e2istream.png'
        params = {'category' : 'Contact','title':color+title_,'desc':'How to report a problem?','icon':img_} 
        self.addDir(params)    
    
    def pluginChanges(self):
        desc = 'Whats new in this release.'
        self.addMarker({'title':'24/08/2019 - Fixed several duktape issues.','desc':desc})    
        self.addMarker({'title':'24/08/2019 - Fixed and added back Wiz1 host inside Webstreams.','desc':desc})    
        self.addMarker({'title':'24/08/2019 - Removed those hosts inside Webstreams that no longer exist.','desc':desc})    
        self.addMarker({'title':'24/08/2019 - Disabled some hosts that require fixing in Webstreams.','desc':desc})    
        self.addMarker({'title':'\c0000??00 !!! You need to re-issue the WGET install command if Wiz1 fails to work.','desc':desc})                         
        self.addMarker({'title':'\c0000??00 !!! Please see the support group post for more information. ','desc':desc})                         
        self.addMarker({'title':'\c0000??00 Thanks for your patience while I catch up and move through the list.','desc':desc})                         

    def knownIssues(self):
        desc = 'Known and outstanding issues'
        self.addMarker({'title':'15/08/2019 - HTTPS / IFD Protocol issues? - Update FFMpeg and install PyCurl.','desc':desc})    
        self.addMarker({'title':'\c0000??00 Please avoid reporting missing hosts - they are "missing" for a reason.','desc':desc})    

    def pluginCredits(self):
        desc = 'Several talented people across the internet help directly or indirectly to keep the E2iStream project alive - I would like to personally thank those who continue to contribute in their own way, without your contribution things would take much longer.'
        self.addMarker({'title':'Codermik: https://www.facebook.com/e2iStream/','desc':desc})    
        self.addMarker({'title':'mosz_nowy: https://gitlab.com/iptv-host-xxx/iptv-host-xxx','desc':desc})    
        self.addMarker({'title':'maxbambi (Max): https://gitlab.com/maxbambi','desc':desc})    
        self.addMarker({'title':'\c0000??00 Lets not forget Samsamsam who created the original E2iPlayer addon.','desc':desc})    

    def pluginContact(self):
        desc = 'E2iStream is a continuation of E2iPlayer originally developed by SamSamSam with permission. © E2iStream aka. Codermik, © E2iPlayer aka SamSamSam, © Ricardo Garcia Gonzalez and © youtube-dl developers.  Thank you Samsamsam for all your hard work throughout the years developing and supporting E2iPlayer.  18+ content supplied and maintained by mosz_nowy on his repo: https://gitlab.com/iptv-host-xxx/iptv-host-xxx/'
        self.addMarker({'title':'Codermik','desc':desc})    
        self.addMarker({'title':'Email Address: codermik@tuta.io','desc':desc})    
        self.addMarker({'title':'Facebook Group: https://www.facebook.com/e2iStream/','desc':desc})    
        self.addMarker({'title':'\c0000??00 - Please use the Facebook group for reporting problems -','desc':desc})    
    
    def handleService(self, index, refresh=0, searchPattern='', searchType=''):
        printDBG('handleService start')
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name = self.currItem.get('name', '')
        category = self.currItem.get('category', '')
        printDBG('handleService: | name[%s], category[%s] ' % (name, category))
        self.currList = []
        
        if name == None:
            self.mainCategories()
        elif category == 'latest':
            self.pluginChanges()
        elif category == 'Issues':
            self.knownIssues()
        elif category == 'Credits':
            self.pluginCredits()
        elif category == 'Contact':
            self.pluginContact()
        else:
            printExc()
            
        CBaseHostClass.endHandleService(self, index, refresh)
        return

class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, E2iStreamInfo(), False, [])



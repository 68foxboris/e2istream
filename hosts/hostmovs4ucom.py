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

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, MergeDicts
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs import ph
import urlparse
import re
import urllib

def gettytul():
    return 'http://movs4u.tv/'


class Movs4uCOM(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history': 'movs4u.com',
         'cookie': 'movs4u.com.cookie'})
        self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        self.HEADER = {'User-Agent': self.USER_AGENT,
         'DNT': '1',
         'Accept': 'text/html'}
        self.AJAX_HEADER = dict(self.HEADER)
        self.AJAX_HEADER.update({'X-Requested-With': 'XMLHttpRequest'})
        self.MAIN_URL = 'https://www.movs4u.tv/'
        self.DEFAULT_ICON_URL = self.getFullIconUrl('/wp-content/uploads/2018/03/TcCsO2w.png')
        self.cacheLinks = {}
        self.cacheSeasons = {}
        self.defaultParams = {'header': self.HEADER,
         'use_cookie': True,
         'load_cookie': True,
         'save_cookie': True,
         'cookiefile': self.COOKIE_FILE}
        self.MAIN_CAT_TAB = [{'category': 'list_items',
          'title': _('Movies'),
          'url': self.getFullUrl('/movie/')},
         {'category': 'list_items',
          'title': _('Series'),
          'url': self.getFullUrl('/tvshows/')},
         {'category': 'list_items',
          'title': _('Collections'),
          'url': self.getFullUrl('/collection/')},
         {'category': 'list_filters',
          'title': _('Filters')},
         {'category': 'search',
          'title': _('Search'),
          'search_item': True},
         {'category': 'search_history',
          'title': _('Search history')}]
        self.FILTERS_CAT_TAB = [{'category': 'list_main',
          'title': _('Alphabetically'),
          'tab_id': 'abc'},
         {'category': 'list_main',
          'title': _('Categories'),
          'tab_id': 'categories'},
         {'category': 'list_main',
          'title': _('Genres'),
          'tab_id': 'genres'},
         {'category': 'list_main',
          'title': _('Qualities'),
          'tab_id': 'qualities'},
         {'category': 'list_main',
          'title': _('Releases'),
          'tab_id': 'releases'}]
        self.reLinkData = re.compile('\\sdata\\-([^=]+?)=[\'"]([^\'^"]*?)[\'"]')

    def getPage(self, baseUrl, addParams = {}, post_data = None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        origBaseUrl = baseUrl
        baseUrl = self.cm.iriToUri(baseUrl)
        printDBG('+++> [%s] - > [%s]' % (origBaseUrl, baseUrl))
        addParams['cloudflare_params'] = {'cookie_file': self.COOKIE_FILE,
         'User-Agent': self.USER_AGENT}
        return self.cm.getPageCFProtection(baseUrl, addParams, post_data)

    def listMainItems(self, cItem, nextCategory):
        printDBG('Movs4uCOM.listMainItems')
        me = '</ul>'
        m1 = '<li'
        m2 = '</li>'
        tabID = cItem.get('tab_id', '')
        if tabID == 'categories':
            ms = '>\xd8\xa7\xd9\x86\xd9\x88\xd8\xa7\xd8\xb9 \xd8\xa7\xd9\x81\xd9\x84\xd8\xa7\xd9\x85<'
        elif tabID == 'qualities':
            ms = '>\xd8\xac\xd9\x88\xd8\xaf\xd8\xa7\xd8\xaa \xd8\xa7\xd9\x81\xd9\x84\xd8\xa7\xd9\x85<'
        elif tabID == 'releases':
            ms = '<ul class="releases'
        elif tabID == 'genres':
            ms = '<ul class="genres'
        elif tabID == 'abc':
            ms = '<ul class="abc">'
        else:
            return
        sts, data = self.getPage(self.getMainUrl())
        if not sts:
            return
        data = self.cm.ph.getDataBeetwenMarkers(data, ms, me)[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, m1, m2)
        for item in data:
            url = self.getFullUrl(self.cm.ph.getSearchGroups(item, 'href=[\'"]([^"^\']+?)[\'"]')[0])
            if not self.cm.isValidUrl(url):
                continue
            title = ph.clean_html(item)
            params = dict(cItem)
            params = {'good_for_fav': True,
             'title': title,
             'url': url}
            params['category'] = nextCategory
            self.addDir(params)

    def listItems(self, cItem, nextCategory):
        printDBG('Movs4uCOM.listItems [%s]' % cItem)
        page = cItem.get('page', 1)
        url = cItem['url']
        if page > 1:
            tmp = url.split('?')
            url = tmp[0]
            if url.endswith('/'):
                url = url[:-1]
            url += '/page/%s/' % page
            if len(tmp) > 1:
                url += '?' + '?'.join(tmp[1:])
        sts, data = self.getPage(url)
        if not sts:
            return
        if '/page/{0}/'.format(page + 1) in data:
            nextPage = True
        else:
            nextPage = False
        data = self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'class="content'), ('<div', '>', 'class="fixed-sidebar-blank"'))[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<article', '</article>')
        for item in data:
            url = self.getFullUrl(self.cm.ph.getSearchGroups(item, 'href=[\'"]([^"^\']+?)[\'"]')[0])
            if not self.cm.isValidUrl(url):
                continue
            icon = self.getFullIconUrl(self.cm.ph.getSearchGroups(item, 'src=[\'"]([^"^\']+?)[\'"]')[0])
            title = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(item, '<div class="title">', '</div>')[1])
            if title == '':
                title = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(item, '<h3', '</h3>')[1])
            if title == '':
                title = ph.clean_html(self.cm.ph.getSearchGroups(item, 'alt=[\'"]([^"^\']+?)[\'"]')[0])
            desc = []
            tmp = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(item, '<div class="meta', '</div>')[1].replace('</span>', ' |'))
            if tmp != '':
                desc.append(tmp)
            tmp = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(item, '<span class="quality">', '</span>')[1])
            if tmp != '':
                desc.append(tmp)
            tmp = self.cm.ph.getDataBeetwenMarkers(item, '<div class="genres">', '</div>')[1]
            tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<a', '</a>')
            genres = []
            for t in tmp:
                t = ph.clean_html(t)
                if t != '':
                    genres.append(t)

            desc = ' | '.join(desc)
            if len(genres):
                desc += '[/br]' + ' | '.join(genres)
            tmp = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(item, '<div class="texto"', '</div>')[1])
            if tmp == '':
                tmp = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(item, '<div class="contenido', '</div>')[1])
            if tmp != '':
                desc += '[/br]' + tmp
            params = dict(cItem)
            params = {'good_for_fav': True,
             'title': title,
             'url': url,
             'desc': desc,
             'icon': icon}
            if '/collection/' in item:
                category = 'list_items'
            else:
                category = nextCategory
            params['category'] = category
            self.addDir(params)

        if nextPage and len(self.currList) > 0:
            params = dict(cItem)
            params.update({'title': _('Next page'),
             'page': page + 1})
            self.addDir(params)

    def exploreItem(self, cItem, nextCategory = ''):
        printDBG('Movs4uCOM.exploreItem')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        self.setMainUrl(self.cm.meta['url'])
        mainDesc = ph.clean_html(self.cm.ph.getDataBeetwenReMarkers(data, re.compile('<div[^>]+?class="wp-content"[^>]*?>'), re.compile('</div>'))[1])
        mainIcon = self.cm.ph.getDataBeetwenMarkers(data, '<div class="poster"', '</div>')[1]
        mainIcon = self.getFullIconUrl(self.cm.ph.getSearchGroups(mainIcon, '<img[^>]+?src=[\'"]([^"^\']+?\\.jpe?g[^"^\']*?)["\']')[0])
        if mainIcon == '':
            mainIcon = cItem.get('icon', '')
        tmp = ph.find(data, ('<li', '>', 'trailer'), '</li>')[1]
        linkData = self.reLinkData.findall(tmp)
        if linkData:
            linkData = dict(linkData)
            url = strwithmeta(cItem['url'] + '#_%s' % linkData, {'link_data': linkData})
            title = ph.clean_html(tmp)
            title = '%s - %s' % (cItem['title'], title)
            self.addVideo(MergeDicts(cItem, {'good_for_fav': False,
             'title': title,
             'prev_title': cItem['title'],
             'url': url,
             'prev_url': cItem['url'],
             'prev_desc': cItem.get('desc', ''),
             'icon': mainIcon,
             'desc': mainDesc}))
        tmp = ph.find(data, ('<div', '>', 'trailer'), '</div>', flags=0)[1]
        url = self.getFullUrl(ph.search(tmp, ph.IFRAME)[1])
        if 1 == self.up.checkHostSupport(url):
            title = ph.clean_html(tmp)
            title = '%s - %s' % (cItem['title'], title)
            self.addVideo(MergeDicts(cItem, {'good_for_fav': False,
             'title': title,
             'prev_title': cItem['title'],
             'url': url,
             'prev_url': cItem['url'],
             'prev_desc': cItem.get('desc', ''),
             'icon': mainIcon,
             'desc': mainDesc}))
        mainTitle = ph.clean_html(self.cm.ph.getSearchGroups(data, '<meta[^>]+?itemprop=[\'"]name[\'"][^>]+?content=[\'"]([^"^\']+?)[\'"]')[0])
        if mainTitle == '':
            mainTitle = cItem['title']
        self.cacheLinks = {}
        reObj = re.compile('<div[^>]+?numerando[^>]+?>\\s*([0-9]+)\\s*\\-\\s*([0-9]+)\\s*</div>')
        if '/tvshows/' in cItem['url']:
            self.cacheSeasons = {}
            sKey = 0
            data = ph.findall(data, ('<div', '>', 'se-c'), '</ul>', flags=0)
            for sItem in data:
                sTtile = ph.clean_html(ph.find(sItem, ('<span', '>', 'title'), '<i>', flags=0)[1])
                sNum = ph.clean_html(ph.find(sItem, ('<span', '>', 'se-t'), '</span>', flags=0)[1])
                sDate = ph.clean_html(ph.find(sItem, ('<i', '>'), '</i>', flags=0)[1])
                sRating = ph.clean_html(ph.find(sItem, ('<div', '>', 'se_rating'), '</div>', flags=0)[1])
                episodesList = []
                sItem = ph.findall(sItem, ('<li', '>'), '</li>', flags=0)
                for item in sItem:
                    url = self.getFullUrl(ph.search(item, ph.A)[1])
                    icon = self.getFullIconUrl(ph.search(item, ph.IMG)[1])
                    if icon == '':
                        icon = mainIcon
                    title = ph.clean_html(ph.find(item, ('<div', '>', 'episodiotitle'), '</a>', flags=0)[1])
                    date = ph.clean_html(ph.find(item, ('<span', '>', 'date'), '</span>', flags=0)[1])
                    tmp = ph.search(item, reObj)
                    title = '%s s%se%s - %s' % (cItem['title'],
                     tmp[0].zfill(2),
                     tmp[1].zfill(2),
                     title)
                    desc = []
                    if date != '':
                        desc.append(date)
                    desc = ' | '.join(desc)
                    if desc != '':
                        desc += '[/br]'
                    desc += mainDesc
                    params = {'title': title,
                     'url': url,
                     'icon': icon,
                     'desc': desc}
                    episodesList.append(params)

                if len(episodesList):
                    self.cacheSeasons[sKey] = episodesList
                    desc = []
                    if sDate != '':
                        desc.append(sDate)
                    if sRating != '':
                        desc.append(sRating)
                    desc = ' | '.join(desc)
                    if desc != '':
                        desc += '[/br]'
                    desc += mainDesc
                    params = dict(cItem)
                    params.update({'good_for_fav': False,
                     'category': nextCategory,
                     'title': sTtile,
                     's_key': sKey,
                     'prev_title': mainTitle,
                     'url': url,
                     'prev_url': cItem['url'],
                     'prev_desc': cItem.get('desc', ''),
                     'icon': icon,
                     'desc': desc})
                    self.addDir(params)
                    sKey += 1

        else:
            self.addVideo(MergeDicts(cItem, {'good_for_fav': True,
             'title': mainTitle,
             'icon': mainIcon,
             'desc': mainDesc}))

    def listEpisodes(self, cItem):
        printDBG('Movs4uCOM.listEpisodes')
        sKey = cItem.get('s_key', -1)
        episodesList = self.cacheSeasons.get(sKey, [])
        for item in episodesList:
            params = dict(cItem)
            params.update(item)
            params.update({'good_for_fav': True})
            self.addVideo(params)

    def listSearchResult(self, cItem, searchPattern, searchType):
        printDBG('Movs4uCOM.listSearchResult cItem[%s], searchPattern[%s] searchType[%s]' % (cItem, searchPattern, searchType))
        cItem = dict(cItem)
        cItem['url'] = self.getFullUrl('/?s=' + urllib.quote_plus(searchPattern))
        self.listItems(cItem, 'explore_item')

    def getLinksForVideo(self, cItem):
        printDBG('Movs4uCOM.getLinksForVideo [%s]' % cItem)
        retTab = []
        if 1 == self.up.checkHostSupport(cItem.get('url', '')):
            videoUrl = cItem['url'].replace('youtu.be/', 'youtube.com/watch?v=')
            return self.up.getVideoLinkExt(videoUrl)
        if '#_' in cItem['url']:
            return [{'name': 'single',
              'url': cItem['url'],
              'need_resolve': 1}]
        cacheTab = self.cacheLinks.get(cItem['url'], [])
        if len(cacheTab):
            return cacheTab
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        data = ph.find(data, ('<ul', '>', 'playeroptionsul'), '</ul>', flags=0)[1]
        data = ph.findall(data, ('<li', '>'), '</li>', flags=ph.START_S)
        for idx in range(1, len(data), 2):
            if 'trailer' in data[idx - 1]:
                printDBG('SKIPP trailer link: %s' % data[idx - 1])
                continue
            linkData = self.reLinkData.findall(data[idx - 1])
            name = ph.clean_html(data[idx])
            if linkData:
                linkData = dict(linkData)
                url = strwithmeta(cItem['url'] + '#_%s' % linkData, {'link_data': linkData})
                retTab.append({'name': name,
                 'url': url,
                 'need_resolve': 1})

        if retTab:
            self.cacheLinks[cItem['url']] = retTab
        return retTab

    def getVideoLinks(self, videoUrl):
        printDBG('Movs4uCOM.getVideoLinks [%s]' % videoUrl)
        videoUrl = strwithmeta(videoUrl)
        urlTab = []
        orginUrl = str(videoUrl)
        if len(self.cacheLinks.keys()):
            for key in self.cacheLinks:
                for idx in range(len(self.cacheLinks[key])):
                    if videoUrl in self.cacheLinks[key][idx]['url']:
                        if not self.cacheLinks[key][idx]['name'].startswith('*'):
                            self.cacheLinks[key][idx]['name'] = '*' + self.cacheLinks[key][idx]['name']
                        break

        if '#_' in videoUrl:
            post_data = MergeDicts(videoUrl.meta['link_data'], {'action': 'doo_player_ajax'})
            if 'url' in post_data:
                post_data['curl'] = post_data.pop('url')
            url = self.getFullUrl('/wp-admin/admin-ajax.php')
            sts, data = self.getPage(url, post_data=post_data)
            if not sts:
                return urlTab
            tmp = ph.IFRAME.findall(data)
            for item in tmp:
                url = self.getFullUrl(item[1])
                if 1 == self.up.checkHostSupport(url):
                    urlTab.extend(self.up.getVideoLinkExt(url))
                else:
                    printDBG('>> SKIPPED: %s' % url)

            return urlTab
        sts, data = self.cm.getPage(videoUrl, self.defaultParams)
        videoUrl = self.cm.meta.get('url', videoUrl)
        if self.up.getDomain(self.getMainUrl()) in videoUrl or self.up.getDomain(videoUrl) == self.up.getDomain(orginUrl):
            if not sts:
                return []
            found = False
            printDBG(data)
            tmp = re.compile('<iframe[^>]+?src=[\'"]([^"^\']+?)[\'"]', re.IGNORECASE).findall(data)
            for url in tmp:
                if 1 == self.up.checkHostSupport(url):
                    videoUrl = url
                    found = True
                    break

            if not found or 'flashx' in videoUrl:
                tmp = self.cm.ph.getAllItemsBeetwenMarkers(data, 'embedFrame', '</a>')
                for urlItem in tmp:
                    url = self.cm.ph.getSearchGroups(urlItem, 'href=[\'"](https?://[^\'^"]+?)[\'"]')[0]
                    if 1 == self.up.checkHostSupport(url):
                        videoUrl = url
                        found = True
                        break

        if self.cm.isValidUrl(videoUrl):
            urlTab = self.up.getVideoLinkExt(videoUrl)
        return urlTab

    def getArticleContent(self, cItem):
        printDBG('Movs4uCOM.getArticleContent [%s]' % cItem)
        retTab = []
        otherInfo = {}
        url = cItem.get('prev_url', '')
        if url == '':
            url = cItem.get('url', '')
        sts, data = self.getPage(url)
        if not sts:
            return retTab
        title = ph.clean_html(self.cm.ph.getSearchGroups(data, '<meta[^>]+?itemprop="name"[^>]+?content="([^"]+?)"')[0])
        icon = self.cm.ph.getDataBeetwenMarkers(data, '<div id="poster"', '</div>')[1]
        icon = self.getFullIconUrl(self.cm.ph.getSearchGroups(icon, '<img[^>]+?src=[\'"]([^"^\']+?\\.jpe?g[^"^\']*?)["\']')[0])
        desc = ph.clean_html(self.cm.ph.getDataBeetwenReMarkers(data, re.compile('<div[^>]+?class="wp-content"[^>]*?>'), re.compile('</div>'))[1])
        mapDesc = {'Original title': 'alternate_title',
         'IMDb Rating': 'imdb_rating',
         'TMDb Rating': 'tmdb_rating',
         'Status': 'status',
         'Firt air date': 'first_air_date',
         'Last air date': 'last_air_date',
         'Seasons': 'seasons',
         'Episodes': 'episodes'}
        tmp = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="custom_fields">', '</div>')
        for item in tmp:
            item = item.split('<span class="valor">')
            if len(item) < 2:
                continue
            marker = ph.clean_html(item[0])
            key = mapDesc.get(marker, '')
            if key == '':
                continue
            value = ph.clean_html(item[1])
            if value != '':
                otherInfo[key] = value

        mapDesc = {'Director': 'directors',
         'Cast': 'cast',
         'Creator': 'creators'}
        tmp = self.cm.ph.getDataBeetwenReMarkers(data, re.compile('<div id="cast"[^>]+?>'), re.compile('fixidtab'))[1]
        tmp = self.cm.ph.rgetAllItemsBeetwenMarkers(tmp, '</div>', '<h2>')
        for item in tmp:
            marker = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(item, '<h2', '</h2>')[1])
            key = mapDesc.get(marker, '')
            if key == '':
                continue
            item = self.cm.ph.getAllItemsBeetwenMarkers(item, '<div class="name">', '</div>')
            value = []
            for t in item:
                t = ph.clean_html(t)
                if t != '':
                    value.append(t)

            if len(value):
                otherInfo[key] = ', '.join(value)

        key = 'genres'
        tmp = self.cm.ph.getDataBeetwenMarkers(data, '<div class="sgeneros">', '</div>')[1]
        tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<a', '</a>')
        value = []
        for t in tmp:
            t = ph.clean_html(t)
            if t != '':
                value.append(t)

        if len(value):
            otherInfo[key] = ', '.join(value)
        tmp = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(data, '<div class="starstruck-rating">', '</div>')[1])
        if tmp != '':
            otherInfo['rating'] = tmp
        tmp = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(data, '<span class="qualityx">', '</span>')[1])
        if tmp != '':
            otherInfo['quality'] = tmp
        tmp = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(data, '<span class="country">', '</span>')[1])
        if tmp != '':
            otherInfo['country'] = tmp
        tmp = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(data, '<span class="runtime">', '</span>')[1])
        if tmp != '':
            otherInfo['duration'] = tmp
        if title == '':
            title = cItem['title']
        if desc == '':
            desc = cItem.get('desc', '')
        if icon == '':
            icon = cItem.get('icon', self.DEFAULT_ICON_URL)
        return [{'title': ph.clean_html(title),
          'text': ph.clean_html(desc),
          'images': [{'title': '',
                      'url': self.getFullUrl(icon)}],
          'other_info': otherInfo}]

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name = self.currItem.get('name', '')
        category = self.currItem.get('category', '')
        mode = self.currItem.get('mode', '')
        printDBG('handleService: |||||||||||||||||||||||||||||||||||| name[%s], category[%s] ' % (name, category))
        self.currList = []
        if name == None:
            self.cacheLinks = {}
            self.listsTab(self.MAIN_CAT_TAB, {'name': 'category'})
        elif category == 'list_filters':
            self.listsTab(self.FILTERS_CAT_TAB, self.currItem)
        elif category == 'list_main':
            self.listMainItems(self.currItem, 'list_items')
        elif category == 'list_items':
            self.listItems(self.currItem, 'explore_item')
        elif category == 'explore_item':
            self.exploreItem(self.currItem, 'list_episodes')
        elif category == 'list_episodes':
            self.listEpisodes(self.currItem)
        elif category in ('search', 'search_next_page'):
            cItem = dict(self.currItem)
            cItem.update({'search_item': False,
             'name': 'category'})
            self.listSearchResult(cItem, searchPattern, searchType)
        elif category == 'search_history':
            self.listsHistory({'name': 'history',
             'category': 'search'}, 'desc', _('Type: '))
        else:
            printExc()
        CBaseHostClass.endHandleService(self, index, refresh)


class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, Movs4uCOM(), True, [])

    def withArticleContent(self, cItem):
        if cItem['type'] == 'video' and '/episodes/' not in cItem['url'] or cItem['category'] == 'explore_item':
            return True
        return False

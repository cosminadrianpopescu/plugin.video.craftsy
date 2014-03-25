import os
import re
import string
import sys
import md5
from json import JSONDecoder
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net

class CraftsyPlugin():
    addon = None
    net = None
    logo = None
    profile_path = None
    cookie_file = None
    base_url = None
    free_url = 'http://www.craftsy.com.edgesuite.net/'
    pay_url = 'http://cd1.craftsy.com/'

    def __init__(self):
        self.addon = Addon('plugin.video.craftsy', sys.argv)
        self.net = Net()

        self.logo = os.path.join(self.addon.get_path(), 'art','logo.jpg')

        self.profile_path = self.addon.get_profile()
        self.cookie_file = os.path.join(self.profile_path, 'craftsy.cookies')

        try:
            os.makedirs(os.path.dirname(self.cookie_file))
        except OSError:
            pass

        self.net.set_cookies(self.cookie_file)
        self.base_url = 'http://www.craftsy.com'

    def __get_image(self, url):
        fname = os.path.join(self.profile_path, md5.new(url).digest())
        print fname
        if os.path.isfile(fname):
            return fname
        return url

    def __check_link(self, url):
        if (re.match('^/', url)):
            return 'http:' + url
        return url

    def __fetch_regexp_idx(self, r, idx, default = None):
        if (r == None):
            return default
        if (len(r.groups()) < idx + 1):
            return default

        return r.groups()[idx]

    def check_login(self):
        source = self.net.http_GET(self.base_url + '/my/home?NAVIGATION_PAGE_CONTEXT_ATTR=NONE').content
        r = re.search('<title>([^<]+)</title>', source)
        title = r.groups()[0]
        
        if title == 'Welcome Back to Craftsy!':
            return False
        return True

    def __get_url(self, url):
        return self.net.http_GET(url).content.encode('utf8').replace("\n", "").replace("\r", "")

    def add_classes(self):
        source = self.__get_url(self.base_url + '/my/home?NAVIGATION_PAGE_CONTEXT_ATTR=NONE')
        source = re.sub('<div class="classCard mostRecent".*?</div>.*?</div>.*?</div>.*?</div>', '', source)
        source = re.sub('<div class="continueArea".*?</div>.*?</div>', '', source)
        # parts = re.split('<div class="classBot myClassBot">', source)
        r = re.findall('<a href="(/lecture[^\"]+)"(.*?)</a>[ \s\t]*<div class="classBot myClassBot">.*?<a href="([^"]+)"', source)
        for i in r:
            url = i[2]
            if (re.match('^/', url)):
                url = self.base_url + url
            t = re.search('<h4>([^<]+)</h4>', i[1])
            title = 'N/A'
            title = self.__fetch_regexp_idx(t, 0, 'N/A')
            img = self.base_url + '/images/craftsy/noImageTitleCard.png'
            t = re.search('<img src="([^"]+)" alt="[^"]+" onerror', i[1])
            _u = self.__fetch_regexp_idx(t, 0)
            if (_u != None):
                img = self.__check_link(_u)

            # print self.__get_image(img)
            self.addon.add_directory({'mode': 'classes', 'url': url}, {'title': title}, fanart=img, img=img)

    def __try_resolve(self, pattern, video):
        r = re.search(pattern, video)
        return self.__fetch_regexp_idx(r, 0)

    def resolve_url(self, lesson_url):
        pattern = '&([0-9]+)&(pay|free)$'
        l = re.search(pattern, lesson_url)
        lesson_id = self.__fetch_regexp_idx(l, 0)
        lesson_type = self.__fetch_regexp_idx(l, 1, 'pay')
        lesson_url = re.sub(pattern, '', lesson_url)

        q = self.addon.get_setting('quality')
        t = self.addon.get_setting('type')

        source = self.__get_url(lesson_url)

        uid = re.search('/([0-9]+)\\.html(\\?t=[0-9]*){0,1}$', lesson_url)
        url_id = self.__fetch_regexp_idx(uid, 0)
        if (url_id == None):
            return None

        r = re.search('arbitraryId = ([0-9]+),', source)
        arbitraryId = self.__fetch_regexp_idx(r, 0)
        if (arbitraryId != None):
            url_id = arbitraryId

        suffix = lesson_id + '/' + url_id + '/' + url_id + '-' + q + '.' + t
        if lesson_type == 'free':
            print "THE URL TO PLAY IS " + self.free_url + suffix
            return self.free_url + suffix
        else:
            return self.pay_url + suffix

        # r = re.search('(<video.*?</video>)', source)

        # if (len(r.groups()) == 0):
        #     return None
        # else:
        #     video = r.groups()[0]
        #     video_url = self.__try_resolve('<source src="([^"]+-' + q + '\\.' + t + ')"', video)
        #     if (video_url == None):
        #         video_url = self.__try_resolve('<source src="([^"]+-' + q + '\\.[^\\.]+)"', video)
        #         if (video_url == None):
        #             video_url = self.__try_resolve('<source src="([^"]+)"', video)

        #     return video_url


    def add_lessons(self, class_url):
        source = self.__get_url(class_url) # self.net.http_GET(class_url).content
        l = re.search('\,([0-9]+)$', class_url)
        lesson_id = self.__fetch_regexp_idx(l, 0)
        if (lesson_id == None):
            self.addon.show_error_dialog(['Could not fetch the lesson ID']);
            return None
        r = re.findall('(<tr class="classLesson.*?</tr>)', source)
        first = True
        lesson_type = 'pay'
        for i in r:
            text = i 
            el = re.search('<td class="lessonName">.*?<a href="([^"]+)">(.*?)</a>', text)
            href = self.__fetch_regexp_idx(el, 0)
            if href != None:
                href = self.__check_link(href)
                title = self.__fetch_regexp_idx(el, 1, 'N/A')
                if (first):
                    if (title.lower() == 'welcome to your free mini-class!'):
                        lesson_type = 'free'
                im = re.search('<td class="lessonImage">.*?<img src="([^"]+)"', text)
                img = self.__check_link(self.__fetch_regexp_idx(im, 0, os.path.join(self.addon.get_path(), 'art','no-img.jpg')))

                self.addon.add_video_item({'url': href + '&' + lesson_id + '&' + lesson_type}, {'title': title}, img = img, fanart = img)
            first = False

    def do_login(self):
        try:
            if self.check_login():
                return True
            data=(('email', self.addon.get_setting('username')), ('password', self.addon.get_setting('password')), ('forwardUrl', '/'))
            source = self.net.http_POST(self.base_url + '/doLogin.json?isCraftsyAjax=true', data).content
            response = JSONDecoder().decode(source)
            self.net.save_cookies(self.cookie_file)
            self.net.set_cookies(self.cookie_file)
            return response.get("success")
        except Exception as e:
            print e
            return False
            

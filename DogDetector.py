import urllib2 as urllib2
import re as re
import Tkinter
import tkMessageBox
from threading import Timer

URL_HOST = 'http://www.wolai66.com'
URL_SEARCH = '/search_results?key=%E4%BA%AC%E4%B8%9CE%E5%8D%A1'
UA_CHROME = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'
DETECT_FREQUENCY = 3600  # 1 hour


def get_url(path):
    return '{0}{1}'.format(URL_HOST, path)


def http_get(url):
    request = urllib2.Request(url=get_url(url), headers={'User-Agent': UA_CHROME})
    response = urllib2.urlopen(request)
    return response.read()


def fetch_dog_list():
    # fetch list web
    data = http_get(URL_SEARCH)

    # find list data area for speed up
    pattern = re.compile('[\s\S]*?<div class="search_result_items">([\s\S]*?)<script>function fn_page_turning[\s\S]*?')
    result = pattern.match(data)
    data = result.group(1)

    # parse the item info
    pattern = re.compile('[\s\S]*?<p class="desc"><a href="(.+?)" target="_blank">(.+?)</a></p>')
    result = pattern.findall(data)
    items = []
    for item in result:
        items.append({'url': item[0], 'name': item[1]})
    return items


def fetch_dog_detail(item):
    data = http_get(item['url'])
    pattern_detail = re.compile('[\s\S]*?<input id="current_pro_inventory_quantity" name="\xe5\xba\x93\xe5\xad\x98\xe9\x87\x8f" type="hidden" value="(\d+?)" />[\s\S]*?')
    result = pattern_detail.match(data)
    item['count'] = int(result.group(1))
    return item


def show_dog_detected_msg(msg):
    top = Tkinter.Tk()
    top.withdraw()  # hide window
    tkMessageBox.showinfo('Dog detected!', msg)


def detect_dog():
    print ('Fetch item list ...')
    dog_list = fetch_dog_list()

    print ('Fetch item detail')
    detected = False
    msg = ''
    for item in dog_list:
        i = fetch_dog_detail(item)
        if i['count'] > 0:
            detected = True

        if msg == '':
            msg = u'{0}: {1}'.format(unicode(i['name'], 'utf8'), i['count'])
        else:
            msg = u'{0}\n{1}: {2}'.format(msg, unicode(i['name'], 'utf8'), i['count'])

    # notify
    if detected:
        print ('====> Detected!')
        print (msg)
        show_dog_detected_msg(msg)
    else:
        print ('====> Not detected!')
        print (msg)


def main():
    detect_dog()

    print ('Scheduler next detect after {0} seconds...'.format(DETECT_FREQUENCY))
    Timer(DETECT_FREQUENCY, main).start()

if __name__ == "__main__":
    main()

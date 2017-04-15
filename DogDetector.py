import urllib2 as urllib2
import re as re
import Tkinter
import tkMessageBox
from threading import Timer

URL_HOST = 'http://www.wolai66.com'
URL_SEARCH = ('/search_results?key=\xe4\xba\xac\xe4\xb8\x9cE\xe5\x8d\xa1',
              '/search_results?key=\xe5\xa4\xa9\xe7\x8b\x97\xe8\xb4\xad\xe7\x89\xa9\xe5\x8d\xa1')
UA_CHROME = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'
DETECT_FREQUENCY = 3600  # 1 hour


def get_url(path):
    return '{0}{1}'.format(URL_HOST, path)


def http_get(url):
    request = urllib2.Request(url=get_url(url), headers={'User-Agent': UA_CHROME})
    response = urllib2.urlopen(request)
    return response.read()


def fetch_dog_list():
    pattern_area = re.compile(
        '[\s\S]*?<div\s+class="search_result_items"\s*>([\s\S]*?)<script>\s*function fn_page_turning[\s\S]*?')
    pattern_item = re.compile(
        '[\s\S]*?<p class="desc">\s*<a\s+href\s*=\s*"(.+?)"\s+target\s*=\s*"_blank"\s*>(.+?)</a>\s*</p>')
    items = []

    for url in URL_SEARCH:
        # fetch list web
        data = http_get(url)

        # find list data area for speed up
        result = pattern_area.match(data)
        data = result.group(1)

        # parse the item info
        result = pattern_item.findall(data)

        # make result for return
        for item in result:
            items.append({'url': item[0], 'name': item[1]})

    return items


def fetch_dog_detail(item):
    data = http_get(item['url'])
    pattern_detail = re.compile(
        '[\s\S]*?id\s*=\s*"current_prov_sku_price"[^>]*?value\s*=\s*"([.\d]+?)"\s+/>[\s\S]*?id\s*=\s*"current_pro_inventory_quantity"[^>]*?value\s*=\s*"(\d+?)"\s*/>[\s\S]*?')
    result = pattern_detail.match(data)
    item['price'] = float(result.group(1))
    item['count'] = int(result.group(2))
    return item


def show_dog_detected_msg(msg):
    top = Tkinter.Tk()
    top.withdraw()  # hide window
    tkMessageBox.showinfo('Dog detected!', msg)


def get_item_string(item):
    return u'{0} [\xa5{2}]: {1} '.format(unicode(item['name'], 'utf8'), item['count'], item['price'])


def detect_dog():
    print ('Fetch item list ...')
    dog_list = fetch_dog_list()

    print ('Fetch item detail')
    detected = False
    str_items = []
    for item in dog_list:
        i = fetch_dog_detail(item)
        if i['count'] > 0:
            detected = True

        # add item string
        str_items.append(get_item_string(i))

    # notify
    msg = '\n'.join(str_items)
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

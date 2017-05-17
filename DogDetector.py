# coding=utf-8

import urllib2 as urllib2
import re as re
import Tkinter
import tkMessageBox
from threading import Timer
import smtplib
from email.mime.text import MIMEText

# host of the website
URL_HOST = 'http://www.wolai66.com'

# url for search. script will parser list from the search list
URL_SEARCH = ('/search_results?key=京东E卡',
              '/search_results?key=天狗购物卡')

# Extra url of items to detect
URL_EXTRA_ITEM = ('/commodity?code=10171476858',  # 企业专属JD卡（电子）
                  '/commodity?code=17206586167')  # 100 兑 100

# Except urls
URL_EXCEPT_ITEM = ('/commodity?code=10173427204', # 京东E卡300元+哈根达斯100元
                   )

# User Agent
UA_CHROME = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0)' \
            ' AppleWebKit/535.11 (KHTML, like Gecko)' \
            ' Chrome/17.0.963.56 Safari/535.11'

# frequency
DETECT_FREQUENCY = 600  # 10 minutes

# mail
MAIL_HOST = 'smtp.zoho.com.cn'  # 设置服务器
MAIL_PORT = 465
MAIL_USER = 'dog_detector@zoho.com.cn'  # 用户名
MAIL_PASS = 'dogdogdog'      # 口令
MAIL_POSTFIX = 'zoho.com.cn'  # 发件箱的后缀
MAIL_FROM = 'dog_detector@zoho.com.cn'
MAIL_TO = ['fan.hu@t2mobile.com',
           'qiang.liu@tcl.com',
           'luyan.ding@tcl.com',
           'huidan.chai@tcl.com',
           'panyue.xu@tcl.com']


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
        '[\s\S]*?<p class="desc">\s*<a\s+href\s*=\s*"(.+?)"')
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
            if item not in URL_EXCEPT_ITEM:  # remove except urls
                items.append({'url': item})

    # append extra item list
    for item in URL_EXTRA_ITEM:
        items.append({'url': item})

    return items


def fetch_dog_detail(item):
    data = http_get(item['url'])
    pattern_detail = re.compile(
        '[\s\S]*?id\s*=\s*"current_prov_sku_price"[^>]*?value\s*=\s*"([.\d]+?)"\s+/>'
        '[\s\S]*?id\s*=\s*"current_pro_inventory_quantity"[^>]*?value\s*=\s*"(\d+?)"\s*/>'
        '[\s\S]*?class\s*=\s*"tb_title">\s*<h3>\s*(.*?)\s*</h3>'
        '[\s\S]*?')
    result = pattern_detail.match(data)
    item['price'] = float(result.group(1))
    item['count'] = int(result.group(2))
    item['name'] = result.group(3)
    return item


def show_dog_detected_msg(dog_list):
    str_items = []
    for item in dog_list:
        # add item string
        str_item = get_item_string(item)
        str_items.append(str_item)
        print(unicode(str_item, 'utf-8'))

    # generate message
    msg = '\n'.join(str_items)

    top = Tkinter.Tk()
    top.withdraw()  # hide window
    tkMessageBox.showinfo('Dog found!', msg)


def get_item_string(item):
    return '{0} [￥{2}]: {1} '.format(item['name'], item['count'], item['price'])


def get_item_email_string(item):
    return '<div><a href="{0}{1}">{2}</a> [￥{4}]: {3}</div>'.format(URL_HOST, item['url'], item['name'], item['count'], item['price'])


def send_dog_detected_email(dog_list):
    str_items = []
    for item in dog_list:
        # add item string
        str_item = get_item_email_string(item)
        str_items.append(str_item)

    # generate message
    msg = '\n'.join(str_items)

    # send email
    msg = MIMEText(msg, _subtype='html', _charset='gb2312')
    msg['Subject'] = 'Dog detected! Go and catch them!!'
    msg['From'] = MAIL_FROM
    msg['To'] = ';'.join(MAIL_TO)
    try:
        server = smtplib.SMTP_SSL(host=MAIL_HOST, port=MAIL_PORT)
        server.login(MAIL_USER, MAIL_PASS)
        server.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())
        server.close()
    except Exception, e:
        print str(e)


def on_dog_detected(dog_list):
    # show_dog_detected_msg(dog_list)
    send_dog_detected_email(dog_list)


def detect_dog():
    print ('Fetch item list ...')
    dog_list = fetch_dog_list()

    print ('Fetch item detail')
    detected = False
    for item in dog_list:
        if fetch_dog_detail(item)['count'] > 0:
            detected = True
        print(unicode(get_item_string(item), 'utf-8'))

    # notify
    if detected:
        print ('====> Hurry up! Catch the dog!!!')
        on_dog_detected(dog_list)
    else:
        print ('====> No dog found, wash wash sleep...')


def main():
    detect_dog()

    print ('Scheduler next detect after {0} seconds...'.format(DETECT_FREQUENCY))
    Timer(DETECT_FREQUENCY, main).start()


if __name__ == "__main__":
    main()

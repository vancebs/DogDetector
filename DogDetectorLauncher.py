import os
import urllib2

LOCAL_DIR = '{0}/.DogDetector'.format(os.path.expanduser('~'))
LOCAL_FILE_VERSION = '{0}/{1}'.format(LOCAL_DIR, 'version')
LOCAL_FILE_DOG_DETECTOR = '{0}/{1}'.format(LOCAL_DIR, 'DogDetector.py')

# User Agent
UA_CHROME = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0)' \
            ' AppleWebKit/535.11 (KHTML, like Gecko)' \
            ' Chrome/17.0.963.56 Safari/535.11'

# VERSION URL
URL_VERSION = 'https://raw.githubusercontent.com/vancebs/DogDetector/master/version'

# DogDetector.py URL
URL_DOG_DETECTOR = 'https://raw.githubusercontent.com/vancebs/DogDetector/master/DogDetector.py'


def http_get(url):
    request = urllib2.Request(url=url, headers={'User-Agent': UA_CHROME})
    response = urllib2.urlopen(request)
    return response.read()

if __name__ == "__main__":
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)
    elif not os.path.isdir(LOCAL_DIR):
        print ('Failed to create {0}'.format(LOCAL_DIR))
        exit(1)

    # get local version
    last_version = ''
    if os.path.exists(LOCAL_FILE_VERSION) and os.path.isfile(LOCAL_FILE_VERSION):
        f = file(LOCAL_FILE_VERSION)
        last_version = f.readline()
        f.close()

    # get remote version
    version = http_get(URL_VERSION)

    # update DogDetector.py if version not same
    if last_version != version:
        print ('new version detected. updating...')
        fail = False

        # update DogDetector.py
        try:
            f = file(LOCAL_FILE_DOG_DETECTOR, mode='w+')
            f.write(http_get(URL_DOG_DETECTOR))
            f.flush()
            f.close()
        except Exception, e:
            fail = True
            print ('update DogDetector.py failed!')
            print Exception, ":", e

        # save last version
        try:
            f = file(LOCAL_FILE_VERSION, mode='w+')
            f.write(version)
            f.close()
        except Exception, e:
            fail = True
            print ('update version failed!')
            print Exception, ":", e

        if fail:
            print ('Update failed. Try with old script.')
        else:
            print ('Update success.')
    else:
        print ('Already update to date.')

    # run DogDetector
    import sys
    sys.path.append(LOCAL_DIR)
    import DogDetector
    DogDetector.main()

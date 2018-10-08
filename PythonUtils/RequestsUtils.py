#!/usr/bin/env python


import numpy # Hint to PyInstaller
import cv2
import requests
import sys


# Spoof a browser's User-Agent string.
# Otherwise, some sites will reject us as a bot.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0'
}

def validateResponse(response):
    statusCode = response.status_code
    if statusCode == 200:
        return True
    url = response.request.url
    sys.stderr.write(
            'Received unexpected status code (%d) when requesting %s\n' % \
            (statusCode, url))
    return False

def cvImageFromUrl(url):
    response = requests.get(url, headers=HEADERS)
    if not validateResponse(response):
        return None
    imageData = numpy.fromstring(response.content, numpy.uint8)
    image = cv2.imdecode(imageData, cv2.IMREAD_COLOR)
    if image is None:
        sys.stderr.write(
                'Failed to decode image from content of %s\n' % url)
    return image


def main():
    image = cvImageFromUrl('http://nummist.com/images/ceiling.gaze.jpg')
    if image is not None:
        cv2.imwrite('image.png', image)

if __name__ == '__main__':
    main()

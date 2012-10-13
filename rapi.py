"""
rapi.py - Rhapsody API
Unofficial API for obtaining metadata and streams for http://www.rhapsody.com
"""

import urllib
import urllib2
import xml.etree.ElementTree as ET

_login_url = "https://playback.rhapsody.com/login.xml"

class Session:
    """
    Caches information about the user currently logged in
    """

    cobrandId = ""
    token = ""
    userGuid = ""

    def __init__(self, cobrandId, token, userGuid):
        self.cobrandId = cobrandId
        self.token = token
        self.userGuid = userGuid

def log_in(username, password):
    """
    Opens a session with Rhapsody's API sever, using the supplied user
    credentials. Returns a rapi.Session containing user information, which
    is required by several rapi calls
    """
    data = urllib.urlencode({
        'username': username,
        'password': password,
    })

    req = urllib2.Request(_login_url, data)
    res = urllib2.urlopen(req)
    xml = ET.fromstring(res.read())

    cobrandId = int(xml.find("data/cobrandId").text)
    token = xml.find("data/token").text
    userGuid = xml.find("data/userGuid").text
    
    res.close()
    return Session(cobrandId, token, userGuid)



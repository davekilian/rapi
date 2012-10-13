"""
rapi.py - Rhapsody API
Unofficial API for obtaining metadata and streams for http://www.rhapsody.com
"""

import urllib
import urllib2
import xml.etree.ElementTree as ET

_login_url = "https://playback.rhapsody.com/login.xml"

class Session:
    """ Caches information about the user currently logged in """

    cobrandId = ""
    token = ""
    userGuid = ""

    def __init__(self, cobrandId, token, userGuid):
        self.cobrandId = cobrandId
        self.token = token
        self.userGuid = userGuid

class Artist:
    """
    Artist metadata

    Attributes
        id [str]        The artist's unique ID
        name [str]      The human-readable name of this artist
        image [str]     A URL to an image of this artist
        albumids [list] A list of IDs [str] of albums by this artist
    """

    id = ""
    name = ""
    image = ""
    albums = []

class Album:
    """
    Album metadta

    Attributes
        id [str]        The album's unique ID
        artistid [str]  The ID of the album artist
        name [str]      The human-readable name of this album
        art [str]       A URL To an image containing the album's album art
        year [int]      The year this album was released
        genre [str]     The genre the album is filed under
        trackids [list] A list of IDs [str] of the tracks in this artist
    """

    id = ""
    naem = ""
    art = ""
    year = 2000
    genre = ""
    tracks = []

class Track:
    """
    Track metadata

    Attributes
        id[str]         The track's unique ID
        artistid [str]  The ID of the track's album's album artist
        albumid [str]   The ID of the album the track appears on
        name [str]      The title of the track
        duration [int]  The length of the track in seconds
    """

    id = ""
    artistid = ""
    albumid = ""
    name = ""
    duration = 0


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



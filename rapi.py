"""
rapi.py - Rhapsody API
Unofficial API for obtaining metadata and streams for http://www.rhapsody.com
"""

import urllib
import urllib2
import xml.etree.ElementTree as ET


_dev_key = "4E1C2E3G4C9H9A2F"
_filter = "18"
_login_url = "https://playback.rhapsody.com/login.xml"
_artist_url = "http://direct.rhapsody.com/metadata/data/getArtist.xml?%s"
_artimg_url = "http://direct.rhapsody.com/metadata/data/getImageForArtist.xml?%s"
_album_url = "http://direct.rhapsody.com/metadata/data/getAlbum.xml?%s"
_track_url = "http://direct.rhapsody.com/metadata/data/getTrack.xml?%s"
_stream_url = "https://playback.rhapsody.com/getContent.xml"
_lib_url = "https://direct.rhapsody.com/library/data/getAllTracksInLibrary.xml?%s"


FORMAT_AAC_192      =   "AAC_192"   """ 192 kbps AAC audio """


class Session:
    """ Caches information about the user currently logged in """

    username = ""
    password = ""
    cobrandId = ""
    token = ""
    userGuid = ""

    def __init__(self, username, password, cobrandId, token, userGuid):
        self.username = username
        self.password = password
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
    bio = ""
    image = ""
    albumids = []

    @staticmethod
    def read(session, id, image = True):
        """
        Returns an Artist object containing information about the artist
        with the given artist ID.

        If image is false, the call will return sooner (since only HTTP
        request is required), but the Artist.image property of the artist
        returned will have the value None
        """
        data = urllib.urlencode({
            "cobrandId": session.cobrandId,
            "developerKey": _dev_key,
            "filterRightsKey": _filter,
            "artistId": id,
        })

        req = urllib2.Request(_artist_url, data)
        res = urllib2.urlopen(req)
        xml = ET.fromstring(res.read())

        art = Artist()
        art.id = id
        art.name = xml.find("name").text
        art.bio = xml.find("bio").text + "\n\n--" + xml.find("bioAuthor").text

        for node in xml.findall("albums/e/albumId"):
            art.albumids.append(node.text)

        if image:
            data = urllib.urlencode({
                "cobrandId": session.cobrandId,
                "developerKey": _dev_key,
                "defineAction": -1,
                "width": 356,
                "height": 237,
                "artistId": id,
            })

            req = urllib2.Request(_artimg_url, data)
            res = urllib2.urlopen(req)
            xml = ET.fromstring(res.read())
            art.image = xml.find("url").text

        return art


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
    artistid = ""
    name = ""
    art = ""
    year = 1900
    trackids = []

    @staticmethod
    def read(session, id):
        """
        Returns an Album object containing information about the album
        with the given album ID
        """
        data = urllib.urlencode({
            "cobrandId": session.cobrandId,
            "developerKey": _dev_key,
            "filterRightsKey": _filter, # XXX 18 or 0?
            "albumId": id,
        })

        req = urllib2.Request(_album_url, data)
        res = urllib2.urlopen(req)
        xml = ET.fromstring(res.read())

        alb = Album()
        alb.id = id
        alb.artistid = xml.find("primaryArtist/artistId").text
        alb.name = xml.find("displayName").text
        alb.art = xml.find("albumArt162x162Url").text
        alb.year = int(xml.find("releaseYear").text)

        for node in xml.findall("trackMetadatas/e/trackId"):
            alb.trackids.append(node.text)

        return alb


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
    genre = ""

    @staticmethod
    def read(session, id):
        """
        Returns an Track object containing information about the track
        with the given track ID
        """
        data = urllib.urlencode({
            "cobrandId": session.cobrandId,
            "developerKey": _dev_key,
            "filterRightsKey": _filter, # XXX 18 or 0?
            "trackId": id,
        })

        req = urllib2.Request(_track_url, data)
        res = urllib2.urlopen(req)
        xml = ET.fromstring(res.read())

        track = Track()
        track.id = id
        track.artistid = xml.find("albumMetadata/primaryArtistId").text
        track.albumid = xml.find("albumId").text
        track.name = xml.find("name").text
        track.duration = int(xml.find("playbackSeconds").text)
        track.genre = xml.find("albumMetadata/primaryStyle").text

        return track

    def stream(self, session, format):
        """
        Begins streaming this track in the given format. Returns a file-
        like object that returns the binary audio stream.
        """
        data = urllib.urlencode({
            "br": format,
            "trackId": self.id,
        })
        headers = {
            "token": session.token,
            "pcode": "mobile_iphone",
        }

        req = urllib2.Request(_stream_url, data, headers)
        res = urllib2.urlopen(req)
        xml = ET.fromstring(res.read())

        url = xml.find("data/mediaUrl").text
        print url

        req = urllib2.Request(url)
        for key in headers:
            req.add_header(key, headers[key])
        return urllib2.urlopen(req)


def auth(username, password):
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
    return Session(username, password, cobrandId, token, userGuid)


def library(session):
    """ Returns a list of IDs of tracks in the user's library """
    data = urllib.urlencode({
        "cobrandId": session.cobrandId,
        "developerKey": _dev_key,
        "logon": session.username,
        "password": session.password,
    })

    req = urllib2.Request(_lib_url, data)
    res = urllib2.urlopen(req)
    xml = ET.fromstring(res.read())

    tracks = []

    for node in xml.findall("tracks/e/trackId"):
        tracks.append(node.text)
        
    return tracks


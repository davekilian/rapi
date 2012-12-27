#!/usr/bin/env python
import os, rapi, re, sys, urllib, urllib2
from mutagen.mp4 import *
from rapi import Artist, Album, Track


def usage():
    print "Usage"
    print " dump.py output_dir [username [password]]"
    print
    print "Any omitted credentials are read from the following files:"
    print " Username        Contents of ./.username"
    print " Password        Contents of ./.password"
    print


def flush():
    sys.stdout.flush()


def safepath(name):
    return re.sub("[\/:\\*\\?\"<>|]", "_", name)


def retag(filepath, artist, album, track):
    TAG_TITLE       = "\xa9nam"
    TAG_ALBUM       = "\xa9alb"
    TAG_ARTIST      = "\xa9ART"
    TAG_ALB_ARTIST  = "aART"
    TAG_YEAR        = "\xa9day"
    TAG_GENRE       = "\xa9gen"
    TAG_GAPLESS     = "pgap"
    TAG_TRACKNUM    = "trkn"
    TAG_DISKNUM     = "disk"
    TAG_COVER       = "covr"

    cover = urllib2.urlopen(album.art).read()

    t = MP4()
    t.load(filepath)
    if t.tags == None:
        t.add_tags()

    t.tags[TAG_TITLE] = track.name
    t.tags[TAG_ALBUM] = album.name
    t.tags[TAG_ARTIST] = artist.name
    t.tags[TAG_ALB_ARTIST] = artist.name
    t.tags[TAG_YEAR] = str(album.year)
    t.tags[TAG_GENRE] = track.genre
    t.tags[TAG_GAPLESS] = True
    t.tags[TAG_TRACKNUM] = [ (track.number, len(album.trackids)) ]
    t.tags[TAG_DISKNUM] = [ (1, 1) ]
    t.tags[TAG_COVER] = [ MP4Cover(cover) ]

    t.tags.save(filepath)

artists = {}
albums = {}
def handle(trackid, outdir, sess):
    print trackid,
    flush()

    track = Track.read(sess, trackid)
    print track.name, 
    flush()

    if not track.albumid in albums:
        album = Album.read(sess, track.albumid)
        albums[album.id] = album
    else:
        album = albums[track.albumid]
    print "on", album.name,
    flush()

    if not track.artistid in artists:
        artist = Artist.read(sess, track.artistid, False)
        artists[artist.id] = artist
    else:
        artist = artists[track.artistid]
    print "by", artist.name, "...",
    flush()

    songdir = "%s/%s/%s" % (outdir, safepath(artist.name), safepath(album.name))
    flush()
    if not os.path.exists(songdir):
        os.makedirs(songdir)
    
    path = "%s/%d - %s.m4a" % (songdir, track.number, safepath(track.name))
    outfile = open(path, "w+")

    content = track.stream(sess, rapi.FORMAT_AAC_192).read()
    outfile.write(content)
    outfile.close()

    retag(path, artist, album, track)

    print "done"
    flush()


manifest = set()
def load_manifest(outdir):
    global manifest
    try:
        path = os.path.join(outdir, '.rapi-manifest')
        f = open(path, 'r')
        tracklist = [ t.strip() for t in f.readlines() ]
        manifest = set(tracklist)
        f.close()
    except IOError:
        pass

def append_manifest(outdir, trackid):
    global manifest
    manifest.add(trackid)

    path = os.path.join(outdir, '.rapi-manifest')
    f = open(path, 'a+')
    f.write(trackid + '\n')
    f.close()

def main():
    if len(sys.argv) < 2:
        usage()
        return

    outdir = sys.argv[1]
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    if len(sys.argv) > 2:
        username = sys.argv[2]
    else:
        f = open("./.username")
        username = f.read()

    if len(sys.argv) > 3:
        password = sys.argv[3]
    else:
        f = open("./.password")
        password = f.read()

    print "Loading manifest...",
    load_manifest(outdir)
    print "%d track(s)" % len(manifest)

    print "Authenticating as %s..." % username,
    flush()
    sess = rapi.auth(username, password)
    print "ok"

    print "Listing library contents...",
    flush()
    lib = rapi.library(sess)
    print "%d tracks" % len(lib)
    flush()

    for i in range(len(lib)):
        print "[%d of %d]" % (i + 1, len(lib)),
        if lib[i] in manifest:
            print "skipped (in manifest)"
        else:
            try:
                handle(lib[i], outdir, sess)
                append_manifest(outdir, lib[i])
            except:
                print "error"


if __name__ == '__main__':
    main()
    

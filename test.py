#!/usr/bin/env python

import rapi
from rapi import Artist, Album, Track

sample_artist = "Art.6774631"
sample_album = "Alb.9999950"
sample_track = "Tra.10013054"

username = "dave2343@gmail.com"
password = "lolhackathon"

if __name__ == '__main__':
    sess = rapi.auth(username, password)

    print sess.cobrandId
    print sess.token
    print sess.userGuid
    print

    art = Artist.read(sess, sample_artist)
    print art.id
    print art.name
    print art.image
    for alb in art.albumids:
        print alb, " ",
    print 
    print

    alb = Album.read(sess, sample_album)
    print alb.id
    print alb.artistid
    print alb.name
    print alb.art
    print alb.year
    print alb.numDiscs
    for tra in alb.trackids:
        print tra, " ",
    print
    print

    track = Track.read(sess, sample_track)
    print track.id
    print track.artistid
    print track.albumid
    print track.name
    print track.number
    print track.duration
    print track.genre
    print track.disc
    print

    library = rapi.library(sess)
    print "Your library has %d tracks" % len(library)
    for i in range(10):
        print library[i], " ",
    print
    print

    stream = track.stream(sess, rapi.FORMAT_AAC_192)
    # XXX does this treat the strings as text and modify the content?
    content = stream.read()
    dump = open("test.m4a", "w+")
    dump.write(content)
    dump.close()


#!/usr/bin/env python

import rapi
from rapi import Artist, Album, Track

sample_artist = "Art.6774631"
sample_album = "Alb.9999950"
sample_track = "Tra.10013054"

if __name__ == '__main__':
    username = open(".username").read()
    password = open(".password").read()
    sess = rapi.auth(username, password)

    print sess.cobrandId
    print sess.token
    print sess.userGuid
    print

    art = Artist.read(sess, sample_artist)
    print art.id
    print art.name
    print art.bio
    print art.image
    for alb in art.albumids:
        print alb, " ",
    print





#!/usr/bin/env python

import rapi

if __name__ == '__main__':
    username = open(".username").read()
    password = open(".password").read()
    sess = rapi.log_in(username, password)

    print sess.cobrandId
    print sess.token
    print sess.userGuid



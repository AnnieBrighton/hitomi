#!/usr/bin/env python
# coding: utf-8

## @package HITOMI downloader
#  Documentation for this module.
#

import os, sys, codecs   # モジュール属性 argv を取得用

try:
    # python3用のパッケージを取得
    import urllib.request as urllib2
except ImportError:
    # python2で例外となり、python2用のパッケージを取得
    import urllib2

import re

import Hitomi

#################################################################################
# Main

argvs = sys.argv
argc  = len(argvs)

b = Hitomi.Hitomi(argvs[1])
b.loadArtistList(os.path.dirname(argvs[0]) + '/artists_list.txt')
print(b.getID())
b.getAritistInfo()
b.getImageURlist()

list = b.getImgList()
#for e in list:
#    print(e)

#print (b.getStatus())
#print (b.getHTML())
print (b.getTitle())
b.imgDownload()

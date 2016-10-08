#!/usr/bin/env python
# coding: utf-8

import os, sys   # モジュール属性 argv を取得用
import urllib2
import re
import zipfile
from xml.etree.ElementTree import *

class Hitomi:
    def __init__(self, url):
        ptr = re.compile('^https?:\/\/.*[^0-9]([0-9]*).html.*$')
        m = ptr.search(url.rstrip('\n'))
        if m:
            self.__id = m.group(1)

        self.__title = ''
        self.__tmpdir = '/tmp/getImg_' + self.__id
        self.__status = ()
        self.__html = ()
        self.__imgList = []

    def getID(self):
        return self.__id

    def getStatus(self):
        return self.__status

    def getTitle(self):
        return self.__title

    def getHTML(self):
        return self.__html

    def  getImgList(self):
        return self.__imgList

    # イメージリストの取得
    def getImageURlist(self):
        url = 'https://hitomi.la/reader/' + self.__id + '.html'

        for loop in range(1, 10):
            req = urllib2.Request(url)
            try:
                response = urllib2.urlopen(req)
                self.__html = response.read()

                # <meta charset="utf-8"> 閉じが ">" -> "/>"
                # <link rel="stylesheet" href="/reader.css"> 閉じが ">" -> "/>"
                self.__html = re.sub(r'<meta([^>]*[^/])>',r'<meta\1/>',self.__html)
                self.__html = re.sub(r'<link([^>]*[^/])>',r'<link\1/>',self.__html)
                elem = fromstring(self.__html)

                # タイトル取得
                self.__title = elem.find('./head/title').text.encode('utf_8')
                if '|' in self.__title:
                    self.__title = self.__title.split('|', 1)[0]
                self.__title = self.__title.strip(' ')

                # イメージURLリストを取得
                for e in elem.findall('./body/div[@class=\'img-url\']'):
                    imgurl = 'https://a' + chr(97 + (int(self.__id) % 7)) + e.text.rstrip('\n')[3:]
                    self.__imgList.append(imgurl)

                return

            except urllib2.HTTPError, ex:
                self.__status = ex
                if ex.code == 404:
                    # 404 Not Foundはリトライする必要が無いため即復帰
                    raise ex

        # リトライ回数を超えた場合、最後の例外で
        raise self.__status


    # イメージダウンロード
    def imgDownload(self):
        list = self.getImgList()
        base = self.__tmpdir + '/' + self.__title
        if not os.path.exists(base):
            os.makedirs(base)

        for url in list:
            file = base + '/' + re.sub(r'^.+/([^/]+)$',r'\1',url)
            print('Download url=' + url + '  To file=' + file)
            self.__imgDownloadFile(file,url)
        self.__createZip()


    # イメージファイルダウンロード
    def __imgDownloadFile(self, file, url):
        for loop in range(1, 10):
            req = urllib2.Request(url)
            try:
                response = urllib2.urlopen(req)
                length = int(response.headers['Content-Length'])

                if (os.path.exists(file)) and (os.stat(file).st_size == length):
                    print 'Used exists file:' + file
                else:
                    img = response.read()
                    f = open(file, 'wb')
                    f.write(img)
                    f.close()

                if length == os.stat(file).st_size:
                    return
                else:
                    print('Download size mismatch ' + 'file size:' + str(os.stat(file).st_size) + '  content-length:' + str(length))
                    continue

            except urllib2.HTTPError, e:
                ex = e
                print('HTTPError: errno: [{0}] msg: [{1}]'.format (e.errno, e.strerror))
                if e.code == 404:
                    # 404 Not Foundはリトライする必要が無いため即復帰
                    raise e
                continue

            except IOError, e:
                print('IOError:errno: [{0}] msg: [{1}]'.format (e.errno, e.strerror))
                raise e

        # リトライ回数を超えた場合、最後の例外で
        raise ex


    # ZIPファイルの作成
    def __createZip(self):
        if os.path.exists(self.__tmpdir):
            file = self.__title + '.zip'
            if os.path.isfile(file):
                file = self.__title + '_' + self.__id + '.zip'

            # ZIPファイル作成コマンド
            cmd = 'zip -rqj "' + file + '" "' + self.__tmpdir + '/' + self.__title + '"'
            print(cmd)
            os.system(cmd)
            cmd = 'rm -fr ' + self.__tmpdir
#            print(cmd)
            os.system(cmd)

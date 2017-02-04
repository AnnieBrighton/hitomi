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
        self.__html = ()
        self.__imgList = []
        self.__artist = []      # 該当BOOKの著作者
        self.__artistList = {}  # 著作者一覧

    def getID(self):
        return self.__id

    def getTitle(self):
        return self.__title

    def getHTML(self):
        return self.__html

    def  getImgList(self):
        return self.__imgList

    # 著作者リスト読み込み
    def loadArtistList(self):
        try:
            f=open('artists_list.txt', 'r')
            ptn=re.compile(r'\t*')
            for l in f:
                l=l.replace('\n', '')
                l=l.replace('\r', '')
                k=(ptn.split(l))[0]
                v=(ptn.split(l))[-1]
                if k != v:
                    self.__artistList[k] = v
            f.close()
        except IOError, e:
            # 著作者リスト読み込みに失敗しても何もしない
            return

    # 著作者情報取得
    def getAritistInfo(self):
        url = 'https://hitomi.la/galleries/' + self.__id + '.html'

        for loop in range(1, 10):
            try:
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                html = response.read()

                html = re.sub(r'<meta([^>]*[^/])>',r'<meta\1/>',html)
                html = re.sub(r'<link([^>]*[^/])>',r'<link\1/>',html)
                html = re.sub(r'<input([^>]*[^/])>',r'<input\1/>',html)
                html = re.sub(r'<img([^>]*[^/])>',r'<img\1/>',html)

                elem = fromstring(html)
                # タイトル取得
                for el in elem.findall('./body/div/div/div/h2/ul/li/a'):
                    self.__artist.append(el.text.encode('utf_8'))

                return

            except urllib2.HTTPError, e:
                print('HTTPError: code: [{0}]'.format (e.code))
                if e.code == 404:
                    # 404 Not Foundはリトライする必要が無いため即復帰
                    raise e
                ex = e

            except urllib2.URLError, e:
                print('URLError: reason: [{0}]'.format (e.reason))
                ex = e

            except IOError, e:
                print('IOError:errno: [{0}] msg: [{1}]'.format (e.errno, e.strerror))
                raise e

        # リトライ回数を超えた場合、最後の例外で
        raise ex


    # イメージリストの取得
    def getImageURlist(self):
        url = 'https://hitomi.la/reader/' + self.__id + '.html'

        for loop in range(1, 10):
            try:
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                self.__html = response.read()

                # <meta charset="utf-8"> 閉じが ">" -> "/>"
                # <link rel="stylesheet" href="/reader.css"> 閉じが ">" -> "/>"
                self.__html = re.sub(r'<meta([^>]*[^/])>',r'<meta\1/>',self.__html)
                self.__html = re.sub(r'<link([^>]*[^/])>',r'<link\1/>',self.__html)
                elem = fromstring(self.__html)

                # タイトル取得
                self.__title = re.sub(r'[\\\'"]', r'', elem.find('./head/title').text.encode('utf_8'))
                if '|' in self.__title:
                    self.__title = self.__title.split('|', 1)[0]
                self.__title = self.__title.strip(' ')

                # 著作者が一人のときタイトルに著作者を追加
                if len(self.__artist) == 1 :
                    if self.__artist[0] in self.__artistList :
                        self.__title = '【' + self.__artistList[self.__artist[0]] + '】' + self.__title
                    else:
                        self.__title = '【' + self.__artist[0] + '】' + self.__title

                # イメージURLリストを取得
                for el in elem.findall('./body/div[@class=\'img-url\']'):
                    #imgurl = 'https://a' + chr(97 + (int(self.__id) % 7)) + el.text.rstrip('\n')[3:]
                    imgurl = 'https://a' + chr(97) + el.text.rstrip('\n')[3:]
                    self.__imgList.append(imgurl)

                return

            except urllib2.HTTPError, e:
                print('HTTPError: code: [{0}]'.format (e.code))
                if e.code == 404:
                    # 404 Not Foundはリトライする必要が無いため即復帰
                    raise e
                ex = e

            except urllib2.URLError, e:
                print('URLError: reason: [{0}]'.format (e.reason))
                ex = e

        # リトライ回数を超えた場合、最後の例外で
        raise ex


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
            try:
                req = urllib2.Request(url)
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
                print('HTTPError: code: [{0}]'.format (e.code))
                if e.code == 404:
                    # 404 Not Foundはリトライする必要が無いため即復帰
                    raise e
                ex = e

            except urllib2.URLError, e:
                print('URLError: reason: [{0}]'.format (e.reason))
                ex = e

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

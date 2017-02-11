#!/usr/bin/env python
# coding: utf-8

import os, sys   # モジュール属性 argv を取得用
import datetime
import json
try:
    # python3用のパッケージを取得
    import urllib.request as urllib2
except ImportError:
    # python2で例外となり、python2用のパッケージを取得
    import urllib2

import re

#
# hitomi.la リスト取得ツール
#

class GetListHitomi:
    #
    # コンストラクタ
    #
    def __init__(self, no):
        self.__artistList = {}  # 著作者一覧
        self.__home = os.environ['HOME'] + '/.hitomi/'
        self.__jsonfile = self.__home + 'hitomi_galleries%02d.json' % no
        self.__url = 'https://hitomi.la/galleries%d.json' % no

        if not os.path.exists(self.__home):
            os.mkdir(self.__home)

    #
    # Listファイルの存在チェック
    #
    def isJsonfile(self):
        return os.path.exists(self.__jsonfile)

    #
    # 著作者リスト取得
    #
    def loadArtistList(self, file):
        try:
            ptn=re.compile(r'\t+')
            try:
                # Python3ではコード系指定
                f=open(file, 'r', encoding='utf_8')
            except TypeError:
                # Python2では、例外となり通常のオープン
                f=open(file, 'r')

            for l in f:
                l=l.replace('\n', '')
                l=l.replace('\r', '')
                k=(ptn.split(l))[0]
                v=(ptn.split(l))[-1]
                if k != v:
                    self.__artistList[k] = v
            f.close()
        except IOError as e:
            # 著作者リスト読み込みに失敗しても何もしない
            return

    #
    # リストファイルダウンロード
    #
    def ListFileDownload(self):
        file = self.__jsonfile
        url = self.__url

        for loop in range(1, 10):
            try:
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)

                # レスポンスのサイズを取得
                length = int(response.headers['Content-Length'])
                # レスポンスの変更時間を取得
                ts= datetime.datetime.strptime( response.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S GMT' )

                if (not(os.path.exists(file)) or not(os.stat(file).st_size == length) or not(datetime.datetime.utcfromtimestamp(os.path.getmtime(file)) > ts)):
                    # ファイルが存在しない、または、
                    # ファイルサイズがレスポンスのサイズと一致しない、または、
                    # ファイルのタイムスタンプがレスポンスの変更時間より新しくない場合、ダウンロードを実施。
                    img = response.read()
                    f = open(file, 'wb')
                    f.write(img)
                    f.close()

                    if length != os.stat(file).st_size:
                        # ファイルサイズがレスポンスのサイズと異なっていれば、再取得を実施
                        print('Download size mismatch ' + 'file size:' + str(os.stat(file).st_size) + '  content-length:' + str(length))
                        continue
                return

            except urllib2.HTTPError as e:
                print('HTTPError: code: [{0}]'.format (e.code))
                if e.code == 404:
                    # 404 Not Foundはリトライする必要が無いため即復帰
                    raise e
                ex = e

            except urllib2.URLError as e:
                print('URLError: reason: [{0}]'.format (e.reason))
                ex = e

            except IOError as e:
                print('IOError:errno: [{0}] msg: [{1}]'.format (e.errno, e.strerror))
                raise e

        # リトライ回数を超えた場合、最後の例外で
        raise ex

    #
    # 取得したListファイルを変換
    #
    def convertList(self):
        f = open(self.__jsonfile)
        data = json.load(f)

        #  jsonファイル構造
        #  type : artistcg / manga / doujinshi
        #    id : Id
        #     n : Title
        #     l : language(japanese ....)
        #     a : Artist
        #     t : Tag
        #     p : Series
        #     g :
        #     c :

        list = {}
        for l in data:
            if l['type'] == 'manga' and l['l'] == 'japanese':
                # 言語:日本語
                # タイプ:漫画

                # タグを展開
                tag = {}
                if 't' in l:
                    for t in l['t']:
                        tag[t] = t

                # 著作者展開
                ar = ''
                sp = ''
                if 'a' in l:
                    for a in l['a']:
                        if a in self.__artistList:
                            ar = ar + sp + self.__artistList[a]
                        else:
                            ar = ar + sp + a
                        sp = '/'

                if ('novel' not in tag) and not(('male:yaoi' in tag) and ('male:males only' in tag)):
                    list[l['id']] = 'https://hitomi.la/galleries/' + str(l['id']) + ".html " + l['n'] + ', Art=[' + ar + ']'

        for k in sorted(list.keys(), reverse=True):
            print(list[k])

#
#
#
def main(no, d):
    file = os.path.dirname(sys.argv[0]) + '/artists_list.txt'

    htm = GetListHitomi(no)
    htm.loadArtistList(file)

    # hitomi リストファイル取得
    if not htm.isJsonfile() or d == 1:
        htm.ListFileDownload()

    # hitomi リストファイル変換
    if htm.isJsonfile():
        htm.convertList()
    else:
        print('リストファイルが存在しない')

#
# メイン
#

if __name__ == "__main__":
    # execute only if run as a script

    d = 0
    max = 1
    if len(sys.argv) > 1:
        d = 1
        max = int(sys.argv[1]) + 1

    for i in range(0, max):
        main(i, d)

# hitomi.la ダウンローダー

## 環境
  MAC(おそらくLinux環境でも動くかと)
  Python 2.7

## 使い方
### 単一指定

     ./getHitomi.py 'https://hitomi.la/galleries/980468.html'

正常にダウンロードできた場合、カレントディレクトリにzipファイルを作成

     Re:Zero nara Mou Kirawarete mo Hameochi Suru made Rape.zip

### 複数指定

ダウンロードしたいリストファイルを作成

sample.txt

    https://hitomi.la/galleries/980468.html
    https://hitomi.la/galleries/969973.html
    https://hitomi.la/galleries/966240.html

ダウンロード実行

    getHitomi.sh sample.txt

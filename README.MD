# hitomi.la ダウンローダー

## 環境
  MAC(おそらくLinux環境でも動くかと)
  Python 2.7 / Pyhon3.5

## 使い方
### 単一指定

     ./getHitomi.py 'https://hitomi.la/galleries/980468.html'

正常にダウンロードできた場合、カレントディレクトリにzipファイルを作成

     Re:Zero nara Mou Kirawarete mo Hameochi Suru made Rape.zip

著作者が1名の場合、ファイル名に著作者を追加

     ./getHitomi.py  https://hitomi.la/galleries/1026809.html

正常にダウンロードできた場合、artists_list.txt に名前があれば置き換える。

    1.【すえひろがり】Roshutsu de Yume Gokochi.zip  ... ある
    2.【suehirogari】Roshutsu de Yume Gokochi.zip  ... なし

### 複数指定

ダウンロードしたいリストファイルを作成

sample.txt

    https://hitomi.la/galleries/980468.html
    https://hitomi.la/galleries/969973.html
    https://hitomi.la/galleries/966240.html

ダウンロード実行

    getHitomi.sh sample.txt

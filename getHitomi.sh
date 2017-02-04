#!/bin/bash

BASE=$(dirname $0)

cat "$1" | while read url other ; do
  [ -n "$url" ] && echo "$url"
done | xargs -P8 -n1 -I{} $BASE/getHitomi.py "{}"

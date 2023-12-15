#!/usr/bin/bash

url="${1}${3}-${4}.txt.zip"

echo

mkdir ${2}

cd ${2}

wget --no-check-certificate ${url}

unzip *.zip

rm README *.zip LICENSE *.xml

cd ..
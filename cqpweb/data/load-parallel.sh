#!/bin/bash

file=`basename $1`
echo ${file}
fileArr=(${file//./ })
name=${fileArr[0]}
directory="/cwb/data/${name}"
echo ${directory}

if [[ ! -d ${directory} ]]; then
mkdir ${directory}
fi

cwb-encode -d ${directory} -f ${file} -R /cwb/registry/${name} -P pos -S text+id -c utf8
cwb-make -V ${name^^}

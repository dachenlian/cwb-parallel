#!/bin/bash

file=`basename $1`
echo ${file}
fileArr=(${file//./ })
name=${fileArr[0]}
directory="/cwb/data/${name}"

if [[ ! -d ${directory} ]]; then
mkdir /cwb/data/${directory}
fi

cwb-encode -d ${directory} -f ${file} -R /cwb/registry/${name} -P pos -S text+id
cwb-make -V ${name^^}

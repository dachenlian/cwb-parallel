#!/usr/bin/env bash

file=$1

echo "Creating alignment TW -> CN"
# cwb-align-import -s text -p ${file} 
cwb-align-import ${file} 

echo "Creating alignment CN -> TW"
cwb-align-import -i ${file}  # invert alignment CN -> TW
# cwb-align-import -s text -i -p ${file}  # invert alignment CN -> TW

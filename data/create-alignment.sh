#!/usr/bin/env bash

file=$1

echo "Creating alignment TW -> CN"
cwb-align-import -p ${file}

echo "Creating alignment CN -> TW"
cwb-align-import -i -p ${file}  # invert alignment CN -> TW

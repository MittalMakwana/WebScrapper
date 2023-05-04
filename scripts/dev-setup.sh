#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_DIR="$(dirname $DIR)/src"

variables=$(find ${SOURCE_DIR} -type f -name ".env.yaml" -exec cat {} \; | sort | uniq | sed 's/: /=/g')

for var in $variables
do
    echo export $var
done
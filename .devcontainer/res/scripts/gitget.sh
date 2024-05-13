#!/bin/sh
if [ -z "$1" ]; then
    echo "Please provide a url to a folder of a git repository."
    exit 1
fi

if ! echo "$1" | grep -q "^https://github.com/"; then
    echo "URL must start with https://github.com/"
    exit 1
fi

URL_RAW=$1

# Replace main/tree with trunk where as main can be any branch name
URL=$(echo $URL_RAW | sed 's/tree\/[A-Za-z0-9]*\?/trunk\//g')

# get the last word of the url wihich is the folder name
LAST_WORD=$(echo $URL | rev | cut -d'/' -f1 | rev)


if [ -d "$PWD/$LAST_WORD" ]; then
    echo "Directory $LAST_WORD already exists."
    exit 1
fi

# checkout the svn repo and remove the .svn folder for clean up
svn checkout "$URL" "$PWD/$LAST_WORD" && cd "$PWD/$LAST_WORD" && rm -rf .svn
exit 0

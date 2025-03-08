#!/bin/zsh


DIR_NAME=$( cd $(dirname $BASH_SOURCE)  && pwd)

source $DIR_NAME/bin/activate

streamlit run $DIR_NAME/app.py


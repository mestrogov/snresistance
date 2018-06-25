#!/bin/bash

screenName="SNResistance"
sshKeyPath="/home/citorijawa/.ssh/git_vps"

eval $(ssh-agent -s)
ssh-add $sshKeyPath
git pull

rm -rf venv

virtualenv venv
venv/bin/python -m pip install pyTelegramBotAPI
venv/bin/python -m pip install requests

screen -dmS $screenName venv/bin/python app/bot.py
sleep 3
screen -x $screenName

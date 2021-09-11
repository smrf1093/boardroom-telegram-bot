# Telegram bot for BroadRoom API

![Build workflow](https://github.com/seyedrezafar/boardroom-telegram-bot/actions/workflows/main.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub license](https://img.shields.io/github/license/seyedrezafar/boardroom-telegram-bot)](https://github.com/seyedrezafar/boardroom-telegram-bot/blob/master/LICENSE)


The telegram bot providing commands for interaction with BroadRoom API.

For webservice provider the Django framework is used, however it could be easily
replaced with Fast api and ... .


# Quickstart
To install and use follow the below instructions:

```sh
$ cp .env.example .env # edit with your favorite editor!
$ docker-compose up -d
```


# Modularity

The source code is modular, so if any other library need to be used for sending bot messages it could be easily done by overriding the login of send_message and send_bulk_message in bot source code.

# help

Run /help command to see all available commands

# The bot

The main source code for bot is located in bothandler application and
also it could be placed anywhere else.
The bot folder contains the following files:

## api_handler

This file handles the interactions with broadroom api

## bot_commands

This file contains the bot's commands they use functions from api_handler

## bot

Contains the bot which handle commands using the classes from bot_commands
s

# Celery and Subscription

For subscription mechanism the celery and django celer were used, the following command needs to run the tasks every 5 minutes:

`celery -A conf beat -l INFO`

Redis is used as the broker for celery, so it should be run on the system. There is a docker-compose file in the project root that contains instruction for running an instance of Redis.

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

# Demo

A live version of the bot is available at:

https://t.me/hhio618_bot

[![Watch the video](https://img.youtube.com/vi/mHbO9RZeg3M/maxresdefault.jpg)](https://youtu.be/mHbO9RZeg3M)

# Modularity

The source code have been written with modularity in the mind. So every part could be changed or can be extended easily without too much effect on other parts.

# Help

Run /help command to see all available commands

# Bot source code

This is a bot for boardroom API written based on Django Framework. The Django ORM and modeling is used for caching and storing data where needed.

The main django configurations resides in conf folder and there is one Django application called bot in the project that handles the Telegram bot views, models, tasks and extra.

# Subscription & Alerting

The following celery tasks are written to handle Alerting and Subscription:

ProposalUpdateTgView: this task view check whether the subscribed proposal by user have been changed or not, if it is changed then it will notify the subscried users.

ProposalPeriodtgView: This is a alerting mechanism that users can toggle it on or off. if the user toggle it on the information for top proposal will be send for user periodically.

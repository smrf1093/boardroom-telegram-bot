# Telegram bot for BroadRoom API

![Build workflow](https://github.com/seyedrezafar/boardroom-telegram-bot/actions/workflows/main.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub license](https://img.shields.io/github/license/seyedrezafar/boardroom-telegram-bot)](https://github.com/seyedrezafar/boardroom-telegram-bot/blob/master/LICENSE)

The telegram bot providing commands for interaction with BroadRoom API.

For webservice provider the Django framework is used, however it could be easily
replaced with Fast api and ... .

## Quickstart

To install and use follow the below instructions:

```sh
$ cp .env.example .env # edit with your favorite editor!
$ docker-compose up -d
```

## Demo

A live version of the bot is available at:

https://t.me/hhio618_bot

[![Watch the video](https://img.youtube.com/vi/mHbO9RZeg3M/maxresdefault.jpg)](https://youtu.be/mHbO9RZeg3M)

## Features
+ Proposal period notifications
+ Track proposal voting
+ Easy UX for better navigation
+ Manage subscriptions
+ List top proposals and protocols
+ Supports API pagination

## Bot source code

This is a bot for boardroom API written based on Django Framework. The Django ORM is used for caching and storing data where needed.  
The main django configurations resides in conf folder and there is one Django application called bot in the project that handles the Telegram bot views, models, tasks and extra.

## Subscription & Alerting

There are two type of alerts provided:

### ProposalUpdateTgView
this task view check whether the subscribed proposals by user have been changed or not, if it is changed then it will notify the subscribed users.

### ProposalPeriodTgView
This is a alerting mechanism that users can toggle it on or off. it will send proposal period alerts whenever a proposal voting end date is reached below a certain time period, e.g. 5 days, 3 days, ...

# Telegram bot for BroadRoom API

The telegram bot providing commands for interaction with BroadRoom API.

For webservice provider the Django framework is used, however it could be easily
replaced with Fast api and ... .

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

import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()

from bot.handlers.dispatcher import run_pooling

if __name__ == "__main__":
    run_pooling()
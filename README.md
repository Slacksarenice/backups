# Backup Home Directory (Linux Debian)

This is a very simple backup program that backs-up a specified directory to a location you specify and has gpg capabilites to encrypt only using the key fingerprint. I tried to design it around using it with cron

## Requirements

[Python 3.8](https://www.python.org/downloads/)

# Installation

## Via Pipenv

+   git clone https://github.com/Slacksarenice/backups.git
+   cd backups
+   pipenv install
+   pipenv run ./backup.py

## Via Requirements

+   git clone https://github.com/Slacksarenice/backups.git
+   cd backups
+   pip install -r requirements.txt
+   ./backup.py

## Contribute

Feel free to ask for pull requests as this is a small project that I am keeping on the side and will expand to greater uses in the future.


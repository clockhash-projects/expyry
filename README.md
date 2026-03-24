# expyry
[![PyPI version](https://badge.fury.io/py/expyry.svg)](https://badge.fury.io/py/expyry)

A lightweight CLI tool to track and monitor credential & token expiry dates across your stack.

[![asciicast](https://asciinema.org/a/LI36NGf6J2gpv4dX.svg)](https://asciinema.org/a/LI36NGf6J2gpv4dX)

## Requirements

- Python 3.10+
- pip

## Install
📦 [PyPI](https://pypi.org/project/expyry/)
```
pip install expyry
```
## Usage
```
expyry add              — add a credential
expyry list             — list all credentials  
expyry notify enable    — enable shell notifications
expyry notify disable   — disable shell notifications
expyry remove <name>    — remove a credential
expyry update <name>    — update a credential
```
## Supported Services

| Service | How expiry is detected |
|---|---|
| GitHub PAT | API response header |
| SSL Certificate | Direct TLS connection |
| Custom | Manual date entry |

## Shell Notifications

Expyry can silently check your credential expiry dates every time you open a terminal
and warns you only when something is expiring soon.
```
expyry notify enable
```
# Contributing

## Adding a new service

1. Create `expyry/services/yourservice.py`
2. Implement `check_yourservice()` and `add_yourservice()`
3. Wire it into `main.py` and `add()`
4. Open a PR

See `services/ssl.py` for a simple example.

## License

MIT

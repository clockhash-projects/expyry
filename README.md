# expyry

A lightweight CLI tool to track and monitor credential & token expiry dates across your stack.

[![asciicast](https://asciinema.org/a/LI36NGf6J2gpv4dX.svg)](https://asciinema.org/a/LI36NGf6J2gpv4dX)

## Install
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
## Contributing

Contributions welcome. To add a new service, create a file in `services/`
and wire it into `main.py`. See `services/ssl.py` for a simple example.

## License

MIT

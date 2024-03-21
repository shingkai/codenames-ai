# Codenames-AI

_An implementation of the game Codenames in a Discord UI, with multiple AI players_

## Setting up the python environment
1. create a virtual environment with python 3.7+ and activate it
    - `python3 -m venv env && source env/bin`
1. install dependencies:
    - `pip install -r requirements.txt`


## Setting up the Discord Bot
1. create a [new Discord app](https://discord.com/developers/docs/getting-started)
1. add the bot to a server:
    - `https://discord.com/oauth2/authorize?client_id=<YOU_CLIENT_ID>&permissions=2048&scope=bot`
    - (permission integer = `2048`)
1. save [`example.env`](example.env) as [`.env`](.env) _(any other config changes will go here)_
1. edit [`.env`](.env) and add your discord bot token

## Running the Discord Bot
1. make [`run.sh`](run.sh) executable: `chmod +x run.sh`
2. run the bot: `./run.sh`

## Using the AI-Spymaster and AI-Guesser directly
### Examples
- [demo.py](codenames/demo.py) - python script that creates a game, prepares embedding models,
creates ai-spymaster and ai-guesser players, and generates glues and hints. game.
- [notebooks/](notebooks/) - jupyter notebooks that were used to as scratchpads while developing python. _not guaranteed to still run properly._

## Software Use
_see [LICENSE](LICENSE)_

_python packages used:_
- [`discord.py`](https://github.com/Rapptz/discord.py)
- [`gensim`](https://github.com/piskvorky/gensim)
- [`sbert`]()

_models used:_
- `word2vec`
- `fasttext`
- `sbert`
- `gemma-2b`

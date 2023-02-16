# Slido Upvoter

A simple Python script for automatically upvoting your Slido question.

## Why?

Why not?

## How it works

The script uses Selenium (which is required for it to run) and loops numerous times (that you set) and upvoting your
question.

## Using the script

You must have `pipenv` installed. Before running the actual script, run `pipenv install` and then `pipenv shell`.

Then run `upvote.py` and pass the necessary parameters, e.g.

```sh
./upvote.py --id cDnyFE9aFzS667ahS69SaK --qid 12345678 --votes 3
```


The full usage info is available with `./upvote.py --help`:

```sh
$ ./upvote.py --help
usage: Slide Upvoter [-h] --id ID --qid QID [--max-wait MAX_WAIT] [--votes VOTES] [-v]

Upvote your question in Slido

options:
  -h, --help           show this help message and exit
  --id ID              The ID of the Slido board
  --qid QID            The ID of the question to upvote
  --max-wait MAX_WAIT  How many seconds to wait for the page to load (default 10)
  --votes VOTES        How many votes should the question receive (default 1)
  -v, --verbose
```

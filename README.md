# Slido Upvoter

A simple Python script to automatically upvote your Slido question.

## Why?

Why not? And opening an incognito window several times is just annoying! 😁

## How does it work

The script uses Selenium and runs through a loop to upvote your question.

## Using the script

You must have `poetry` installed. Before running the actual script, run
`poetry install --no-root` and then `poetry shell`.

Then run `upvote.py` and pass the necessary parameters, e.g.

```sh
./upvote.py --id cDnyFE9aFzS667ahS69SaK --qid 12345678 --votes 3
```

The full usage info is available with `./upvote.py --help`:

```sh
$ ./upvote.py --help
usage: Slide Upvoter [-h] --id ID --qid QID [--max-wait MAX_WAIT] [--max-votes MAX_VOTES] [--parallel PARALLEL] [--sleep SLEEP] [-v]

Upvote your question in Slido

options:
  -h, --help            show this help message and exit
  --id ID               The ID of the Slido board
  --qid QID             The ID of the question to upvote
  --max-wait MAX_WAIT   How many seconds to wait for the page to load (default 10)
  --max-votes MAX_VOTES
                        How many votes should the question receive (default 1)
  --parallel PARALLEL   How many instances should vote parallel (default 4)
  --sleep SLEEP         How long to sleep between votes (default 5)
  -v, --verbose
```

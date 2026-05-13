# Contributing to ClaudeClaw BANDA

This repository is a BANDA starter kit / overlay, not a forked redistribution of ClaudeClaw runtime source.

## Scope

Good contributions:

- BANDA agent profiles in `overlay/agents/`;
- setup and packaging improvements in `setup.sh`;
- documentation, examples, screenshots, and diagrams;
- safety checks for secrets, private paths, and attribution metadata.

Out of scope here:

- vendoring or copying upstream ClaudeClaw source code into this repository;
- removing upstream attribution;
- adding real API keys, Telegram bot tokens, private chat IDs, or local machine paths.

## Local test

```bash
./setup.sh runtime/claudeclaw-test
```

Then inspect the generated runtime directory before adding secrets:

```bash
cd runtime/claudeclaw-test
find agents .claudeclaw data -maxdepth 3 -type f | sort
```

## Before committing

```bash
git diff --check
bash -n setup.sh
```

Also scan changed lines for secrets and private paths. This repository is public.

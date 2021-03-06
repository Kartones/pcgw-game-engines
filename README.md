# PCGW Game Engines

## Intro

There is no official list of game engines and which games use them, but the awesome website [www.pcgamingwiki.com](https://www.pcgamingwiki.com) contains an incredible amount of titles **and** many are tagged with the corresponding engine **and** the website is powered by [MediaWiki](https://www.mediawiki.org/wiki/API:Main_page) for its [API](https://www.pcgamingwiki.com/wiki/PCGamingWiki:API). Because of those reasons, I decided to write some python scripts to fetch the relevant data (in a polite, non-abusive way) and then be able to do some analytics with it.

Currently the Python script just fetches and stores a CSV of game engine names (PCGW naming scheme), then fetches and stores a list of games for each engine (into a single CSV file), and then generates a third CSV file containing a generalized games per engines list, because why building that basic aggregate later when they is so easily built from here?

## Setup

```bash
pip3 install -r requirements.txt
```

## Running

```bash
python3 fetch_data.py
```

Comment or uncomment as desired actions at `__main__`. 

Note that it is on purpose using most of the times files as input where it could instead pass in-memory data, but my intention is to ensure CSV files are always in perfect shape and dataset size is tiny so really fast anyway.


## License

See [LICENSE](LICENSE).

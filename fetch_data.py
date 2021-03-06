import csv
from datetime import datetime
import json
from operator import itemgetter
from typing import cast, Dict, List, Tuple
from urllib.parse import quote_plus

import requests


class FetchPCGWData:

    USER_AGENT = "PCGW-Game-Engines/0.2 (https://github.com/kartones/pcgw-game-engines)"
    CSV_SEPARATOR = ","
    CSV_QUOTE_CHAR = "\""

    PAGE_SIZE = 500

    ENGINE_PREFIX = "Engine:"

    GAMES_CSV_HEADER_ROW = ["title", "engine", "release_date"]

    # bad data
    ENGINE_OUTLIERS = ["129401"]

    @classmethod
    def fetch_game_engines_list_to_csv(cls, list_output_filename: str) -> None:
        count = 0
        # must be json
        engines_list_url = "https://www.pcgamingwiki.com/w/api.php?action=query&generator=categorymembers&gcmlimit={limit}&format=json&gcmtitle=Category:Engines".format(  # NOQA: E501
            limit=cls.PAGE_SIZE
        )
        headers = {
            "User-Agent": cls.USER_AGENT
        }

        response = requests.get(engines_list_url, headers=headers)
        engines_json = json.loads(response.text)["query"]["pages"]

        with open(list_output_filename, "w", newline="") as csv_file_handle:
            csv_writer = csv.writer(csv_file_handle, delimiter=cls.CSV_SEPARATOR, quotechar=cls.CSV_QUOTE_CHAR,
                                    quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["id", "title"])

            for key in (engines_json.keys() - cls.ENGINE_OUTLIERS):
                csv_writer.writerow([engines_json[key]["pageid"], engines_json[key]["title"].lstrip(cls.ENGINE_PREFIX)])
                count += 1

        print("> Read {} engines ".format(count))
        print("> Written data to '{}'".format(list_output_filename))

    @classmethod
    def fetch_games(cls, engines_list_filename: str, games_output_filename: str) -> None:
        count = 0
        games = []  # type: List[Tuple[str, str, str]]

        engines = cls._load_engines_from_csv(engines_list_filename)

        # Note: as saves each game of a certain engine, engines without games automatically filtered out
        for engine in engines:
            engine_games = data._fetch_games_per_engine(engine)
            games += engine_games
            print("> Read {count} games with engine '{engine}'".format(count=len(engine_games), engine=engine))

        with open(games_output_filename, "w", newline="") as csv_file_handle:
            csv_writer = csv.writer(csv_file_handle, delimiter=cls.CSV_SEPARATOR, quotechar=cls.CSV_QUOTE_CHAR,
                                    quoting=csv.QUOTE_ALL)
            csv_writer.writerow(cls.GAMES_CSV_HEADER_ROW)

            for game in games:
                csv_writer.writerow(game)
                count += 1

        print("> Read {} games".format(count))
        print("> Written data to '{}'".format(games_output_filename))

    @classmethod
    def generalize_game_engines(cls, games_list_filename: str, generalized_games_output_filename: str) -> None:
        count = 0
        engine_mapping = cls._combined_engine_versions_map()

        games = cls._load_games_from_csv(games_list_filename)

        generalized_games = [(
                game[0],
                engine_mapping[game[1]] if game[1] in engine_mapping else game[1],
                game[2],
            ) for game in games]
        # to ease human reading
        generalized_games = sorted(generalized_games, key=itemgetter(1, 0))

        with open(generalized_games_output_filename, "w", newline="") as csv_file_handle:
            csv_writer = csv.writer(csv_file_handle, delimiter=cls.CSV_SEPARATOR, quotechar=cls.CSV_QUOTE_CHAR,
                                    quoting=csv.QUOTE_ALL)
            csv_writer.writerow(cls.GAMES_CSV_HEADER_ROW)

            for game in generalized_games:
                csv_writer.writerow(game)
                count += 1

        print("> Checked {} games".format(count))
        print("> Written data to '{}'".format(generalized_games_output_filename))

    @staticmethod
    def _combined_engine_versions_map() -> Dict[str, str]:
        return {
            "CryEngine V": "CryEngine",
            "CryEngine (4th generation)": "CryEngine",
            "CryEngine 2": "CryEngine",
            "CryEngine 3": "CryEngine",
            "Id Tech 1": "Id Tech",
            "Id Tech 2": "Id Tech",
            "Id Tech 3": "Id Tech",
            "Id Tech 4": "Id Tech",
            "Id Tech 5": "Id Tech",
            "Id Tech 6": "Id Tech",
            "Id Tech 7": "Id Tech",
            "Quake engine": "Id Tech",
            "QuakeWorld": "Id Tech",
            "Frostbite 1.5": "Frostbite",
            "Frostbite 2": "Frostbite",
            "Frostbite 3": "Frostbite",
            "SAGE 2.0": "SAGE",
            "Unreal Engine 1": "Unreal Engine",
            "Unreal Engine 2": "Unreal Engine",
            "Unreal Engine 2.5": "Unreal Engine",
            "Unreal Engine 3": "Unreal Engine",
            "Unreal Engine 4": "Unreal Engine",
            "Unreal Engine 5": "Unreal Engine",
            "Gamebryo (TES Engine)": "Gamebryo",
            "GEM 2": "GEM",
            "GEM 3": "GEM",
            "AGL 2": "AGL",
            "AGL 3": "AGL",
            "AGL 4": "AGL",
            "The Sims 2 Engine": "The Sims Engine",
            "The Sims 3 Engine": "The Sims Engine",
            "Glacier 2": "Glacier",
            "Avalanche Engine 3.0": "Avalanche Engine",
            "Avalanche Engine 2.0": "Avalanche Engine",
            "Ptero Engine II": "Ptero Engine",
            "Ptero Engine III": "Ptero Engine",
            "Refractor 2": "Refractor",
            "Construct Classic": "Construct",
            "Construct 2": "Construct",
            "Construct 3": "Construct",
            "Photex2": "Photex",
            "Dunia 2": "Dunia",
            "Source 2": "Source",
            "Vicious Engine 2": "Vicious Engine",
            "KiriKiri Z": "KiriKiri",
        }

    @classmethod
    def _load_games_from_csv(cls, games_list_filename: str) -> List[Tuple[str, str, str]]:
        games = []  # type: List[Tuple[str, str, str]]

        with open(games_list_filename, newline="") as csv_file_handle:
            csv_reader = csv.reader(csv_file_handle, delimiter=cls.CSV_SEPARATOR, quotechar=cls.CSV_QUOTE_CHAR)
            for index, row in enumerate(csv_reader):
                if (index == 0):
                    continue
                games.append(cast(Tuple[str, str, str], tuple(row)))

        return games

    @classmethod
    def _load_engines_from_csv(cls, engines_list_filename: str) -> List[str]:
        engines = []  # type: List[str]

        with open(engines_list_filename, newline="") as csv_file_handle:
            csv_reader = csv.reader(csv_file_handle, delimiter=cls.CSV_SEPARATOR, quotechar=cls.CSV_QUOTE_CHAR)
            for index, row in enumerate(csv_reader):
                if (index == 0):
                    continue
                engines.append(row[1])

        return engines

    @classmethod
    def _fetch_games_per_engine_page(cls, engine_title: str, offset: int) -> List[Tuple[str, str, str]]:
        # could be csv also, but we want to filter data
        export_format = "json"

        # [[Category:Games]] [[Uses engine::Engine:id Tech 2]]
        games_per_engine_url = "https://www.pcgamingwiki.com/w/index.php?title=Special:Ask&q=[[Category%3AGames]]+[[Uses+engine%3A%3AEngine%3A{engine}]]&po=%3FRelease+date%23ISO%7C%2Border%3Dasc%7C%2Blimit%3D1%0D%0A&p=format%3D{format}&limit={limit}&offset={offset}".format(  # NOQA: E501
            engine=quote_plus(engine_title), format=export_format, limit=cls.PAGE_SIZE, offset=max(offset, 0)
        )
        headers = {
            "User-Agent": cls.USER_AGENT
        }

        response = requests.get(games_per_engine_url, headers=headers)
        if response.text:
            games_json = json.loads(response.text)["results"]
        else:
            games_json = {}

        games = []  # type: List[Tuple[str, str, str]]

        for key in games_json.keys():
            release_date = games_json[key]["printouts"]["Release date"]

            games.append(
                (games_json[key]["fulltext"],
                 engine_title,
                 datetime.fromtimestamp(int(release_date[0]["timestamp"])).strftime("%Y") if release_date else "")
            )

        return games

    @classmethod
    def _fetch_games_per_engine(cls, title: str) -> List[Tuple[str, str, str]]:
        games = []  # type: List[Tuple[str, str, str]]

        offset = 0
        keep_reading = True
        while keep_reading:
            games_page = cls._fetch_games_per_engine_page(title, offset)
            games += games_page
            offset += cls.PAGE_SIZE
            keep_reading = len(games_page) == cls.PAGE_SIZE

        return games


if __name__ == "__main__":

    engines_csv = "engines_list.csv"
    games_csv = "games.csv"
    generalized_games_csv = "games_generalized.csv"

    data = FetchPCGWData()

    data.fetch_game_engines_list_to_csv(engines_csv)

    data.fetch_games(engines_csv, games_csv)

    data.generalize_game_engines(games_csv, generalized_games_csv)

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

    GENERALIZED_GAMES_CSV_HEADER_ROW = ["title", "engine", "release_dates"]
    GAMES_CSV_HEADER_ROW = ["title", "engine", "engine_build", "release_dates"]

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

        print("> Fetching engines list: {}".format(engines_list_url))

        response = requests.get(engines_list_url, headers=headers)
        engines_json = json.loads(response.text)["query"]["pages"]

        with open(list_output_filename, "w", newline="") as csv_file_handle:
            csv_writer = csv.writer(csv_file_handle, delimiter=cls.CSV_SEPARATOR, quotechar=cls.CSV_QUOTE_CHAR,
                                    quoting=csv.QUOTE_ALL)
            csv_writer.writerow(["id", "title"])

            for key in (engines_json.keys() - cls.ENGINE_OUTLIERS):
                csv_writer.writerow([engines_json[key]["pageid"], engines_json[key]["title"][len(cls.ENGINE_PREFIX):]])
                count += 1

        print("> Read {} engines ".format(count))
        print("> Written data to '{}'".format(list_output_filename))

    @classmethod
    def fetch_games_from_cargo_page(cls, games_output_filename: str) -> None:
        count = 0
        games = []  # type: List[Tuple[str, str, str, str]]

        offset = 0
        keep_reading = True
        while keep_reading:
            games_page = cls._fetch_games_page(offset)
            games += games_page
            offset += cls.PAGE_SIZE
            keep_reading = len(games_page) == cls.PAGE_SIZE

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
    def _fetch_games_page(cls, offset: int) -> List[Tuple[str, str, str, str]]:
        export_format = "json"

        # cargo queries support joins, so we retrieve the game release date(s) at the same time

        games_page_url = "https://www.pcgamingwiki.com/w/api.php?action=cargoquery&tables=Infobox_game_engine%2C+Infobox_game&join+on=Infobox_game._pageName%3DInfobox_game_engine._pageName&fields=Infobox_game_engine._pageName%3DPage%2C+Infobox_game_engine.Engine%2C+Infobox_game_engine.Build%2C+Infobox_game.Released&limit={limit}&offset={offset}&format={format}".format(  # NOQA: E501
            limit=cls.PAGE_SIZE,
            offset=offset,
            format=export_format
        )
        headers = {
            "User-Agent": cls.USER_AGENT
        }

        print("> Fetching games page: {}".format(games_page_url))

        response = requests.get(games_page_url, headers=headers)
        if response.text:
            games_json = json.loads(response.text)["cargoquery"]
        else:
            games_json = []

        # sample:
        # {"cargoquery":[
        # {"title":{
        # "Page":"! That Bastard Is Trying To Steal Our Gold !",
        # "Engine":"Engine:Unity",
        # "Build":"6.18.3.761",
        # "Released":"2018-05-04;2018-05-04;2018-05-04"
        # }}
        # ]}

        games = [
            (
                game["title"]["Page"],
                game["title"]["Engine"][len(cls.ENGINE_PREFIX):],
                game["title"]["Build"],
                # A game can have multiple release dates, we simplify by taking the first one
                game["title"]["Released"].split(";")[0].split("-")[0] if game["title"]["Released"] else ""
            )
            for game in games_json
        ]  # type: List[Tuple[str, str, str, str]]

        return games

    @classmethod
    def generalize_game_engines(cls, games_list_filename: str, generalized_games_output_filename: str) -> None:
        count = 0
        engine_mapping = cls._combined_engine_versions_map()

        games = cls._load_games_from_csv(games_list_filename)

        generalized_games = [(
                game[0],
                engine_mapping[game[1]] if game[1] in engine_mapping else game[1],
                game[3],
            ) for game in games]

        with open(generalized_games_output_filename, "w", newline="") as csv_file_handle:
            csv_writer = csv.writer(csv_file_handle, delimiter=cls.CSV_SEPARATOR, quotechar=cls.CSV_QUOTE_CHAR,
                                    quoting=csv.QUOTE_ALL)
            csv_writer.writerow(cls.GENERALIZED_GAMES_CSV_HEADER_ROW)

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
    def _load_games_from_csv(cls, games_list_filename: str) -> List[Tuple[str, str, str, str]]:
        games = []  # type: List[Tuple[str, str, str, str]]

        with open(games_list_filename, newline="") as csv_file_handle:
            csv_reader = csv.reader(csv_file_handle, delimiter=cls.CSV_SEPARATOR, quotechar=cls.CSV_QUOTE_CHAR)
            for index, row in enumerate(csv_reader):
                if (index == 0):
                    continue
                games.append(cast(Tuple[str, str, str, str], tuple(row)))

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


if __name__ == "__main__":

    engines_csv = "engines_list.csv"
    games_csv = "games.csv"
    generalized_games_csv = "games_generalized.csv"

    data = FetchPCGWData()

    data.fetch_game_engines_list_to_csv(engines_csv)
    data.fetch_games_from_cargo_page(games_csv)
    data.generalize_game_engines(games_csv, generalized_games_csv)

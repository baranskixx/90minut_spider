from minut90_finder.items import Player, Season, PlayerImage
from scrapy.exporters import JsonLinesItemExporter
from itemadapter import ItemAdapter
from dataclasses import asdict
import json
import datetime
import os


class BirthDatePipeline:
    MONTHS = {
        "stycznia": 1,
        "lutego": 2,
        "marca": 3,
        "kwietnia": 4,
        "maja": 5,
        "czerwca": 6,
        "lipca": 7,
        "sierpnia": 8,
        "września": 9,
        "października": 10,
        "listopada": 11,
        "grudnia": 12
    }

    def process_item(self, item, spider):
        if isinstance(item, Player):
            try:
                old_date_split = item.birth_date.split(" ")
                year = int(old_date_split[2])
                month = self.MONTHS[old_date_split[1]]
                day = int(old_date_split[0])
                birth_date = str(datetime.date(year, month, day))
            except BaseException:
                birth_date = ""
            finally:
                item.birth_date = birth_date
        return item


class LeagueStatsPipeline:
    ALLOWED_LEAGUES = [
        "LM", "LE", "LKE", "IT",  # european cups
        "Ekstraklasa", "I liga", "PP", "SP"  # polish leagues and cups
    ]

    def process_item(self, item, spider):
        if isinstance(item, Season):
            item.league_stats_list = list(
                filter(
                    lambda league_stats: league_stats.league_name in self.ALLOWED_LEAGUES,
                    item.league_stats_list
                )
            )
        return item


class ItemExportPipeline:
    PLAYERS_PATH = "data/players.jsonl"
    SEASONS_PATH = "data/seasons.jsonl"
    IMG_PATH = "data/img/{}.png"
    players_file = None
    players_exporter = None
    seasons_file = None
    seasons_exporter = None

    def open_spider(self, spider):
        self.players_file = open(self.PLAYERS_PATH, "wb+")
        self.players_exporter = JsonLinesItemExporter(self.players_file)
        self.seasons_file = open(self.SEASONS_PATH, "wb+")
        self.seasons_exporter = JsonLinesItemExporter(self.seasons_file)

    def close_spider(self, spider):
        self.players_file.close()
        self.seasons_file.close()

    def get_exporter(self, item):
        return self.players_exporter if isinstance(item, Player) else self.seasons_exporter

    def process_item(self, item, spider):
        if isinstance(item, PlayerImage):
            if item.img is not None:
                file_path = self.IMG_PATH.format(str(item.player_id))
                with open(file_path, "wb+") as img_file:
                    img_file.write(item.img)
        else:
            exporter = self.get_exporter(item)
            exporter.export_item(ItemAdapter(item).asdict())
        return item


class ClubsPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, Player):
            item.polish_clubs = [club for club in item.polish_clubs
                                 if "(juniorzy)" not in club
                                 and "(ME)" not in club
                                 and "(PE)" not in club
                                 ]

        return item


class PlayerNamePipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, Player):
            affected_fields = ['first_name', 'last_name']
            for field in affected_fields:
                field_val = getattr(item, field)
                if '(' in field_val:
                    open_bracket_index = field_val.find('(')
                    close_bracket_index = field_val.find(')')
                    setattr(item, field, field_val[open_bracket_index+1:close_bracket_index])

        return item

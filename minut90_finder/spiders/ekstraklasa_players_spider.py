from urllib.parse import urlparse, parse_qs
from minut90_finder.items import Player, LeagueStats, Season, PlayerImage
from minut90_finder.settings import PARSE_IMGS
from scrapy.http import Response
import scrapy
import requests


class UrlParser:

    @staticmethod
    def get_url_parameters_from_response(params: list[str], response: scrapy.http.Response):
        parsed_response_url = urlparse(response.url)
        response_url_params = parse_qs(parsed_response_url.query)
        params_dict = {}

        for param in params:
            params_dict[param] = response_url_params.get(param, None)[0]
        return params_dict


class EkstraklasaPlayersSpider(scrapy.Spider):
    name = 'ekstraklasa_players_spider'
    allowed_domains = ['90minut.pl']

    LINK_TEXT_CONTAINS_XPATH = "//a[contains(text(), '{}')]//@href"
    LINK_HREF_CONTAINS_XPATH = "//a[contains(@href, '{}')]//@href"
    PLAYER_NAME_XPATH = "//b[.='Imię']/parent::td/following-sibling::td[1]/text()"
    PLAYER_SURNAME_XPATH = "//b[.='Nazwisko']/parent::td/following-sibling::td[1]/text()"
    PLAYER_NATIONALITIES_XPATH = "//b[.='Kraj']/parent::td/following-sibling::td[1]/img/@title"
    BIRTH_DATE_XPATH = "//b[.='Data urodzenia']/parent::td/following-sibling::td[1]/text()"
    IMG_URL_XPATH = "//img[contains(@src, 'players')]/@src"
    ACHIEVEMENTS_XPATH = "//tr[td[2]/img[@title=\"Polska\"]]/td[5]"

    WON_TROPHIES_XPATH = "//text()[contains(., '{}')]"
    CLUBS_XPATH = "//img[@title=\"Polska\"]/following-sibling::a[1]"

    def parse_main_page(self, response: scrapy.http.Response, **kwargs):
        # jump to 'ligowcy' page to find all players that ever played in highest polish 
        all_time_first_division_players_xpath = self.LINK_HREF_CONTAINS_XPATH.format('ligowcy')
        all_time_first_division_players_url = response.xpath(all_time_first_division_players_xpath).get()
        all_time_first_division_players_url = response.urljoin(all_time_first_division_players_url)

        yield scrapy.Request(
            url=all_time_first_division_players_url,
            callback=self.parse_first_division_players_group_page
        )

    def parse_first_division_players_group_page(self, response: scrapy.http.Response, **kwargs):
        # in that page players are group by start of their name
        # we go through each page to find all players
        all_time_first_division_players_groups_xpath = self.LINK_HREF_CONTAINS_XPATH.format('ligowcy.php?')
        all_time_first_division_players_urls = response.xpath(all_time_first_division_players_groups_xpath).getall()
        all_time_first_division_players_urls = list(
            map(
                lambda page_url: response.urljoin(page_url),
                all_time_first_division_players_urls
            )
        )

        for url in all_time_first_division_players_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_first_division_players_starting_on_letter_page
            )

    def parse_first_division_players_starting_on_letter_page(self, response: scrapy.http.Response, **kwargs):
        # we have to go to player's career page in order to get player detailed stats
        first_division_players_career_xpath = self.LINK_HREF_CONTAINS_XPATH.format('kariera.php?')
        first_division_players_urls = response.xpath(first_division_players_career_xpath).getall()
        first_division_players_urls = list(
            map(
                lambda page_url: response.urljoin(page_url),
                first_division_players_urls
            )
        )

        for url in first_division_players_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_player_career_page
            )

    def parse_player_career_page(self, response: scrapy.http.Response, **kwargs):
        main_table_xpath = '//table[contains(@class, "main")]'

        main_tables = response.xpath(main_table_xpath)
        general_stats_table = main_tables[0]
        first_name = general_stats_table.xpath(self.PLAYER_NAME_XPATH).get()
        last_name = general_stats_table.xpath(self.PLAYER_SURNAME_XPATH).get()
        nationalities = general_stats_table.xpath(self.PLAYER_NATIONALITIES_XPATH).getall()
        birth_date = general_stats_table.xpath(self.BIRTH_DATE_XPATH).get()
        clubs_table = main_tables[1] if len(main_tables) > 1 else None
        if clubs_table:
            club_links = clubs_table.xpath(self.CLUBS_XPATH)
            clubs_set = set([club_link.xpath("string()").get() for club_link in club_links])
            achievements = clubs_table.xpath(self.ACHIEVEMENTS_XPATH)
            achievements = [a.xpath("string()").get() for a in achievements]
            league_trophies = len([a for a in achievements if "mistrzostwo" in a])
            national_cup_trophies = len([a for a in achievements if "puchar krajowy" in a])
            super_cup_trophies = len([a for a in achievements if "superpuchar" in a])

        else:
            clubs_set = set()
            league_trophies = 0
            national_cup_trophies = 0
            super_cup_trophies = 0

        player_id = int(
            UrlParser.get_url_parameters_from_response(
                ['id'],
                response
            )['id']
        )

        player = Player(
            first_name=first_name,
            last_name=last_name,
            nationalities=nationalities,
            birth_date=birth_date,
            player_id=player_id,
            polish_clubs=list(clubs_set),
            league_trophies=league_trophies,
            national_cup_trophies=national_cup_trophies,
            super_cup_trophies=super_cup_trophies
        )
        yield player
        if PARSE_IMGS:
            img_url = response.xpath(self.IMG_URL_XPATH).get()
            http_response = requests.get(img_url, stream=True) if img_url is not None else None
            img_bin = None
            if img_url is not None and http_response.status_code == 200:
                img_bin = http_response.content

            player_image = PlayerImage(player_id, img_bin)
            yield player_image

        player_season_pages_xpath = self.LINK_HREF_CONTAINS_XPATH.format('wystepy.php?')
        player_season_pages_urls = response.xpath(player_season_pages_xpath).getall()
        player_season_pages_urls = list(
            map(
                lambda page_url: response.urljoin(page_url),
                player_season_pages_urls
            )
        )
        for url in player_season_pages_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_player_season
            )

    def parse_player_season(self, response: Response, **kwargs):
        main_table_xpath = '//table[contains(@class, "main")]'
        rows_xpath = './/tr[@bgcolor="#F5F5F5"]'
        main_tables = response.xpath(main_table_xpath)

        if len(main_tables) >= 3:
            stats_table = main_tables[2]
            league_stats_list = []

            for row in stats_table.xpath(rows_xpath):
                data_normal = row.xpath('.//td//text()').extract()
                data_bold = row.xpath('.//td//b//text()').extract()

                league_name = data_normal[1]
                club_name = data_normal[0]
                games_played = data_bold[0]
                goals_scored = data_bold[1]
                yellow_cards = data_normal[-2]
                red_cards = data_normal[-1]
                minutes_played = data_normal[-6]
                new_stats = LeagueStats(
                    club_name=club_name,
                    league_name=league_name,
                    games_played=games_played,
                    goals_scored=goals_scored,
                    yellow_cards=yellow_cards,
                    red_cards=red_cards,
                    minutes_played=minutes_played
                )
                league_stats_list.append(new_stats)
            url_params = UrlParser.get_url_parameters_from_response(['id', 'id_sezon'], response)

            player_id = url_params['id']
            season_id = url_params['id_sezon']

            yield Season(player_id, season_id, league_stats_list)

    def start_requests(self):
        yield scrapy.Request(
            'http://www.90minut.pl',
                 callback=self.parse_main_page
        )

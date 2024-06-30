from dataclasses import dataclass


@dataclass
class LeagueStats:
    club_name: str
    league_name: str
    games_played: int
    goals_scored: int
    yellow_cards: int
    red_cards: int
    minutes_played: int


@dataclass
class Season:
    player_id: int
    season_id: int
    league_stats_list: list[LeagueStats]


@dataclass
class Player:
    player_id: int
    first_name: str
    last_name: str
    nationalities: list[str]
    birth_date: str
    polish_clubs: list[str]
    league_trophies: int
    national_cup_trophies: int
    super_cup_trophies: int


@dataclass
class PlayerImage:
    player_id: int
    img: bytes

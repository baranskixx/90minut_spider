# 90minut_spider

Scrapy spider to extract data from [90minut](http://www.90minut.pl/) - the most extended site about polish football
players and teams

## Usage

## Results

Result of running the script:

- **players.jsonl** - JSONLines file containing data about every player, that played in Polish top tier league - **'
  Ekstraklasa'** (before known also as 'I Liga') - over 9000 players
- **seasons.json** - JSONLines file containing info about every player's season, with detailed information about
  appearances, goals scored, cards etc
- **/img** - directory containing photos of all players (for many players the photos are missing, mainly for players
  that played long time ago)

## Sample entries

### Players:

```
{
  "player_id": 41470,
  "first_name": "Mikael",
  "last_name": "Ishak",
  "nationalities": [
    "Szwecja",
    "Syria"
  ],
  "birth_date": "1993-03-31",
  "polish_clubs": [
    "Lech Poznań"
  ],
  "league_trophies": 1,
  "national_cup_trophies": 0,
  "super_cup_trophies": 0
}
```

### Seasons: 

```
{
  "player_id": "41470",
  "season_id": "101",
  "league_stats_list": [
    {
      "club_name": "Lech Poznań",
      "league_name": "Ekstraklasa",
      "games_played": "23",
      "goals_scored": "11",
      "yellow_cards": "4",
      "red_cards": "0",
      "minutes_played": "1731"
    },
    {
      "club_name": "Lech Poznań",
      "league_name": "LKE",
      "games_played": "17",
      "goals_scored": "8",
      "yellow_cards": "2",
      "red_cards": "0",
      "minutes_played": "1341"
    },
    {
      "club_name": "Lech Poznań",
      "league_name": "LM",
      "games_played": "2",
      "goals_scored": "1",
      "yellow_cards": "0",
      "red_cards": "0",
      "minutes_played": "169"
    },
    {
      "club_name": "Lech Poznań",
      "league_name": "PP",
      "games_played": "1",
      "goals_scored": "0",
      "yellow_cards": "0",
      "red_cards": "0",
      "minutes_played": "19"
    }
  ]
}
```


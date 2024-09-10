import os

import pandas as pd
import yaml
from espn_api.football import League
from yfpy.query import YahooFantasySportsQuery


def strip_title_from_name(s):
    """
    :param s: name
    :return: removes jr and III from s
    """
    s = s.replace(' Jr.', '')
    s = s.replace(" III", '')
    s = s.replace(" II", '')
    s = s.replace("'", '')
    return s


def get_player_name(player_name):
    if player_name.ascii_last is None:
        player_name.ascii_last = ""
    last_name = strip_title_from_name(player_name.ascii_last)
    return f"{player_name.ascii_first} {last_name}"


def get_secrets():
    with open("conf.yaml") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data


def get_rostered_players_yahoo(league_id, output_fname):
    auth_dir = './'
    d = get_secrets()
    yahoo_query = YahooFantasySportsQuery(
        auth_dir,
        league_id,
        game_id=None,
        game_code="nfl",
        offline=False,
        all_output_as_json_str=False,
        consumer_key=d['yahoo']['consumer_key'],
        consumer_secret=d['yahoo']['consumer_secret'],
        browser_callback=True
    )
    teams = yahoo_query.get_league_teams()

    rostered_players = []
    for team_id in range(1, len(teams) + 1):
        team_rosters = yahoo_query.get_team_roster_by_week(team_id, 16)
        for p in team_rosters.players:
            rostered_players.append(get_player_name(p.name))
    df = pd.DataFrame({
        "Name": rostered_players
    })
    df.to_csv(output_fname, index=False)


def get_rostered_players_espn(league_id, output_fname):
    year = 2024
    secrets = get_secrets()
    espn_s2 = secrets['espn']['espn_s2']
    swid = secrets['espn']['swid']

    league = League(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid)
    teams = league.teams
    full_roster = []
    for t in teams:
        for p in t.roster:
            full_roster.append(strip_title_from_name(p.name))
    df = pd.DataFrame({
        "Name": full_roster
    })
    df.to_csv(output_fname, index=False)


def save_rosters():
    if not os.path.exists('scr'):
        os.makedirs('scr')

    secrets = get_secrets()
    for league in secrets['leagues']:
        roster_fname = f"scr/{league['league_name']}.csv"
        if league['website'] == 'yahoo':
            get_rostered_players_yahoo(league['league_id'], roster_fname)
        elif league['website'] == 'espn':
            get_rostered_players_espn(league['league_id'], roster_fname)
        else:
            raise ValueError("Only support Yahoo and ESPN Leagues")


def main():
    save_rosters()


if __name__ == "__main__":
    main()

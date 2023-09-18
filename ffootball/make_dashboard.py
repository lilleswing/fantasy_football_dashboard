import nfl_data_py as nfl
import pandas as pd
import numpy as np
import copy

from ffootball.get_rosters import get_secrets


def bootstrap_median(weekly_data, score_column, player_name, window=6):
    player_df = weekly_data[weekly_data['player_display_name'] == player_name]
    last_6 = player_df[score_column].values[-1 * window:]
    if len(last_6) == 0:
        return 0, 0, 0
    bootstraps = np.random.choice(last_6, size=(100, window))
    means = np.mean(bootstraps, axis=1)
    return np.median(means), np.std(means), len(last_6)


def bootstrap_2023(weekly_data, score_column, player_name, window=6):
    player_df = weekly_data[weekly_data['player_display_name'] == player_name]
    last_6 = player_df[player_df['season'] == 2023][score_column].values
    if len(last_6) == 0:
        return 0, 0, 0
    bootstraps = np.random.choice(last_6, size=(100, window))
    means = np.mean(bootstraps, axis=1)
    return np.median(means), np.std(means), len(last_6)


def add_rostered_players(df, fname):
    my_df = copy.deepcopy(df)
    rostered_players = pd.read_csv(f'scr/{fname}.csv')
    rostered_players = set(rostered_players['Name'])
    my_df['is_rostered'] = [x in rostered_players for x in my_df['Name']]
    my_df.to_html(f"scr/{fname}.html")

    unrostered = my_df[~my_df['is_rostered']]
    unrostered = unrostered[unrostered['games_played_2023'] >= 1]
    unrostered = unrostered.sort_values('ADV_2023', ascending=False)
    unrostered.to_html(f"scr/{fname}_unrostered.html")


def calculate_advs(weekly_data, is_ppr, league_name):
    """
    :param weekly_data:
    :param is_ppr:  str of ("none", 'half', 'full')
    :param league_name:
    :return:
    """
    if is_ppr == 'half':
        score_column = 'half_ppr'
    elif is_ppr == 'none':
        score_column = 'fantasy_points'
    elif is_ppr == 'full':
        score_column = 'fantasy_points_ppr'
    else:
        raise ValueError(f"League type of {is_ppr} is not supported")
    weekly_data = copy.deepcopy(weekly_data)
    position_lookup = {}
    for n, p in zip(weekly_data['player_display_name'], weekly_data['position']):
        position_lookup[n] = p

    players = set(weekly_data['player_display_name'])
    player_adv = {}
    player_adv_2023 = {}

    for p in players:
        player_adv[p] = bootstrap_median(weekly_data, score_column, p, window=6)
        player_adv_2023[p] = bootstrap_2023(weekly_data, score_column, p)
    table = []
    for k in player_adv.keys():
        row = [k, position_lookup[k], *player_adv[k], *player_adv_2023[k]]
        table.append(row)
    player_adv_df = pd.DataFrame(table, columns=['Name', 'position', 'ADV', 'variance', 'games_played', 'ADV_2023',
                                                 'variance_2023', 'games_played_2023'])
    player_adv_df = player_adv_df.sort_values('ADV', ascending=False)
    player_adv_df['rank'] = [x + 1 for x in range(len(player_adv_df))]
    add_rostered_players(player_adv_df, league_name)


def main():
    weekly_data = nfl.import_weekly_data(years=[2022, 2023])
    weekly_data = weekly_data.sort_values('fantasy_points', ascending=False)
    weekly_data = weekly_data.sort_values(['season', 'week'])
    weekly_data['half_ppr'] = [(x + y) / 2 for x, y in
                               zip(weekly_data['fantasy_points'], weekly_data['fantasy_points_ppr'])]

    secrets = get_secrets()
    for league in secrets['leagues']:
        calculate_advs(weekly_data, league['ppr'], league['league_name'])


if __name__ == "__main__":
    main()

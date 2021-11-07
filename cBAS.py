import pandas as pd
from pprint import pprint
from progressbar import ProgressBar
from datetime import datetime
from sportsipy.ncaab.boxscore import Boxscore
from sportsipy.ncaab.conferences import Conferences
from sportsipy.ncaab.roster import Roster, Player
import openpyxl

def cBAS():
    # measure time elapsed
    start_timestamp = datetime.today()
    
    # on-screen welcome prompt
    print('''
    Welcome to the College Basketball Analysis System (cBAS)
        > Follow on-screen instructions to properly query
          data from Sports Reference. Files will be saved
          to the same directory where the cBAS file lives
    ''')

    # gather all men's CBB D1 teams
    print('|| Gathering Division I teams  ||')
    complete_conferences = Conferences().conferences
    print('|| Successful data query ||')
    
    # create dictionary of all men's CBB D1 teams {team_id:team_name}
    complete_teams = {}
    for conference in complete_conferences:
        for team in complete_conferences[conference]['teams']:
            complete_teams[team] = complete_conferences[conference]['teams'][team]

    # enter home team name, away team name
    home_team, away_team = input('<<Enter home team name>> ').title(), input('<<Enter away team name>> ').title()
    home_id, away_id = '-'.join(home_team.split(' ')).lower(), '-'.join(away_team.split(' ')).lower()

    # verify home_team, away_team exist in complete_conferences
    while (home_team not in complete_teams.values()):
        print('!! {} not found in Division 1 - please reenter !!'.format(home_team))
        home_team = input('<<Enter home team name>> ').title()
        home_id = '-'.join(home_team.split(' ')).lower()
    while (away_team not in complete_teams.values()):
        print('!! {} not found in Division 1 - please reenter !!'.format(away_team))
        away_team = input('<<Enter away team name>> ').title()
        away_id = '-'.join(away_team.split(' ')).lower()

    # output successful entry of team names
    final_string = 'GAME SELECTED: ' + home_team + ' (home) vs. ' + away_team + ' (away)'
    print('=' * len(final_string)); print(final_string); print('=' * len(final_string))

    # create dictionary for teams {player_id: player_name}
    hroster_pbar, aroster_pbar = ProgressBar(), ProgressBar()
    home_roster, away_roster = Roster(home_id), Roster(away_id)
    home_roster_dict = {player.player_id : player.name for player in hroster_pbar(home_roster.players)}
    away_roster_dict = {player.player_id : player.name for player in aroster_pbar(away_roster.players)}

    # create empty dataframes for pd.concat(player's data)
    home_dataframe, away_dataframe = pd.DataFrame(), pd.DataFrame()
    # used for filtering previous season, current season, and career statistics
    current_year = int(datetime.today().date().year)
    current_year_str = str(current_year) + '-' + str(current_year + 1)[2:]
    previous_year_str = str(current_year - 1) + '-' + str(current_year)[2:]
    
    # home team dataframe - saved as home_results
    print('|| {} data loading ||'.format(home_team))
    home_pbar = ProgressBar()
    for player in home_pbar(home_roster_dict):
        player_df = Player(player).dataframe
        player_df['player_name'] = home_roster_dict[player]
        home_dataframe = pd.concat([home_dataframe, player_df])

    home_results = home_dataframe.reset_index().rename(columns={'level_0':'season'})
    home_results = home_results[home_results['season'].isin([current_year_str, previous_year_str, 'Career'])]

    home_results['rebounds'] = home_results['defensive_rebounds'] + home_results['offensive_rebounds']
    home_results = home_results[['player_name', 'position', 'height', 'weight',
                'season', 'games_played', 'minutes_played',
                'points', 'rebounds', 'assists',
                'field_goal_percentage', 'free_throw_percentage']]
    
    # away team dataframe - saved as away_results
    print('|| {} data loading ||'.format(away_team))
    away_pbar = ProgressBar()
    for player in away_pbar(away_roster_dict):
        player_df = Player(player).dataframe
        player_df['player_name'] = away_roster_dict[player]
        away_dataframe = pd.concat([away_dataframe, player_df])

    away_results = away_dataframe.reset_index().rename(columns={'level_0':'season'})
    away_results = away_results[away_results['season'].isin([current_year_str, previous_year_str, 'Career'])]

    away_results['rebounds'] = away_results['defensive_rebounds'] + away_results['offensive_rebounds']
    away_results = away_results[['player_name', 'position', 'height', 'weight',
                'season', 'games_played', 'minutes_played',
                'points', 'rebounds', 'assists',
                'field_goal_percentage', 'free_throw_percentage']]

    # final touch up: convert/transform column types/values
    ints = ['weight', 'games_played', 'minutes_played', 'points', 'rebounds', 'assists']
    floats = ['field_goal_percentage', 'free_throw_percentage']

    for col in ints:
        home_results[col] = home_results[col].astype('int64')
        away_results[col] = away_results[col].astype('int64')
    for col in floats:
        home_results[col] = home_results[col].fillna(0).astype('float64') * 100
        away_results[col] = away_results[col].fillna(0).astype('float64') * 100
    
    # save to local directory: "HomeTeam-AwayTeam-SaveDate.xlsx"
    save_date = datetime.today().date().strftime('%Y-%m-%d')
    save_time = datetime.today().time().strftime('%H:%M:%S')
    with pd.ExcelWriter('{}-{}-{}.xlsx'.format(home_team, away_team, save_date)) as output_xlsx:  
        home_results.to_excel(output_xlsx, sheet_name='Home-Data')
        away_results.to_excel(output_xlsx, sheet_name='Away-Data')
    
    # update user
    print('''
    cBAS system successfully gathered and stored data
        > File name: {}-{}-{}
        > Timestamp: {}
    '''.format(home_team, away_team, save_date, save_time))

if __name__ == '__main__':
    cBAS()

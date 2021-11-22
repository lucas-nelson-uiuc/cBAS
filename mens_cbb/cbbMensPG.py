import pandas as pd
import numpy as np
import openpyxl
import os
from progressbar import ProgressBar
from datetime import datetime

from sportsipy.ncaab.boxscore import Boxscore
from sportsipy.ncaab.conferences import Conferences
from sportsipy.ncaab.roster import Roster, Player


class TeamData():

    '''
    Class for individual team. Contains surface-level description of team
    (team name), relational database key (team_id), and parameters
    necessary for sportsipy functions
    '''

    def __init__(self, team_name, season_year):

        '''
        Initialization of TeamData instance

        Parameters
        ----------
            team_name (str)  : name of the team; verified in Division01_Teams.txt
            season_year (int): year of ongoing or most recent season
        '''

        self.team_name = team_name
        self.team_id = '-'.join(self.team_name.split(' ')).lower()
        self.team_dataframe = pd.DataFrame()
        self.per_game_dataframe = pd.DataFrame()
        self.current_year = season_year
        self.current_year_str = str(self.current_year) + '-' + str(self.current_year + 1)[2:]
        self.previous_year_str = str(self.current_year - 1) + '-' + str(self.current_year)[2:]

    
    def create_team_dataframe(self):

        '''
        Generate pd.DataFrame for each team to be updated and later written
        to .xlsx file at the end of the script

        Self-fulfilling function (i.e. no parameters and no returns)
        '''

        print('> Extracting {}\'s roster'.format(self.team_name))
        team_roster = Roster(self.team_id)
        team_roster_dict = {player.player_id : player.name for player in team_roster.players}

        pbar = ProgressBar()
        print('> Extracting {}\'s data'.format(self.team_name))
        for player in pbar(team_roster_dict):
            player_df = Player(player).dataframe
            player_df['player_name'] = team_roster_dict[player]
            self.team_dataframe = pd.concat([self.team_dataframe, player_df])
        
        self.team_dataframe = self.team_dataframe.reset_index().rename(columns={'level_0':'season'})
        self.team_dataframe = self.team_dataframe[self.team_dataframe['season'].isin([self.current_year_str, self.previous_year_str, 'Career'])]

        self.team_dataframe['rebounds'] = self.team_dataframe['defensive_rebounds'] + self.team_dataframe['offensive_rebounds']
        self.team_dataframe = self.team_dataframe[['player_name', 'position', 'height', 'weight',
                    'season', 'games_played', 'minutes_played',
                    'points', 'rebounds', 'assists',
                    'field_goal_percentage', 'free_throw_percentage']].fillna(0)
    
    def clean_team_dataframe(self):

        '''
        Assign proper data types and convert data to per game statistics
        instead of season-by-season aggregates

        Self-fulfilling function (i.e. no parameters and no returns)
        '''

        ints = ['weight', 'games_played', 'minutes_played', 'points', 'rebounds', 'assists']
        floats = ['field_goal_percentage', 'free_throw_percentage']

        for col in ints:
            self.team_dataframe[col] = self.team_dataframe[col].astype('int64')
        for col in floats:
            self.team_dataframe[col] = self.team_dataframe[col].fillna(0).astype('float64') * 100
    
    def insert_missing_player_data(self):

        '''
        Create empty rows for players who do not have data for previous season,
        current season, or career (empty row generated for seasons that meet
        criteria).

        Returns
        _______
            self.team_dataframe (pd.DataFrame):
                final dataframe for team; each player has three rows for
                previous season, current season, and career (empty if no
                data exists for said row)
        '''

        player_season_dict = {}
        for player, season in zip(self.team_dataframe['player_name'], self.team_dataframe['season']):
            if player not in player_season_dict:
                player_season_dict[player] = [season]
            else:
                player_season_dict[player].append(season)
        
        for player in player_season_dict:
            if self.current_year_str not in player_season_dict[player]:
                append_index = {'player_name':player,
                            'season':self.current_year_str}
                append_data = {col:np.nan for col in self.team_dataframe.columns.drop(['player_name', 'season'])}
                append_index.update(append_data)
                self.team_dataframe = self.team_dataframe.append(pd.Series(append_index), ignore_index=True)
            if self.previous_year_str not in player_season_dict[player]:
                append_index = {'player_name':player,
                            'season':self.previous_year_str}
                append_data = {col:np.nan for col in self.team_dataframe.columns.drop(['player_name', 'season'])}
                append_index.update(append_data)
                self.team_dataframe = self.team_dataframe.append(pd.Series(append_index), ignore_index=True)
                
        self.team_dataframe = self.team_dataframe.sort_values(['player_name', 'season']).reset_index(drop=True)
        self.per_game_dataframe = self.team_dataframe.copy()
    
    def per_game_statistics(self):
        
        per_game = ['minutes_played', 'points', 'rebounds', 'assists']
        
        for col in per_game:
            self.per_game_dataframe[col] = self.per_game_dataframe[col] / self.per_game_dataframe['games_played']
            self.per_game_dataframe[col] = self.per_game_dataframe[col].round(1)
        
        self.per_game_dataframe = self.per_game_dataframe.sort_values(['player_name', 'season']
                                        ).reset_index(drop=True)
        self.per_game_dataframe = self.per_game_dataframe.drop(['player_name', 'position',
                                                                'height', 'weight'], axis=1)
        self.per_game_dataframe.rename(columns={col:f'{col}.PG' for col in self.per_game_dataframe.columns},
                               inplace=True)
        return pd.concat([HomeTeam.team_dataframe, HomeTeam.per_game_dataframe], axis=1)



class ExcelWorksheet():

    '''
    Class for instantiating .xlsx file to write data to
    '''

    def __init__(self, home_dataframe, away_dataframe, home_team, away_team, save_date):

        '''
        Initialize worksheet by passing relevant dataframes and save information

        Parameters
        __________
            home_dataframe (pd.DataFrame): dataframe returned from
                TeamData(home_team, YYYY).team_dataframe
            away_dataframe (pd.DataFrame): dataframe returned from
                TeamData(away_team, YYYY).team_dataframe
            home_team (str)              : name of home team
            away_team (str)              : name of away team
            save_date (datetime)         : date when script executed
        '''

        self.home_dataframe = home_dataframe
        self.away_dataframe = away_dataframe
        self.home_team = home_team
        self.away_team = away_team
        self.save_date = save_date

    def write_to_excel(self):
        with pd.ExcelWriter('{}-{}-{}.xlsx'.format(self.home_team, self.away_team, self.save_date)) as output_xlsx:  
            self.home_dataframe.to_excel(output_xlsx, sheet_name=f'{home_team}-Data')
            self.away_dataframe.to_excel(output_xlsx, sheet_name=f'{away_team}-Data')


if __name__ == '__main__':
    
    print('=' * 65)

    print('''
    Welcome to the College Basketball Analysis Scoresheet System (cBASS)
        > Follow on-screen instructions to properly query
        data from Sports Reference.
        > Files will be saved to the same directory where
        the cBASS file lives.
    ''')

    year_as_of_today = int(datetime.today().date().year)
    home_team, away_team = input('<<Enter home team name>> ').title(), input('<<Enter away team name>> ').title()

    # check if file of division 1 teams exists; if not, create it
    if 'Division01_Teams.txt' not in os.listdir():
        print('> Gathering Division I teams...')
        complete_conferences = Conferences().conferences
        print('> Writing teams to file: "Division01_Teams.txt"')
        complete_teams = {}
        with open('Division01_Teams.txt', 'w') as d1:
            for conference in complete_conferences:
                for team in complete_conferences[conference]['teams']:
                    d1.write('{}\n'.format(complete_conferences[conference]['teams'][team]))

    # open file of division 1 teams for opening
    with open('Division01_Teams.txt', 'r') as d1:
        complete_teams = [team.strip() for team in d1.readlines()]

    # verify home_team, away_team exist in complete_conferences
    while (home_team not in complete_teams):
        print('!! {} not found in Division 1 - please reenter !!'.format(home_team))
        home_team = input('<<Enter home team name>> ').title()
        home_id = '-'.join(home_team.split(' ')).lower()
    while (away_team not in complete_teams):
        print('!! {} not found in Division 1 - please reenter !!'.format(away_team))
        away_team = input('<<Enter away team name>> ').title()
        away_id = '-'.join(away_team.split(' ')).lower()

    # output successful entry of team names
    final_string = 'GAME SELECTED: ' + home_team + ' (home) vs. ' + away_team + ' (away)'
    print('=' * 65); print(final_string); print('=' * 65)

    # create, clean, and write home_team DataFrame
    HomeTeam = TeamData(home_team, year_as_of_today)
    HomeTeam.create_team_dataframe()
    HomeTeam.clean_team_dataframe()
    HomeTeam.insert_missing_player_data()
    home_df = HomeTeam.per_game_statistics()

    # create, clean, and write away_team DataFrame
    AwayTeam = TeamData(away_team, year_as_of_today)
    AwayTeam.create_team_dataframe()
    AwayTeam.clean_team_dataframe()
    AwayTeam.insert_missing_player_data()
    away_df = AwayTeam.per_game_statistics()

    # write results to excel file
    save_date = datetime.today().date().strftime('%Y-%m-%d')
    save_time = datetime.today().time().strftime('%H:%M:%S')
    ExcelWriter = ExcelWorksheet(home_df, away_df, HomeTeam.team_name, AwayTeam.team_name, save_date)
    ExcelWriter.write_to_excel()

    # log results: file name, date saved, time saved
    print('=' * 53)
    print('''
    cBASS system successfully gathered and stored data
        > File name: {}-{}-{}
        > Datestamp: {}
        > Timestamp: {}
    '''.format(home_team, away_team, save_date, save_date, save_time))
    print('=' * 53)


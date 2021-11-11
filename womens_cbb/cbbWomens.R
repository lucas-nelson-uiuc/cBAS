library(wehoop)
library(tidyverse)
library(glue)
library(xlsx)


validate_date = function(query.date) {
  
  while (query.date < 2002 | query.date > as.numeric(format(Sys.Date(), '%Y'))) {
    print(glue('Invalid date entered! Year must exist between 2002 - {format(Sys.Date(), \'%Y\')}'))
    query.date = as.numeric(readline('Enter season end year (e.g. 2022 for 2021-22 season): '))
  }
  
  return(query.date)
  
}

validate_teams = function() {
  
  if (!file.exists('Womens_CBB_Division01_Teams.txt')) {
    wbb.teams = espn_wbb_teams() %>% select(team, team_id)
    write.csv(wbb.teams, 'Womens_CBB_Division01_Teams.txt')
  }
  
  wbb.teams = as_tibble(read.csv('Womens_CBB_Division01_Teams.txt'))
  return(wbb.teams)
  
}

validate_query = function(home.team, away.team) {
  
  while (!(str_to_title(home.team) %in% valid.teams$team)) {
    home.team = str_to_title(readline("Invalid home team! Reenter home team name: "))
  }
  
  while (!(str_to_title(away.team) %in% valid.teams$team)) {
    away.team = str_to_title(readline("Invalid away team! Reenter away team name: "))
  }
  
  print(glue('GAME SELECTED: {home.team} (home) vs. {away.team} (away)'))
  
  return(list(home.team, away.team))
  
}

main = function() {
  valid.start = validate_date(as.numeric(readline('Enter season end year (e.g. 2022 for 2021-22 season): ')))
  valid.teams = validate_teams() %>% select(-X)
  valid.query = validate_query(str_to_title(readline('Enter home team: ')),
                               str_to_title(readline('Enter away team: ')))
  
  # assign home team names
  home.team = valid.query[[1]][1]
  # away.team = valid.teams[[2]][1]
  
  # create information matrix for each team
  home.info = valid.teams %>% filter(team == home.team) %>% select(team_id, team)
  
  # gather previous season game statistics using game IDs
  home.previous_game_ids = load_wbb_team_box(valid.start) %>% filter(team_id == home.info$team_id) %>%
    select(game_id)
  
  print(glue('  > Extracting {valid.start - 1} data for {home.team} ...'))
  dfs = apply(home.previous_game_ids, 1, espn_wbb_game_all)
  
  print(glue('  > Merging {home.team} {valid.start - 1} data.frames ...'))
  player_df_list = list()
  for (i in 1:length(dfs)) {
    player_df_list[[i]] = dfs[[i]]$Player
  }
  
  home.big_data = dplyr::bind_rows(player_df_list) %>%
    filter(team_id == home.info$team_id) %>%
    select(athlete_display_name, min, pts,
           reb, ast) %>%
    group_by(athlete_display_name) %>%
    summarise(
      GP = n(),
      MIN = round(mean(as.numeric(min), na.rm=TRUE), 1),
      PTS = round(mean(as.numeric(pts), na.rm=TRUE), 1),
      RBS = round(mean(as.numeric(reb), na.rm=TRUE), 1),
      AST = round(mean(as.numeric(ast), na.rm=TRUE), 1)
    )
  
  home.shooting_data = dplyr::bind_rows(player_df_list) %>%
    filter(team_id == home.info$team_id) %>%
    select(athlete_display_name, fg, ft) %>%
    extract(fg, c('fga', 'fgm'), '(.)-(.)') %>%
    extract(ft, c('fta', 'ftm'), '(.)-(.)') %>%
    group_by(athlete_display_name) %>%
    summarise(
      FGA = sum(as.numeric(fga)),
      FGM = sum(as.numeric(fgm)),
      FTA = sum(as.numeric(fta)),
      FTM = sum(as.numeric(ftm))
    ) %>%
    mutate(fgp = round(FGA / (FGA + FGM) * 100, 1),
           ftp = round(FTA / (FTA + FTM) * 100, 1)) %>%
    select(athlete_display_name, fgp, ftp)
  
  
  home.prevszn_stats = merge(home.big_data, home.shooting_data, by='athlete_display_name')
  print(glue('  > SUCCESS: {home.team} {valid.start - 1} data gathered'))
  
  
  
  home.current_season = load_wbb_schedule(valid.start + 1) %>% filter(home.id == home.info$team_id)
  
  teams.current_played = home.current_season %>%
    mutate(date = as.Date(date)) %>%
    filter(date < Sys.Date()) %>%
    select(id)
  
  print(glue('  > Extracting {valid.start} data for {home.team} ...'))
  home.played_list = apply(teams.current_played, 1, espn_wbb_game_all)
  
  print(glue('  > Merging {home.team} {valid.start} data.frames ...'))
  current_df_list = list()
  for (i in 1:length(teams.current_played)) {
    current_df_list[[i]] = home.played_list[[i]]$Player
  }
  
  home.current_data = dplyr::bind_rows(current_df_list) %>%
    filter(team_id == home.info$team_id) %>%
    select(athlete_display_name, min, pts,
           reb, ast) %>%
    group_by(athlete_display_name) %>%
    summarise(
      GP = n(),
      MIN = round(mean(as.numeric(min), na.rm=TRUE), 1),
      PTS = round(mean(as.numeric(pts), na.rm=TRUE), 1),
      RBS = round(mean(as.numeric(reb), na.rm=TRUE), 1),
      AST = round(mean(as.numeric(ast), na.rm=TRUE), 1)
    )
  
  home.current_shooting_data = dplyr::bind_rows(current_df_list) %>%
    filter(team_id == home.info$team_id) %>%
    select(athlete_display_name, fg, ft) %>%
    extract(fg, c('fga', 'fgm'), '(.)-(.)') %>%
    extract(ft, c('fta', 'ftm'), '(.)-(.)') %>%
    group_by(athlete_display_name) %>%
    summarise(
      FGA = sum(as.numeric(fga)),
      FGM = sum(as.numeric(fgm)),
      FTA = sum(as.numeric(fta)),
      FTM = sum(as.numeric(ftm))
    ) %>%
    mutate(fgp = round(FGA / (FGA + FGM) * 100, 1),
           ftp = round(FTA / (FTA + FTM) * 100, 1)) %>%
    select(athlete_display_name, fgp, ftp)
  
  home.current_stats = merge(home.current_data, home.current_shooting_data, by='athlete_display_name')
  print(glue('  > SUCCESS: {home.team} {valid.start - 1} data gathered'))
  
  write.xlsx(home.current_stats, glue('{home.team}-{away.team}-{Sys.Date()}.xlsx'))
}

main()
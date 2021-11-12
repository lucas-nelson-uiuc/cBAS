library(wehoop)
library(tidyverse)
library(glue)
library(xlsx)


user.input = function(prompt) {
  if (interactive()) {
    return(readline(prompt))
  } else {
    cat(prompt)
    return(readLines("stdin", n=1))
  }
}

validate_date = function(query.date) {
  
  while (query.date < 2002 | query.date > as.numeric(format(Sys.Date(), '%Y')) + 1) {
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

extract_team_data = function(team.name, valid.start, relative.season) {
  # create key for home.team
  team.info = valid.teams %>% filter(team == team.name)
  
  # update date query if previous season requested
  if (relative.season == 'previous') {valid.start = valid.start - 1}
  print(glue('  == QUERY == {team.name} (team) {valid.start - 1}-{valid.start} (season)'))
  
  # gather previous season game statistics using game IDs
  team.previous_game_ids = load_wbb_team_box(valid.start) %>% 
    filter(team_id == team.info$team_id) %>%
    select(game_id)
  
  if (relative.season == 'lastfive') {team.previous_game_ids %>% slice_tail(n=5)}
  
  print(glue('    ... Extracting {valid.start - 1}-{valid.start} data for {team.name}'))
  dfs = apply(team.previous_game_ids, 1, espn_wbb_game_all)
  
  print(glue('    ... Merging {team.name} {valid.start - 1}-{valid.start} data.frames'))
  player_df_list = list()
  for (i in 1:length(dfs)) {
    player_df_list[[i]] = dfs[[i]]$Player
  }
  
  team.statistics_batch_01 = dplyr::bind_rows(player_df_list) %>%
    filter(team_id == team.info$team_id) %>%
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
  
  team.statistics_batch_02 = dplyr::bind_rows(player_df_list) %>%
    filter(team_id == team.info$team_id) %>%
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
  
  # merge data.frames on athlete's name and output/return successful result
  team.statistics = merge(team.statistics_batch_01, team.statistics_batch_02,
                          by='athlete_display_name')
  print(glue('  == SUCCESS == {team.name} {valid.start - 1} data gathered'))
  
  return(team.statistics)
}

format_team_data = function(previous_dataframe, lastfive_dataframe, current_dataframe) {
  previous_dataframe %>%
    dplyr::bind_rows(lastfive_dataframe) %>%
    dplyr::bind_rows(current_dataframe) %>%
    arrange(athlete_display_name) %>%
    select(athlete_display_name, season, GP, MIN,
           PTS, RBS, AST, fgp, ftp)
}

main = function() {
  start.input = user.input('Enter season end year (e.g. 2022 for 2021-22 season): ')
  valid.start = validate_date(as.numeric(start.input))
  home.input = str_to_title(user.input('Enter home team: '))
  away.input = str_to_title(user.input('Enter away team: '))
  valid.query = validate_query(home.input, away.input)
  
  # assign home team names
  home.team = valid.query[[1]][1]
  away.team = valid.query[[2]][1]
  
  # extract previous season and current season data.frames per team
  home.current_dataframe = extract_team_data(home.team, valid.start, 'current') %>%
    mutate(season = glue('{valid.start-1}-{valid.start-0-2000}'))
  home.lastfive_dataframe = extract_team_data(home.team, valid.start, 'lastfive') %>%
    mutate(season = 'Previous5')
  home.previous_dataframe = extract_team_data(home.team, valid.start, 'previous') %>%
    filter(athlete_display_name %in% home.current_dataframe$athlete_display_name) %>%
    mutate(season = glue('{valid.start-2}-{valid.start-1-2000}'))
  away.current_dataframe = extract_team_data(away.team, valid.start, 'current') %>%
    mutate(season = glue('{valid.start-1}-{valid.start-0-2000}'))
  away.lastfive_dataframe = extract_team_data(away.team, valid.start, 'lastfive') %>%
    mutate(season = 'Previous5')
  away.previous_dataframe = extract_team_data(away.team, valid.start, 'previous') %>%
    filter(athlete_display_name %in% home.current_dataframe$athlete_display_name) %>%
    mutate(season = glue('{valid.start-2}-{valid.start-1-2000}'))
 
  home.results = format_team_data(home.previous_dataframe,
                                  home.lastfive_dataframe,
                                  home.current_dataframe)
  away.results = format_team_data(away.previous_dataframe,
                                  away.lastfive_dataframe,
                                  away.current_dataframe)
  
  wb = createWorkbook()
  home.data = createSheet(wb, sheetName='Home_Data')
  addDataFrame(home.results, home.data)
  away.data = createSheet(wb, sheetName='Away_Data')
  addDataFrame(away.results, away.data)
  saveWorkbook(wb, glue('{home.team}-{away.team}-{Sys.Date()}.xlsx'))
  
}

valid.teams = validate_teams() %>% select(-X)
main()

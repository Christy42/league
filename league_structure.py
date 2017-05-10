"""
12 teams per league.

League structure has 3 multiplier in each tier.  Labelled by greek letter followed by number.
The top team from each league(except the top) promotes automatically.

The second places team go into a play off system

The bottom 3 teams in each league (Except any in the bottom tier) demote automatically.  The 4th last team joins the 3
second placed teams in the play off system.  Only the winner retains/promotes.

Demotion and promotion are random.  Which of the teams go into each pool in the play offs is random (except that each
pool should contain 3 teams attempting promotion and 1 avoiding demotion).
"""
import yaml
import os
import csv
import pandas

from shutil import copyfile
from random import randint
from american_football import game

from create_team import create_team, remove_player, ensure_team_has_minimum
from league import LeagueTable

from training_modules import match_training


def create_tier_from_lists(dict_of_teams):
    """
    :param dict_of_teams: a dict of dicts, labelled by tier followed by league- each of these is a list of 12 team ids
    :return:
    """
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams"
    with open(os.environ['FOOTBALL_HOME'] + "//leagues//season_number.yaml", "r") as file:
        season_number = yaml.safe_load(file)
    base_name = "leagues//" + str(season_number)
    if not os.path.exists(base_name):
        os.makedirs(base_name)

    for tier in dict_of_teams:
        if not os.path.exists(base_name + "//" + str(tier)):
            os.makedirs(base_name + "//" + str(tier))
        for league_name in dict_of_teams[tier]:
            league = {}

            for team in dict_of_teams[tier][league_name]:
                with open(team_folder + "//teams//" + team + ".yaml", "r") as team_file:
                    team_stat = yaml.safe_load(team_file)
                team_name = team_stat["team name"]
                team_stat["league name"] = league_name
                with open(team_folder + "//teams//" + team + ".yaml", "w") as team_file:
                    yaml.safe_dump(team_stat, team_file)
                league.update({team: team_name})
            if not os.path.exists(base_name + "//" + str(tier) + "//" + league_name):
                os.makedirs(base_name + "//" + str(tier) + "//" + league_name)

            with open(base_name + "//" + str(tier) + "//" + league_name + "//" + "teams.yaml", "w") as file:
                yaml.safe_dump({"leagues name": league_name, "teams": list(league.keys())}, file)
            if not os.path.isfile(base_name + "//cup_fixtures.yaml"):
                with open(base_name + "//cup_fixtures.yaml", "w"):
                    pass
            with open(base_name + "//cup_fixtures.yaml", "r") as file:
                cup_teams = yaml.safe_load(file)
            if cup_teams is None:
                cup_teams = []
            else:
                cup_teams = cup_teams[1:]
            cup_teams += league
            with open(base_name + "//cup_fixtures.yaml", "w") as file:
                yaml.safe_dump([1] + cup_teams, file)
            league_stat = LeagueTable(league, base_name + "//" + str(tier) + "//" + league_name + "//schedule.yaml",
                                      base_name + "//" + str(tier) + "//" + league_name + "//table.csv",
                                      league_name)
            league_stat.create_schedule()
            league_stat.initialise_file()


def create_tier(tier):
    with open(os.environ['FOOTBALL_HOME'] + "//leagues//season_number.yaml", "r") as file:
        season_number = yaml.safe_load(file)
    base_name = os.environ['FOOTBALL_HOME'] + "//leagues//" + str(season_number)
    if not os.path.exists(base_name):
        os.makedirs(base_name)
    for i in range(max(3 ** (tier - 1), 1)):
        league_name = chr(tier - 1 + ord('a')) + " " + str(i)
        if not os.path.exists(base_name + "//" + str(tier)):
            os.makedirs(base_name + "//" + str(tier))
        team = {}
        country = ["Ireland", "United Kingdom", "United States of America", "Canada", "Australia"]
        for _ in range(12):
            t = create_team(country[randint(0, 4)], league_name)
            team.update({t: t})
        if not os.path.exists(base_name + "//" + str(tier) + "//" + league_name):
            os.makedirs(base_name + "//" + str(tier) + "//" + league_name)
        with open(base_name + "//" + str(tier) + "//" + league_name + "//" + "teams.yaml", "w") as file:
            yaml.safe_dump({"leagues name": league_name, "teams": list(team.keys())}, file)
        with open(base_name + "//cup_fixtures.yaml", "r") as file:
            cup_teams = yaml.safe_load(file)
        if cup_teams is None:
            cup_teams = []
        else:
            cup_teams = cup_teams[1:]
        cup_teams += list(team.keys())
        with open(base_name + "//cup_fixtures.yaml", "w") as file:
            yaml.safe_dump([1] + cup_teams, file)
        league = LeagueTable(team, base_name + "//" + str(tier) + "//" + league_name + "//schedule.yaml",
                             base_name + "//" + str(tier) + "//" + league_name + "//table.csv", league_name)
        league.create_schedule()
        league.initialise_file()


def play_week(week_number, season_number):
    league_folder = os.environ['FOOTBALL_HOME'] + "//leagues//" + str(season_number)
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams"
    player_folder = os.environ['FOOTBALL_HOME'] + "//players"
    for tier in os.listdir(league_folder):
        if "cup" not in tier and "round" not in tier and "promotions" not in tier:
            for league in os.listdir(league_folder + "//" + str(tier)):
                with open(league_folder + "//" + str(tier) + "//" + league + "//teams.yaml", "r") as file:
                    ids = yaml.safe_load(file)["teams"]
                leagues = LeagueTable(team_ids=ids,
                                      yaml_file=league_folder + "//" + str(tier) + "//" + league + "//schedule.yaml",
                                      csv_file=league_folder + "//" + str(tier) + "//" + league + "//table.csv",
                                      name=league)

                leagues.play_week(week_number, team_folder, player_folder, season_number, league)


def work_out_promotions(season_number):
    league_folder = os.environ['FOOTBALL_HOME'] + "//leagues//" + str(season_number)
    leagues = {}
    play_offs_up = {}
    play_offs_down = {}
    promotions = {}
    demotions = {}
    tier_max = 0
    team_league = {}
    for tier in os.listdir(league_folder):
        if "round" not in tier and "cup" not in tier and "promotions" not in tier:
            leagues[str(tier)] = {}
            play_offs_up[str(tier)] = []
            promotions[str(tier)] = []
            demotions[str(int(tier) + 1)] = []
            play_offs_down[str(tier)] = {}
            tier_max = tier
            for league in os.listdir(league_folder + "//" + str(tier)):
                leagues[str(tier)][str(league)] = []
                play_offs_down[str(tier)][str(league)] = []
                with open(league_folder + "//" + str(tier) + "//" + league + "//table.csv") as table_file:
                    table = csv.reader(table_file, delimiter=',', quotechar="~")
                    teams = []
                    for row in table:
                        teams.append(row[3])
                    teams.pop(0)
                    leagues[str(tier)][str(league)] = teams[2:8]
                    if int(tier) > 1:
                        promotions[str(int(tier) - 1)].append(teams[0])
                        play_offs_up[str(int(tier) - 1)].append(teams[1])
                        team_league[teams[1]] = [tier, league]
                    else:
                        leagues[str(tier)][str(league)] += teams[0:2]
                    play_offs_down[str(tier)][str(league)].append(teams[8])

                    demotions[str(int(tier) + 1)] += teams[9:12]
                    team_league[teams[8]] = [tier, league]
                    team_league[teams[9]] = [tier, league]
                    team_league[teams[10]] = [tier, league]
                    team_league[teams[11]] = [tier, league]
    print(team_league)
    print("far out")
    print({"play_offs_up": play_offs_up, "promotions": promotions, "demotions": demotions,
           "tier_max": tier_max, "leagues": leagues, "team_league": team_league,
           "play_offs_down": play_offs_down})
    print(league_folder + "//promotions.yaml")
    with open(league_folder + "//promotions.yaml", "w") as file:
        yaml.safe_dump({"play_offs_up": play_offs_up, "promotions": promotions, "demotions": demotions,
                        "tier_max": tier_max, "leagues": leagues, "team_league": team_league,
                        "play_offs_down": play_offs_down}, file)


def run_playoffs(league_folder):
    play_offs = {}
    with open(league_folder + "//promotions.yaml", "r") as promotion_file:
        promotions = yaml.safe_load(promotion_file)
    for tier in range(1, int(promotions["tier_max"])):
        play_offs[str(tier)] = {}
        play_off_up_holder = list(promotions["play_offs_up"][str(tier)])
        for league in os.listdir(league_folder + "//" + str(tier)):
            play_offs[str(tier)][str(league)] = []
            play_offs[str(tier)][str(league)].append(promotions["play_offs_down"][str(tier)][str(league)][0])

            while len(play_offs[str(tier)][str(league)]) < 4:
                next_team = randint(0, len(promotions["play_offs_up"][str(tier)]) - 1)
                play_offs[str(tier)][league].append(promotions["play_offs_up"][str(tier)][next_team])
                promotions["play_offs_up"][str(tier)].remove(promotions["play_offs_up"][str(tier)][next_team])
            next_round = run_play_offs(play_offs[str(tier)][league], league_folder[-1])
            while len(next_round) > 1:
                next_round = run_play_offs(next_round, league_folder[-1])
            winner = next_round[0]
            # TODO: Separate this into two functions so it can take course over a week (remember two games)
            # TODO: Have a place for the games to be put in a file, put them there with their scores
            for team in play_offs[str(tier)][league]:
                if team != winner and team in play_off_up_holder:

                    default_tier = str(promotions["team_league"][team][0])
                    promotions["leagues"][default_tier][str(promotions["team_league"][team][1])].append(team)
                elif team not in play_off_up_holder and team != winner:
                    default_tier = str(promotions["team_league"][winner][0])

                    promotions["leagues"][default_tier][str(promotions["team_league"][winner][1])].append(team)

            promotions["leagues"][str(tier)][str(league)].append(winner)

            for _ in range(3):
                auto_promote = randint(0, len(promotions["promotions"][str(tier)]) - 1)
                promotions["leagues"][str(tier)][str(league)].append(promotions["promotions"][str(tier)][auto_promote])
                promotions["promotions"][str(tier)].remove(promotions["promotions"][str(tier)][auto_promote])
            if tier > 1:
                demoted = randint(0, len(promotions["demotions"][str(tier)]) - 1)
                promotions["leagues"][str(tier)][str(league)].append(promotions["demotions"][str(tier)][demoted])
                promotions["demotions"][str(tier)].remove(promotions["demotions"][str(tier)][demoted])

    for team in promotions["demotions"][str(int(promotions["tier_max"]) + 1)]:
        default_tier = str(promotions["team_league"][team][0])
        promotions["leagues"][str(default_tier)][str(promotions["team_league"][team][1])].append(team)
    print(promotions["tier_max"])
    if int(promotions["tier_max"]) > 1:
        for league in os.listdir(league_folder + "//" + str(promotions["tier_max"])):
            demoted = randint(0, len(promotions["demotions"][str(promotions["tier_max"])]) - 1)
            promotions["leagues"][str(promotions["tier_max"])][league].append(promotions["demotions"]
                                                                              [str(promotions["tier_max"])][demoted])
            promotions["demotions"][str(promotions["tier_max"])].remove(promotions["demotions"]
                                                                              [str(promotions["tier_max"])][demoted])
    for league in os.listdir(league_folder + "//" + str(promotions["tier_max"])):
        for team in promotions["play_offs_down"][str(promotions["tier_max"])][league]:
            print("T {}" .format(team))
            promotions["leagues"][str(promotions["tier_max"])][league].append(team)
    create_tier_from_lists(promotions["leagues"])


# TODO: create a function to run the games and add all the needed teams to the correct lists
def run_play_offs(team_list, season_number):
    team_folder = os.environ['FOOTBALL_HOME'] + "teams//teams"
    player_folder = os.environ['FOOTBALL_HOME'] + "players//players"
    next_round = []
    for play_off in range(0, int(len(team_list) / 2)):
        name = [0, 0]
        formation = [0, 0]
        orders = ["", ""]
        for i in range(2):
            with open(team_folder + "//teams//" + team_list[2 * play_off + i] + ".yaml") as team_file:
                name[i] = yaml.safe_load(team_file)["team name"]
                if not os.path.isfile(os.environ['FOOTBALL_HOME'] + "//matches//orders//" +
                                      str(season_number) + 'Play_Off' + str(team_list[2 * play_off]) +
                                      str(team_list[2 * play_off + 1]) + str(team_list[2 * play_off + i]) + ".yaml"):
                    copyfile(team_folder + "//orders//" + str(team_list[2 * play_off + i]) + "-formation.yaml",
                             os.environ['FOOTBALL_HOME'] + "//matches//formations//" +
                             str(season_number) + 'Play_Off' + str(team_list[2 * play_off]) +
                             str(team_list[2 * play_off + 1]) + str(team_list[2 * play_off + i]) + ".yaml")
                    copyfile(team_folder + "//orders//" + str(team_list[2 * play_off + i]) + "-orders.yaml",
                             os.environ['FOOTBALL_HOME'] + "//matches//orders//" +
                             str(season_number) + 'Play_Off' + str(team_list[2 * play_off]) +
                             str(team_list[2 * play_off + 1]) + str(team_list[2 * play_off + i]) + ".yaml")

                formation[i] = os.environ['FOOTBALL_HOME'] + "//matches//formations//" + \
                    str(season_number) + 'Play_Off' + str(team_list[2 * play_off]) + str(team_list[2 * play_off + 1]) + \
                    str(team_list[2 * play_off + i]) + ".yaml"
                orders[i] = os.environ['FOOTBALL_HOME'] + "//matches//orders//" + \
                    str(season_number) + 'Play_Off' + str(team_list[2 * play_off]) + str(team_list[2 * play_off + 1]) + \
                    str(team_list[2 * play_off + i]) + ".yaml"
            comm_file = os.environ['FOOTBALL_HOME'] + "//matches//commentary//" + \
                str(season_number) + 'Play_Off' + str(team_list[2 * play_off]) + str(team_list[2 * play_off + 1]) + \
                ".txt"
            match = game.Game(player_folder, orders, formation, name, comm_file, "cup")
            match.play_game()
            result = match.score
            if result[0] > result[1]:
                next_round.append(team_list[2 * play_off])
            else:
                next_round.append(team_list[2 * play_off + 1])

    return next_round


# TODO: create a function to take these from a file and enact/remove promotions
def change_files_promotions():
    league_folder = os.environ['FOOTBALL_HOME'] + "//leagues"
    for tier in range(1, len([name for name in os.listdir(league_folder)]) + 1):
        for league in range(max(1, (tier - 1) * 3)):
            with open(league_folder + "//" + str(tier) + "//" + str(league) + "//playoff.yaml", "r") as file:
                play_offs = yaml.safe_load(file)
            with open(league_folder + "//" + str(tier) + "//" + str(league) + "//leagues.yaml", "r") as file:
                teams = yaml.safe_load(file)
            teams += play_offs
# delete yaml files.  Have season files?  maybe in leagues file name


def create_cup_fixtures(season_number):
    league_folder = os.environ['FOOTBALL_HOME'] + "//leagues//" + str(season_number)
    with open(league_folder + "//cup_fixtures.yaml") as file:
        teams = yaml.safe_load(file)
    round_of_cup = teams[0]
    teams = teams[1:]
    no_of_teams = len(teams)
    no_of_byes = shift_bit_length(no_of_teams) - no_of_teams
    byes = ["BYE"] * no_of_byes
    fixtures = []
    while len(byes) > 0:
        team_playing = randint(0, len(teams) - 1)
        fixtures.append(("BYE", teams[team_playing]))
        teams.remove(teams[team_playing])
        byes.remove("BYE")
    while len(teams) > 0:
        count = 0
        team_playing = randint(0, len(teams) - 1)
        team_playing_2 = team_playing
        while teams[team_playing] == teams[team_playing_2]:
            count += 1
            team_playing_2 = randint(0, len(teams) - 1)
            if count > 15:
                return -1
        match = [teams[team_playing], teams[team_playing_2]]
        if count > 15:
            return -1
        fixtures.append((match[0], match[1]))
        teams.remove(match[0])
        teams.remove(match[1])
    with open(league_folder + "//round_" + str(round_of_cup) + ".yaml", "w") as file:
        yaml.safe_dump(fixtures, file)
    return 0


def shift_bit_length(x):
    return 1 << (x-1).bit_length()


def play_cup_fixtures(season_number, player_folder):
    league_folder = os.environ['FOOTBALL_HOME'] + "//leagues//" + str(season_number)
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams//teams"
    with open(league_folder + "//cup_fixtures.yaml", "r") as cup_file:
        teams = yaml.safe_load(cup_file)
    with open(league_folder + "//round_" + str(teams[0]) + ".yaml", "r") as round_file:
        fixtures = yaml.safe_load(round_file)

    winners = [teams[0] + 1]
    if not os.path.isdir(os.environ['FOOTBALL_HOME'] + "//matches//orders//" + str(season_number) + "//" + "CUP"):
        os.mkdir(os.environ['FOOTBALL_HOME'] + "//matches//orders//" + str(season_number) + "//" + "CUP")
        os.mkdir(os.environ['FOOTBALL_HOME'] + "//matches//commentary//" + str(season_number) + "//" + "CUP")
        os.mkdir(os.environ['FOOTBALL_HOME'] + "//matches//formations//" + str(season_number) + "//" + "CUP")
    for fixture in fixtures:
        name = [0, 0]
        formation = [0, 0]
        orders = ["", ""]
        if fixture[0] == "BYE":
            result = [0, 1]
        elif fixture[1] == "BYE":
            result = [1, 0]
        else:
            for i in range(2):
                with open(team_folder + "//teams//" + fixture[i] + ".yaml") as team_file:
                    name[i] = yaml.safe_load(team_file)["team name"]
                if not os.path.isfile(os.environ['FOOTBALL_HOME'] + "//matches//orders//" +
                                      str(season_number) + 'Cup//' + str(fixture[0]) +
                                      str(fixture[1]) + str(fixture[i]) + ".yaml"):
                    copyfile(team_folder + "//orders//" + str(fixture[i]) + "-formation.yaml",
                             os.environ['FOOTBALL_HOME'] + "//matches//formations//" +
                             str(season_number) + '//Cup//' + str(fixture[0]) + str(fixture[1]) + str(fixture[i]) +
                             ".yaml")
                    copyfile(team_folder + "//orders//" + str(fixture[i]) + "-orders.yaml",
                             os.environ['FOOTBALL_HOME'] + "//matches//orders//" +
                             str(season_number) + '//Cup//' + str(fixture[0]) + str(fixture[1]) + str(fixture[i]) +
                             ".yaml")

                formation[i] = os.environ['FOOTBALL_HOME'] + "//matches//formations//" + \
                    str(season_number) + '//Cup//' + str(fixture[0]) + str(fixture[1]) + str(fixture[i]) + ".yaml"
                orders[i] = os.environ['FOOTBALL_HOME'] + "//matches//orders//" + \
                    str(season_number) + '//Cup//' + str(fixture[0]) + str(fixture[1]) + str(fixture[i]) + ".yaml"
            comm_file = os.environ['FOOTBALL_HOME'] + "//matches//commentary//" + \
                str(season_number) + '//Cup//' + str(fixture[0]) + str(fixture[1]) + ".txt"
            match = game.Game(player_folder + "//players", orders, formation, name, comm_file, "cup")
            team_stats_folder = os.environ['FOOTBALL_HOME'] + "//teams//stats"
            player_stats_folder = os.environ['FOOTBALL_HOME'] + "//players//stats"
            match.play_game(season_number, team_stats_folder, player_stats_folder, [str(fixture[0]), str(fixture[1])])
            result = match.score

        winner = int(result[1] > result[0])
        print("winner")
        print("{} vs {}" .format(fixture[0], fixture[1]))
        print(winner)
        winners.append(fixture[winner])

    with open(league_folder + "//cup_fixtures.yaml", "w") as file:
        yaml.safe_dump(winners, file)
    if len(fixtures) > 1:
        create_cup_fixtures(season_number)


def end_of_season(salary_cap, minimum, season_number):
    league_folder = os.environ['FOOTBALL_HOME'] + "//leagues"

    # TODO: Do promotion stuff
    # Retire players/announce retirements Done
    age_players()
    print("aged players")
    # Change contract details Done
    check_salary_cap(salary_cap)
    print("salary cap checked")
    # Create list of free agent players (with old teams) Done
    # sort out who is in what league
    # iterate season number
    with open(league_folder + "//season_number.yaml", "r") as file:
        number = yaml.safe_load(file) + 1
    with open(league_folder + "//season_number.yaml", "w") as file:
        yaml.safe_dump(number, file)
    print("season number changed")
    work_out_promotions(season_number)
    print("promotions worked out")
    run_playoffs(league_folder + "//" + str(number - 1))
    print("play offs run")
    # create tiers from preset lists of teams Done
    ensure_team_has_minimum(minimum)
    # ensure teams are not going over the maximum salary cap Done
    # ensure each team has minimum number of players by any means needed Done


def match_training_all(season_no, games, league, plays):
    for j in range(2):
        formation_amounts = {}
        route_amounts = {}
        with open(os.environ['FOOTBALL_HOME'] + "//matches//orders//" + str(season_no) + "//" + str(league) +
                  "//" + str(games[0]) + str(games[1]) + str(games[j]) + ".yaml", "r") as order_file:
            order = yaml.safe_load(order_file)
        with open(os.environ['FOOTBALL_HOME'] + "//matches//formations//" + str(season_no) + "//" + str(league) +
                  "//" + str(games[0]) + str(games[1]) + str(games[j]) + ".yaml", "r") as order_file:
            formation_stats = yaml.safe_load(order_file)
        for play in order["defense"]:
            if play != "kick return":
                if plays[play]["formation"] in list(formation_amounts.keys()):
                    formation_amounts[plays[play]["formation"]] += sum(order["defense"][play].values()) / \
                                                                       len(order["defense"][play].values())
                else:
                    formation_amounts[plays[play]["formation"]] = sum(order["defense"][play].values()) / \
                                                                          len(order["defense"][play].values())

        for play in order["offense"]:
            if sum(order["offense"][play].values()) > 0 and play not in ["kick off", "punting", "kicking"]:
                cut = 2 + (play[2] == " ")
                cut_name = play[cut:]
                if plays[cut_name]["formation"] in list(formation_amounts.keys()):
                    formation_amounts[plays[cut_name]["formation"]] += sum(order["offense"][play].values()) / 4
                else:
                    formation_amounts[plays[cut_name]["formation"]] = sum(order["offense"][play].values())
                for i in range(len(plays[cut_name]["assignments"])):
                    if "BLOCK" not in plays[cut_name]["assignments"][i].upper() and "RUN" not in \
                      plays[cut_name]["assignments"][i].upper():
                        if plays[cut_name]["formation"] not in list(route_amounts.keys()):
                            route_amounts[plays[cut_name]["formation"]] = {}
                        if i not in list(route_amounts[plays[cut_name]["formation"]].keys()):
                            route_amounts[plays[cut_name]["formation"]][i] = {}
                        if plays[cut_name]["assignments"][i] not in \
                            list(route_amounts[plays[cut_name]["formation"]][i].keys()):
                            route_amounts[plays[cut_name]["formation"]][i][plays[cut_name]["assignments"][i]] = 0
                        route_amounts[plays[cut_name]["formation"]][i][plays[cut_name]["assignments"][i]] += \
                            sum(order["offense"][play].values()) / 4
        players_train = {}
        for formation in formation_amounts:
            for i in range(11):
                player = formation_stats[formation][i]
                if player not in players_train.keys():
                    players_train[player] = {}
                    players_train[player]["formation"] = {}
                    players_train[player]["routes"] = {}
                if formation not in players_train[player].keys():
                    players_train[player]["formation"][formation] = 0
                players_train[player]["formation"][formation] += formation_amounts[formation]
                if formation in route_amounts:
                    if i in route_amounts[formation].keys():
                        for route in route_amounts[formation][i]:
                            if route not in players_train[player]["routes"]:
                                players_train[player]["routes"][route] = 0
                            players_train[player]["routes"][route] += route_amounts[formation][i][route]
        for i in range(2):
            with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//" + games[i] + ".yaml", "r") as team_file:
                players = yaml.safe_load(team_file)["player"]
            for player in players:
                if player in players_train:
                    position = LeagueTable.find_position(player, players_train[player]["formation"],
                                                         os.environ['FOOTBALL_HOME'] + "//matches//formations//" +
                                                         str(season_no) + "//" + str(league) + "//" + str(games[0]) +
                                                         str(games[1]) + str(games[i]) + ".yaml")
                    match_training.match_training(
                        os.environ['FOOTBALL_HOME'] + "//players//players//" + player + ".yaml",
                        players_train[player]["routes"], players_train[player]["formation"], position)


def age_players():
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams"
    player_folder = os.environ['FOOTBALL_HOME'] + "//players"
    for file in os.listdir(player_folder + "//players"):
        if ".yaml" in file:
            with open(player_folder + "//players//" + file, "r") as player_file:
                player_stats = yaml.safe_load(player_file)
            player_stats["age"] += 1
            if player_stats["age"] <= 20:
                increase = randint(1, 5)
                player_stats["weight"] += (increase + randint(-6, 4)) * 1.9
                player_stats["height"] += increase
            if player_stats["retiring"]:
                os.remove(player_folder + "//players//" + file)
                os.remove(player_folder + "//training//" + file)
                with open(player_folder + "//ref//player_id.yaml", "r") as player_names:
                    names = yaml.safe_load(player_names)
                player_no = file[:len(file) - 5]
                player_no = player_no[7:]
                names.remove(int(player_no))
                with open(player_folder + "//ref//player_id.yaml", "w") as player_names:
                    yaml.safe_dump(names, player_names)
            else:
                if randint(32, 37) < player_stats["age"]:
                    player_stats["retiring"] = False
                # Move player to free agency
                if player_stats["years_left"] == 1:
                    with open(team_folder + "//" + player_stats["team_id"] + ".yaml", "r") as file_team:
                        team = yaml.safe_load(file_team)
                    team["player"].remove(file[:len(file)-5])
                    with open(team_folder + "//" + player_stats["team_id"] + ".yaml", "w") as file_team:
                        yaml.safe_dump(team, file_team)
                    with open(player_folder + "//free_agents.yaml", "r") as free_agent_file:
                        free_agents = yaml.safe_load(free_agent_file)
                    free_agents.update({file[:len(file)-5]: {"team_id": player_stats["team_id"],
                                                             "team": player_stats["team"],
                                                             "asking": 1000}})
                    with open(player_folder + "//free_agents.yaml", "w") as free_agent_file:
                        yaml.safe_dump(free_agents, free_agent_file)
                    player_stats["team"] = "N/A"
                    pass
                else:
                    player_stats["years_left"] = max(0, player_stats["years_left"] - 1)
                with open(player_folder + "//players//" + file, "w") as player_file:
                    yaml.safe_dump(player_stats, player_file)


def check_salary_cap(salary_cap):
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams"
    player_folder = os.environ['FOOTBALL_HOME'] + "//players"
    for team_file in os.listdir(team_folder + "//teams"):
        with open(team_folder + "//teams//" + team_file) as file:
            team = yaml.safe_load(file)
        players = team["player"]
        salaries = {}
        for player in players:
            with open(player_folder + "//players//" + player + ".yaml") as player_file:
                salaries.update({player: yaml.safe_load(player_file)["contract_value"]})
        salary = sum(list(salaries.values()))
        while salary > salary_cap:

            fired = randint(0, len(players))
            remove_player(players[fired], team_file[:len(team_file) - 5], -1, True)
            salaries.pop(players[fired])
            salary = sum(list(salaries.values()))


def sort_league(league_folder):
    with open(league_folder + "//" + "table.csv") as table_file:
        table = csv.reader(table_file, delimiter=',', quotechar="~")
        data = []
        for row in table:
            data.append(row)
    headers = data.pop(0)
    df = pandas.DataFrame(data, columns=headers)
    df["rand"] = [randint(0, 10000) for _ in range(12)]
    df["win per"] = [int(df["wins"][i]) + int(df["draws"][i]) / 2 for i in range(12)]
    df["points difference"] = [int(df["points difference"][i]) for i in range(12)]
    df["for"] = [int(df["for"][i]) for i in range(12)]
    df = df.sort_values(by=["win per", "points difference", "for", "rand"], ascending=False)
    del df["rand"]
    del df["position"]
    del df["win per"]
    position = [x for x in range(1, 13)]
    df.insert(1, "position", position)
    del df[""]
    df.to_csv(league_folder + "//" + "table.csv")


def sort_entire_league(season_number):
    league_folder = os.environ['FOOTBALL_HOME'] + "//leagues//" + str(season_number)
    for tier_folder in os.listdir(league_folder):
        if "fixtures" not in tier_folder and "round" not in tier_folder and "promotions" not in tier_folder:
            for folder in os.listdir(league_folder + "//" + tier_folder):
                sort_league(league_folder + "//" + tier_folder + "//" + folder)


def work_out_franchise_cost():
    positions_total = {"QB": [0, 0], "FB": [0, 0], "RB": [0, 0], "OL": [0, 0], "OC": [0, 0], "WR": [0, 0],
                       "TE": [0, 0], "DL": [0, 0], "DE": [0, 0], "LB": [0, 0], "MLB": [0, 0], "CB": [0, 0],
                       "SF": [0, 0], "K": [0, 0], "GNR": [0, 0], "RET": [0, 0]}
    final_totals = {"QB": 0, "FB": 0, "RB": 0, "OL": 0, "OC": 0, "WR": 0, "TE": 0, "DL": 0, "DE": 0, "LB": 0, "MLB": 0,
                     "CB": 0,  "SF": 0,  "K": 0,  "GNR": 0,  "RET": 0, }
    for player in os.listdir(os.environ['FOOTBALL_HOME'] + "//players//players"):
        # TODO: Work out who is in which position and add them in
        pass
    for position in positions_total:
        final_totals[position] = positions_total[position][0] / positions_total[position][1]

    # TODO: Put final totals somewhere

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

from random import randint

from create_team import create_team, remove_player
from league import LeagueTable


def create_tier(tier):
    with open("leagues//season_number.yaml", "r") as file:
        season_number = yaml.safe_load(file)
    base_name = "leagues//" + str(season_number)
    if not os.path.exists(base_name):
        os.makedirs(base_name)
    for i in range(max(3 ** (tier - 1), 1)):
        league_name = chr(tier - 1 + ord('a')) + " " + str(i)
        if not os.path.exists(base_name + "//" + str(tier)):
            os.makedirs(base_name + "//" + str(tier))
        team = {}
        country = ["Ireland", "United Kingdom", "United States of America", "Canada", "Australia"]
        for _ in range(12):
            t = create_team(country[randint(0, 4)], str(tier) + " " + str(i))
            team.update({t: t})
        print(i)
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


def play_week(week_number, league_folder):
    for tier in os.listdir(league_folder):
        if "cup" not in tier and "round" not in tier:
            for league in os.listdir(league_folder + "//" + str(tier)):
                with open(league_folder + "//" + str(tier) + "//" + league + "//teams.yaml", "r") as file:
                    ids = yaml.safe_load(file)["teams"]
                # TODO: Create League Class here
                leagues = LeagueTable(team_ids=ids,
                                      yaml_file=league_folder + "//" + str(tier) + "//" + league + "//schedule.yaml",
                                      csv_file=league_folder + "//" + str(tier) + "//" + league + "//table.csv",
                                      name=league)

                leagues.play_week(week_number)


def enact_promotions(league_file):
    promotion_list = {}
    demotion_list = {}
    promotion_qualifiers = {}
    demotion_qualifiers = {}
    for tier in range(1, len([name for name in os.listdir(league_file)]) + 1):
        promotion_list[tier] = demotion_list[tier] = promotion_qualifiers[tier] = demotion_qualifiers[tier] = []
        for file in os.listdir(league_file + "//" + str(tier)):
            if "csv" in file:
                with open(league_file + "//" + str(tier) + "//" + str(tier), 'rb') as csv_file:
                    standings = csv.reader(csv_file)
                place = 0
                for row in standings:
                    if tier != 1:
                        if place == 0:
                            promotion_list[tier].append(row[1])
                        elif place == 1:
                            promotion_qualifiers[tier].append(row[1])
                    if tier != len([name for name in os.listdir(league_file)]):
                        if place in (9, 10, 11):
                            demotion_list[tier].append(row[1])
                        if place == 8:
                            demotion_qualifiers[tier].append(row[1])
                    place += 1
    return {"promotion": promotion_list, "demotion": demotion_list, "prom_playoff": promotion_qualifiers,
            "dem_playoff": demotion_qualifiers}


def run_playoffs(promotions, league_folder):
    play_offs = {}
    for tier in range(1, len(promotions["promotion"])):
        play_offs[tier] = []
        for league in range(max(1, (tier - 1) * 3)):
            play_offs[tier][league] = []
            play_offs[tier][league].append(promotions["dem_playoff"][tier][league])
            if tier < len(promotions["promotion"]):
                for i in range(3):
                    team = randint(0, len(promotions["prom_playoff"][tier+1]))
                    play_offs[tier][league].append(promotions["prom_playoff"][tier+1][team])
                    del promotions["prom_playoff"][tier + 1][team]
                for i in range(3):
                    team = randint(0, len(promotions["promotion"][tier+1]))
                    play_offs[tier][league].append(promotions["promotion"][tier+1][team])
                    del promotions["promotion"][tier + 1][team]
            if tier > 1:
                team = randint(0, len(promotions["demotion"][tier - 1]))
                play_offs[tier][league].append(promotions["demotion"][tier - 1][team])
                del promotions["demotion"][tier - 1][team]
            with open(league_folder + "//" + str(tier) + "//" + str(league) + "//playoff.yaml", "w") as file:
                yaml.safe_dump(play_offs, file)


# TODO: create a function to run the games and add all the needed teams to the correct lists
def run_play_offs(league_folder):
    for tier in range(1, len([name for name in os.listdir(league_folder)]) + 1):
        for league in range(max(1, (tier - 1) * 3)):
            with open(league_folder + "//" + str(tier) + "//" + str(league)  + "//playoff.yaml", "r") as file:
                play_offs = yaml.safe_load(file)
            # TODO: play the games and make one the winner
            del play_offs[2]
            del play_offs[3]
            del play_offs[1]
            with open(league_folder + "//" + str(tier) + "//" + str(league)  + "//playoff.yaml", "w") as file:
                yaml.safe_dump(play_offs, file)


# TODO: create a function to take these from a file and enact/remove promotions
def change_files_promotions(league_folder):
    for tier in range(1, len([name for name in os.listdir(league_folder)]) + 1):
        for league in range(max(1, (tier - 1) * 3)):
            with open(league_folder + "//" + str(tier) + "//" + str(league)  + "//playoff.yaml", "r") as file:
                play_offs = yaml.safe_load(file)
            with open(league_folder + "//" + str(tier) + "//" + str(league)  + "//leagues.yaml", "r") as file:
                teams = yaml.safe_load(file)
            teams += play_offs
# delete yaml files.  Have season files?  maybe in leagues file name


def create_cup_fixtures(league_folder):
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
                print(teams[team_playing])
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


def play_cup_fixtures(league_folder):
    with open(league_folder + "//cup_fixtures.yaml", "r") as file:
        teams = yaml.safe_load(file)
    with open(league_folder + "//round_" + str(teams[0]) + ".yaml", "r") as file:
        fixtures = yaml.safe_load(file)

    winners = [teams[0] + 1]
    for fixture in fixtures:
        # TODO: Actually play cup fixtures
        if fixture[0] == "BYE":
            winner = 1
        elif fixture[1] == "BYE":
            winner = 0
        else:
            winner = randint(0, 1)
        winners.append(fixture[winner])
    with open(league_folder + "//cup_fixtures.yaml", "w") as file:
        yaml.safe_dump(winners, file)
    create_cup_fixtures(league_folder)


def end_of_season(league_folder):
    # TODO: Do promotion stuff
    # Retire players/announce retirements Done
    # Age players Done
    # Change contract details Done
    # Create list of free agent players (with old teams) Done
    # sort out who is in what league

    # iterate season number
    with open(league_folder + "//season_number.yaml", "r") as file:
        number = yaml.safe_load(file) + 1
    with open(league_folder + "//season_number.yaml", "w") as file:
        yaml.safe_dump(number, file) + 1
    # create tiers from preset lists of teams
    # ensure teams are not going over the maximum salary cap
    # ensure each team has minimum number of players by any means needed Done


def age_players(player_folder, team_folder):
    for file in os.listdir(player_folder):
        if ".yaml" in file:
            with open(player_folder + "//" + file, "r") as player_file:
                player_stats = yaml.safe_load(player_file)
            player_stats["age"] += 1
            if player_stats["retiring"]:
                os.remove(player_folder + "//players//" + file)
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
                with open(player_folder + "//" + file, "w") as player_file:
                    yaml.safe_dump(player_stats, player_file)


def check_salary_cap(team_folder, player_folder, salary_cap):
    for team_file in os.listdir(team_folder):
        with open(team_folder + "//teams//" + team_file) as file:
            team = yaml.safe_load(file)
        players = team["player"]
        salary = salary_c
        while salary > salary_cap:
        for player in players:
            with open(player_folder + "//players//" + player + ".yaml") as player_file:
                player_stats = yaml.safe_load(player_file)
            salary += player_stats["contract_value"]

            fired = randint(0, len(players))
            remove_player(players[fired], player_folder, team_file[:len(team_file) - 5], team_folder, -1)
            players.remove(players[fired])

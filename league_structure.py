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

from create_team import create_team
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
        with open(base_name + "//" + str(tier) + "//" + league_name + "//" + "teams.yaml", "w") as file:
            yaml.safe_dump({"leagues name": league_name, "teams": list(team.keys())}, file)
        with open(base_name + "cup_fixtures.yaml", "a") as file:
            yaml.safe_dump([1] + list(team.keys()), file)
        league = LeagueTable(team, base_name + "//" + str(tier) + "//" + league_name + "//schedule.yaml",
                             base_name + "//" + str(tier) + "//" + league_name + "//table.csv", league_name)
        league.create_schedule()
        league.initialise_file()


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

    teams += ["BYE"] * no_of_byes
    fixtures = []
    assert len(teams) - shift_bit_length(len(teams)) == 0
    while len(teams) > 0:
        match = []
        for i in range(1):
            team_playing = randint(0, len(teams) - 1)
            match.append(teams[team_playing])
            teams.remove(teams[team_playing])
        fixtures.append((match[0], match[1]))
    with open(league_folder + "//round_" + round_of_cup + ".yaml") as file:
        yaml.safe_load(fixtures, file)
    return fixtures


def shift_bit_length(x):
    return 1 << (x-1).bit_length()


def play_cup_fixtures(league_folder):
    # TODO: Remember that we need to create the next fixtures as well
    # TODO: Don't create fixtures, simply create list of teams for the next one and call create cup fixtures

    create_cup_fixtures(league_folder)
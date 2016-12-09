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

from League.create_team import create_team
from League.league import LeagueTable


def create_tier(tier):
    for i in range(max(3 ** (tier - 1), 1)):
        league_name = chr(tier - 1 + ord('a')) + " " + str(i)
        if not os.path.exists("leagues//" + str(tier)):
            os.makedirs("leagues//" + str(tier))
        team = {}
        country = ["Ireland", "United Kingdom", "United States of America", "Canada", "Australia"]
        for _ in range(12):
            t = create_team(country[randint(0, 4)], str(tier) + " " + str(i))
            team.update({t: t})
        with open("leagues//" + str(tier) + "//" + league_name + ".yaml", "w") as file:
            yaml.safe_dump({"league name": league_name, "teams": list(team.keys())}, file)
        league = LeagueTable(team, "leagues//" + str(tier) + "//" + league_name + "-schedule.yaml",
                             "leagues//" + str(tier) + "//" + league_name + ".csv", league_name)
        league.create_schedule()
        league.initialise_file()
        # TODO: create league table and fixture list file


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

def run_playoffs(promotions):
    play_offs = {}
    for tier in range(1, len(promotions["promotion"])):
        for league in range(max(1, (tier - 1) * 3)):
            play_offs[tier * 100 + league] = []
            play_offs[tier * 100 + league].append(promotions["dem_playoff"][tier][0])
            for i in range(3):
                team = randint(0, len(promotions["prom_playoff"][tier]))
                play_offs[tier * 100 + league].append(promotions["prom_playoff"][tier+1][team])
                del promotions["prom_playoff"][tier + 1][team]
    # TODO: create a yaml file with the schedule
    # also include auto promote/demote teams - maybe a second yaml file?

# TODO: create a function to run the games and add all the needed teams to the correct lists

# TODO: create a function to take these from a file and enact/remove promotions
# delete yaml files.  Have season files?  maybe in league file name

def create_cup_fixtures(tier):
    no_of_teams = 0
    count = tier - 1
    while count > 0:
        no_of_teams += 12 * 3 ** count
        count -= 1
    no_of_byes = shift_bit_length(no_of_teams) - no_of_teams
    # TODO: Add all team ids of these to a list properly
    list_of_teams = []
    for i in range(no_of_teams):
        list_of_teams.append(i)
    list_of_teams += ["BYE"] * no_of_byes
    fixtures = []
    print(len(list_of_teams))
    print(no_of_byes)
    assert len(list_of_teams) - shift_bit_length(len(list_of_teams)) == 0
    while len(list_of_teams) > 0:
        team_played = randint(1, len(list_of_teams) - 1)
        fixtures.append((list_of_teams[0], list_of_teams[team_played]))
        list_of_teams.remove(list_of_teams[team_played])
        list_of_teams.remove(list_of_teams[0])
    return fixtures


def shift_bit_length(x):
    return 1 << (x-1).bit_length()


def play_cup_fixtures():
    # TODO: Remember that we need to create the next fixtures as well
    pass
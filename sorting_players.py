import os
import yaml
from create_team import add_player

from training_modules import aging, training


def train_players():
    for file in os.listdir(os.environ['FOOTBALL_HOME'] + "//players//training"):
        print(file)
        with open(os.environ['FOOTBALL_HOME'] + "//players//training//" + file, "r") as train_file:
            training_mod = yaml.safe_load(train_file)
        focus = training_mod["focus"]
        route_assignment = training_mod["route assignment"]
        training.training(os.environ['FOOTBALL_HOME'] + "//players//players//" + file, focus, route_assignment, "")
        aging.aging(os.environ['FOOTBALL_HOME'] + "//players//players//" + file)


def new_players(week):
    for team in os.listdir(os.environ['FOOTBALL_HOME'] + "//teams//teams"):
        with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//" + team) as team_file:
            draft = yaml.safe_load(team_file)['draft picks']
        week_draft = [draft[i] for i in range(len(draft)) if str(draft[i]) == str(week)]
        with open(os.environ['FOOTBALL_HOME'] + "//teams//scouting//scouts-" + team.replace(".yaml", ""), "r") \
                as scout_file:
            scouts = yaml.safe_load(scout_file)
        for _ in range(len(week_draft)):
            add_player(team.replace(".yaml", ""), attrib=scouts["attrib"], ideal_height=scouts["ideal_height"],
                       ideal_weight=scouts["ideal_weight"], week=week, maximum=70)


def check_position(player_stats):
    return ""


def check_players_wages():
    for player in os.listdir(os.environ['FOOTBALL_HOME'] + "players//players"):
        with open(os.environ['FOOTBALL_HOME'] + "players//players//" + player) as player_file:
            player_stats = yaml.safe_load(player_file)
        if player_stats["contract_value"] == 1000:
            pos = check_position(player_stats)
            if pos != "":
                # TODO: Change players position
                # TODO: Create bid file for player
                pass


def check_bid_files():
    # TODO: checks the various bid files and accepts them or not
    pass

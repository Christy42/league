import os
import yaml
from create_team import add_player

from training_modules import aging, training


def train_players():
    for file in os.listdir(os.environ['FOOTBALL_HOME'] + "//players//training"):
        with open(os.environ['FOOTBALL_HOME'] + "//players//training//" + file, "r") as train_file:
            training_mod = yaml.safe_load(train_file)
        focus = training_mod["focus"]
        route_assignment = training_mod["route assignment"]
        training.training(os.environ['FOOTBALL_HOME'] + "//players//players//" + file, focus, route_assignment, "")
        aging.aging(os.environ['FOOTBALL_HOME'] + "//players//players//" + file)


def new_players(week):
    for team in os.listdir(os.environ['FOOTBALL_HOME'] + "//teams//teams"):
        with open(os.environ['FOOTBALL_HOME'] + "//teams//scouting//scouts-" + team.replace(".yaml", ""), "r") \
                as scout_file:
            scouts = yaml.safe_load(scout_file)
        add_player(team.replace(".yaml", ""), attrib=scouts["attrib"], ideal_height=scouts["ideal_height"],
                   ideal_weight=scouts["ideal_weight"], week=week, maximum=70)

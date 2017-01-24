import os
import yaml

from training_modules import aging, training


def train_players():
    for file in os.listdir(os.environ['FOOTBALL_HOME'] + "//players//training"):
        with open(os.environ['FOOTBALL_HOME'] + "//players//training//" + file, "r") as train_file:
            training_mod = yaml.safe_load(train_file)
        focus = training_mod["focus"]
        route_assignment = training_mod["route assignment"]
        training.training(os.environ['FOOTBALL_HOME'] + "//players//players//" + file, focus, route_assignment, "")
        aging.aging(os.environ['FOOTBALL_HOME'] + "//players//players//" + file)

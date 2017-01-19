import os
import yaml

from training_modules import aging, training


def train_players(training_folder, player_folder):
    for file in os.listdir(training_folder):
        with open(training_folder + "//" + file, "r") as train_file:
            training_mod = yaml.safe_load(train_file)
        focus = training_mod["focus"]
        route_assignment = training_mod["route assignment"]
        training.training(player_folder + "//" + file, focus, route_assignment, "")
        aging.aging(player_folder + "//" + file)

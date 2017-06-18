import os
import yaml
from random import randint

from create_team import add_player, update_draft_picks

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
        if type(draft) != list:
            draft = [draft]
        week_draft = [draft[i] for i in range(len(draft)) if str(draft[i]) == str(week)]
        with open(os.environ['FOOTBALL_HOME'] + "//teams//scouting//scouts-" + team, "r") \
                as scout_file:
            scouts = yaml.safe_load(scout_file)
        for _ in range(len(week_draft)):
            add_player(team.replace(".yaml", ""), attrib=scouts["attrib"], ideal_height=scouts["ideal_height"],
                       ideal_weight=scouts["ideal_weight"], week=week, maximum=70)
    update_draft_picks(week)


def check_position(player):
    with open(os.environ['FOOTBALL_HOME'] + "players//players//" + player, "r") as player_file:
        player_stats = yaml.safe_load(player_file)
    with open(os.environ['FOOTBALL_HOME'] + "trading//franchise_wages.yaml", "r") as franchise_wages:
        franchise = yaml.safe_load(franchise_wages)
    return ""


def update_players_wages():
    for player in os.listdir(os.environ['FOOTBALL_HOME'] + "players//players"):
        with open(os.environ['FOOTBALL_HOME'] + "players//players//" + player, "r") as player_file:
            player_stats = yaml.safe_load(player_file)
        if player_stats["franchised"]:
            player_stats["franchised"] = False
        if player_stats["franchise next season"] is True:
            pos = check_position(player)
            player_stats["franchise next season"] = False
            player_stats["franchised"] = True
            player_stats["guarantee"] = 1
            player_stats["years_left"] = 1
            with open(os.environ['FOOTBALL_HOME'] + "trading//franchise_wages.yaml", "r") as franchise_wages:
                player_stats["contract_value"] = yaml.safe_load(franchise_wages)[pos]
        if (player_stats["contract_value"] > 1000 and player_stats["years_left"] > 1) \
                or player_stats["franchised"] is True:
            pass
        else:
            pos = check_position(player)
            with open("wages", "r") as wage_file:
                wages = yaml.safe_load(wage_file)[pos]
            max_stat = 0
            second_stat = 0
            for stat in wages["stats"]:
                if player_stats[stat] > max_stat:
                    max_stat = player_stats[stat]
                    second_stat = max_stat
                else:
                    second_stat = max(second_stat, player_stats[stat])
            if max_stat > 500:
                player_stats["asking_price"] = max(player_stats["contract_value"], wages[round(max_stat / 10.0, -1)]) + \
                    randint(-10000, 10000) + second_stat * 10000
                player_stats["asking_guarantee"] = 0
        with open(os.environ['FOOTBALL_HOME'] + "players//players//" + player, "w") as player_file:
            yaml.safe_dump(player_stats, player_file)


def check_bid_files():
    # TODO: checks the various bid files and accepts them or not
    pass


def franchise_player(player, team, franchise_limit):
    with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + player + ".yaml", "r") as player_file:
        player_stats = yaml.safe_load(player_file)
    with (os.environ['FOOTBALL_HOME'] + "//team//team//" + team + ".yaml", "r") as team_file:
        team = yaml.safe_load(team_file)
    if "franchised" not in team.keys():
        team["franchised"] = 0

    if team["franchised"] >= franchise_limit or player not in team["player"]:
        return False
    if player_stats["franchise next season"] is True or player_stats["years_left"] > 1 or player_stats["franchised"]:
        return False
    player_stats["franchise next season"] = True
    with open(os.environ['FOOTBALL_HOME'] + "players//players//" + player + ".yaml", "w") as player_file:
        yaml.safe_dump(player_stats, player_file)
    team["franchised"] += 1
    with (os.environ['FOOTBALL_HOME'] + "//team//team//" + team + ".yaml", "w") as team_file:
        yaml.safe_dump(team, team_file)
    return True

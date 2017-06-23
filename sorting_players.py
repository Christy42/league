import os
import yaml
from random import randint

from create_team import add_player, update_draft_picks

from training_modules import aging, training

from Wages.Wages import add_player_to_free_agency, check_position


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
            draft = yaml.safe_load(team_file)
        if draft["bot"]:
            continue
        draft = draft["draft picks"]
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


def update_players_wages():
    for player in os.listdir(os.environ['FOOTBALL_HOME'] + "//players//players"):
        with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + player, "r") as player_file:
            player_stats = yaml.safe_load(player_file)
        with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//" + player_stats["team"] + ".yaml", "r") as team_file:
            bot_team = yaml.safe_load(team_file)["bot"]
        if bot_team and randint(0, 99) != 0:
            player_stats["years_left"] = 2
            player_stats["contract_value"] = 1000
        if player_stats["franchised"]:
            player_stats["franchised"] = False
        if player_stats["franchise next season"] is True:
            pos = check_position(player)
            player_stats["franchise next season"] = False
            player_stats["franchised"] = True
            player_stats["guarantee"] = 1
            player_stats["years_left"] = 1
            with open(os.environ['FOOTBALL_HOME'] + "//trading//franchise_wages.yaml", "r") as franchise_wages:
                player_stats["contract_value"] = yaml.safe_load(franchise_wages)[pos]
        if (player_stats["contract_value"] > 1000 and player_stats["years_left"] > 1) \
                or player_stats["franchised"] is True:
            pass
        elif check_position(player)[1] > 50:
            player_stats["position"] = check_position(player)[0]
            add_player_to_free_agency(player)
        # print(player)
        with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + player, "w") as player_file:
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

update_players_wages()

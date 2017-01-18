import yaml
import os

from random import randint


def create_team(nationality, league_name):
    with open("teams//ref//team_names.yaml", "r") as file:
        names = yaml.safe_load(file)
    new_name = smallest_missing_in_list(names)
    to_write = {"nationality": nationality, "leagues name": league_name, "bot": True}
    if not names:
        names = [0]
    else:
        names = names[:new_name] + [new_name] + names[new_name:]
    team_name = "Team_" + str(new_name)
    to_write["team name"] = team_name
    with open("teams//ref//team_names.yaml", "w") as file:
        yaml.safe_dump(names, file)
    to_write["player"] = []
    for i in range(22):
        to_write["player"].append(create_player(nationality, team_name, team_name))
    with open("teams//teams//" + team_name + ".yaml", "w") as file:
        yaml.safe_dump(to_write, file)
    with open("teams//dead_money//" + team_name + ".yaml", "w") as dead_money_file:
        yaml.safe_dump({}, dead_money_file)
    with open("formation.yaml", "r") as file:
        formations = yaml.safe_load(file)
    starters = {}
    for formation in formations["offense"]:
        starters[formation] = [to_write["player"][i] for i in range(11)]
    for formation in formations["defense"]:
        starters[formation] = [to_write["player"][i] for i in range(11, 22)]
    for formation in formations["special"]:
        starters[formation] = [to_write["player"][i] for i in range(11)]
    with open("teams//orders//" + team_name + "-formation.yaml", "w") as file:
        yaml.safe_dump(starters, file)
    percentages = {"offense": dict(), "defense": dict()}

    percentages["offense"]["1 Deep Attack"] = {1: 30, 2: 30, 3: 20, 4: 70}
    percentages["offense"]["4 HB Dive"] = {1: 40, 2: 35, 3: 30, 4: 20}
    percentages["offense"]["1 Cross Up"] = {1: 20, 2: 25, 3: 30, 4: 10}
    percentages["offense"]["4 kick off"] = {1: 0, 2: 0, 3: 0, 4: 0}
    percentages["offense"]["10 Double TE QB Sneak"] = {1: 10, 2: 10, 3: 20, 4: 0}
    with open("plays.yaml", "r") as file:
        plays = yaml.safe_load(file)
    for play in plays["offense"]:
        if play not in ["1 Deep Attack", "4 HB Dive", "1 Cross Up", "10 Double TE QB Sneak"]:
            percentages["offense"][play] = {1: 0, 2: 0, 3: 0, 4: 0}
    for play in plays["defense"]:
        if play not in ["3-4-4 Cover 2", "4-3-4 Engage Eight", "4-4-3 Cover 3", "Dime Double Wide", "Nickel Double Z"]:
            percentages["defense"][play] = {"Shotgun": 0, "Spread": 0, "Double TE Set": 0, "I-Form": 0,
                                            "Singleback": 0}
    percentages["defense"]["3-4-4 Cover 2"] = {"Shotgun": 50, "Spread": 40, "Double TE Set": 15,
                                               "I-Form": 20, "Singleback": 30}
    percentages["defense"]["4-3-4 Engage Eight"] = {"Shotgun": 10, "Spread": 5, "Double TE Set": 25,
                                                    "I-Form": 20, "Singleback": 0}
    percentages["defense"]["4-4-3 Cover 3"] = {"Shotgun": 10, "Spread": 15, "Double TE Set": 10, "I-Form": 20,
                                               "Singleback": 15}
    percentages["defense"]["Dime Double Wide"] = {"Shotgun": 20, "Spread": 20, "Double TE Set": 30,
                                                  "I-Form": 20, "Singleback": 20}
    percentages["defense"]["Nickel Double Z"] = {"Shotgun": 10, "Spread": 20, "Double TE Set": 20,
                                                 "I-Form": 20, "Singleback": 35}
    percentages["special"] = {"time between plays": 35, "field goal range": 20}
    with open("teams//orders//" + team_name + "-orders.yaml", "w") as file:
        yaml.safe_dump(percentages, file)
    return team_name


def create_player(nationality, team, team_id):
    with open("players//ref//player_id.yaml", "r") as file:
        names = yaml.safe_load(file)
    new_name = smallest_missing_in_list(names)
    if names:
        names = names[:new_name] + [new_name] + names[new_name:]
    else:
        names = [0]
    player_id = "Player_" + str(new_name)
    with open("players//ref//player_id.yaml", "w") as file:
        yaml.safe_dump(names, file)
    player = dict()
    player["name"] = name_player(nationality)
    with open("players//ref//player_stats.yaml", "r") as file:
        att = yaml.safe_load(file)
    low_att = att["low attributes"]
    pos_att = att["positional attributes"]
    high_att = att["high attributes"]
    player["nationality"] = nationality
    player["team"] = team
    player["team_id"] = team_id
    player["contract_value"] = 1000
    player["guarantee"] = 0
    player["age"] = 16 + randint(0, 3)
    player["height"] = generate_height(player["age"])
    player["height"] = generate_weight(player["height"])
    player["years_left"] = 0
    player["retiring"] = False
    player["id"] = new_name
    for attribute in low_att:
        player[attribute] = 100 + randint(0, 300)
    for attribute in pos_att:
        player[attribute] = 150 + randint(0, 100)
    for attribute in high_att:
        player[attribute] = 500 + (randint(0, 500) + randint(0, 500) +
                                   randint(0, 500) + randint(0, 500) + randint(0, 500)) / 5
    with open("players//players//" + player_id + ".yaml", "w") as file:
        yaml.safe_dump(player, file)
    training = {"file name": "players//players//" + player_id + ".yaml", "focus": "", "route assignment": ""}
    with open("players//training//" + player_id + ".yaml", "w") as file:
        yaml.safe_dump(training, file)
    return player_id


def smallest_missing_in_list(list_of_numbers):
    if not list_of_numbers:
        return 0
    lowest_fail = len(list_of_numbers)
    partial = list_of_numbers
    highest_pass = -1
    half = int(len(list_of_numbers) / 2)
    while lowest_fail - highest_pass > 1 and partial:
        if list_of_numbers[half] == half:
            partial = partial[half:]
            highest_pass = half
            half += max(int(len(partial) / 2), 1)
        else:
            partial = partial[:half]
            lowest_fail = half
            half -= max(int(len(partial) / 2), 1)

    return lowest_fail


def name_player(nationality):
    with open("list_of_names.yaml", "r") as file:
        names = yaml.safe_load(file)
    random_first = randint(0, 99)
    random_second = randint(0, 99)
    first_name = names[nationality]["first"][random_first]
    second_name = names[nationality]["second"][random_second]
    return first_name + " " + second_name


def add_player(team_id, team_folder, maximum):
    with open(team_folder + "//" + team_id + ".yaml", "r") as team_file:
        team = yaml.safe_load(team_file)
    if team["player"] < maximum:
        team_name = team["team name"]
        team["player"].append(create_player(team["nationality"], team_name, team_id))
        with open(team_folder + "//" + team_id + ".yaml", "w") as team_file:
            yaml.safe_dump(team, team_file)


def add_player_old(team_id, team_folder, player_folder, player_id, maximum):
    with open(team_folder + "//" + team_id + ".yaml", "r") as team_file:
        team = yaml.safe_load(team_file)
    if team["player"] < maximum:
        team["player"].append(player_id)
        with open(team_folder + "//" + team_id + ".yaml", "w") as team_file:
            yaml.safe_dump(team, team_file)
        with open(player_folder + "//" + player_id + ".yaml", "r") as player_file:
            player = yaml.safe_load(player_file)
        player["team_id"] = team_id
        player["team"] = team["team name"]
        with open(player_folder + "//" + player_id + ".yaml", "w") as player_file:
            yaml.safe_dump(player, player_file)


def ensure_team_has_minimum(team_folder, minimum):
    for file in os.listdir(team_folder + "//teams"):
        with open(team_folder + "//teams//" + file, "r") as team_file:
            team = yaml.safe_load(team_file)
        while len(team["player"]) < minimum:
            add_player(file[:len(file) - 5], team_folder, 999)
        with open(team_folder + "//teams//" + file, "w") as team_file:
            yaml.safe_dump(team, team_file)


def remove_player(player_id, player_folder, team_id, team_folder, minimum):
    with open(team_folder + "//teams//" + team_id + ".yaml") as team_file:
        team = yaml.safe_load(team_file)
    if len(team["player"]) > minimum:
        team["player"].remove(player_id)
        with open(team_folder + "//teams//" + team_id, "w") as team_file:
            yaml.safe_dump(team, team_file)
        with open(player_folder + "//players//" + player_id + ".yaml", "r") as player_file:
            player = yaml.safe_load(player_file)
        player["team_id"] = "N/A"
        team_name = player["team"]
        player["team"] = "N/A"
        with open(player_folder + "//players//" + player_id, "w") as player_file:
            yaml.safe_dump(player, player_file)
        with open(player_folder + "//free_agents.yaml", "r") as free_agent_file:
            free_agents = yaml.safe_load(free_agent_file)
        free_agents.update({player_id: {"team_id": team_id, "team": team_name, "asking": 1000}})
        with open(player_folder + "//free_agents.yaml", "w") as free_agent_file:
            yaml.safe_dump(free_agents, free_agent_file)
        with open(team_folder + "//dead_money//" + team_id + ".yaml", "r") as dead_money_file:
            dead_money = yaml.safe_load(dead_money_file)
        dead_money.update({player_id: {"years": player["years_left"],
                                       "amount": player["guarantee"] * player["contract_value"]}})
        with open(team_folder + "//dead_money//" + team_id + ".yaml", "w") as dead_money_file:
            yaml.safe_dump(dead_money, dead_money_file)
    else:
        # TODO: put in something to point out to the user that the player may not be removed
        pass


def generate_height(age):
    height = 135 + max(min(age - 16, 4), 0)
    for _ in range(17 + max(min(age - 16, 4), 0)):
        height += randint(0, 4)
    return height


def generate_weight(height):
    weight = 1.11 * height - 15
    random_max = int(min(height / 10 - 8, 10))
    for _ in range(19):
        weight -= randint(0, random_max)
    return weight

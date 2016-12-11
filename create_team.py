import yaml

from random import randint


def create_team(nationality, league_name):
    with open("teams//team_names.yaml", "r") as file:
        names = yaml.safe_load(file)
    new_name = smallest_missing_in_list(names)
    to_write = {"nationality": nationality, "leagues name": league_name, "bot": True}
    if not names:
        names = [0]
    else:
        names = names[:new_name] + [new_name] + names[new_name:]
    team_name = "Team_" + str(new_name)
    to_write["team name"] = team_name
    with open("teams//team_names.yaml", "w") as file:
        yaml.safe_dump(names, file)
    to_write["player"] = []
    for i in range(22):
        to_write["player"].append(create_player(nationality))
    with open("teams//" + team_name + ".yaml", "w") as file:
        yaml.safe_dump(to_write, file)
    with open("formation.yaml", "r") as file:
        formations = yaml.safe_load(file)
    starters = {}
    for formation in formations["offense"]:
        starters[formation] = [to_write["player"][i] for i in range(11)]
    for formation in formations["defense"]:
        starters[formation] = [to_write["player"][i] for i in range(11, 22)]
    for formation in formations["special"]:
        starters[formation] = [to_write["player"][i] for i in range(11)]
    with open("teams//" + team_name + "-formation.yaml", "w") as file:
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
            percentages["offense"][play] ={1: 0, 2: 0, 3: 0, 4: 0}
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
    with open("teams//" + team_name + "-orders.yaml", "w") as file:
        yaml.safe_dump(percentages, file)
    return team_name


def create_player(nationality):
    with open("players//player_id.yaml", "r") as file:
        names = yaml.safe_load(file)
    new_name = smallest_missing_in_list(names)
    if names:
        names = names[:new_name] + [new_name] + names[new_name:]
    else:
        names = [0]
    player_id = "Player_" + str(new_name)
    with open("players//player_id.yaml", "w") as file:
        yaml.safe_dump(names, file)
    player = dict()
    player["name"] = name_player(nationality)
    with open("players//player_stats.yaml", "r") as file:
        att = yaml.safe_load(file)
    low_att = att["low attributes"]
    pos_att = att["positional attributes"]
    high_att = att["high attributes"]
    player["nationality"] = nationality
    player["contract_years"] = 0
    player["contract_value"] = 0
    player["guarantee"] = 0
    player["years_left"] = 0
    for attribute in low_att:
        player[attribute] = 100 + randint(0, 300)
    for attribute in pos_att:
        player[attribute] = 150 + randint(0, 100)
    for attribute in high_att:
        player[attribute] = 500 + (randint(0, 500) + randint(0, 500) +
                                   randint(0, 500) + randint(0, 500) + randint(0, 500)) / 5
    with open("players//" + player_id + ".yaml", "w") as file:
        yaml.safe_dump(player, file)
    training = {"file name": "players//" + player_id + ".yaml", "focus": [], "route assignment": []}
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

import yaml
import os
import csv

from random import randint


def create_team(nationality, league_name):
    with open(os.environ['FOOTBALL_HOME'] + "//teams//ref//team_names.yaml", "r") as file:
        names = yaml.safe_load(file)
    new_name = smallest_missing_in_list(names)
    to_write = {"nationality": nationality, "leagues name": league_name, "bot": True}
    if not names:
        names = [0]
    else:
        names = names[:new_name] + [new_name] + names[new_name:]
    team_name = "Team_" + str(new_name)
    to_write["team name"] = team_name
    to_write["draft picks"] = list(range(1, 12))
    to_write["salary"] = 22000
    to_write["trophies"] = {"cup": [0]}
    scout_base = {"ideal_height": -1, "ideal_weight": -1, "attrib": []}
    with open(os.environ['FOOTBALL_HOME'] + "//teams//scouting//scouts-" + team_name + ".yaml", "w") as scout_file:
        yaml.safe_dump(scout_base, scout_file)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//ref//team_names.yaml", "w") as file:
        yaml.safe_dump(names, file)
    to_write["player"] = {}
    for i in range(22):
        to_write["player"].update(create_player(nationality, team_name, team_name, attrib=[], week=8,
                                  ideal_height=-1, ideal_weight=-1))
    with open(os.environ['FOOTBALL_HOME'] + "//teams//teams//" + team_name + ".yaml", "w") as file:
        yaml.safe_dump(to_write, file)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//dead_money//" + team_name + ".yaml", "w") as dead_money_file:
        yaml.safe_dump({}, dead_money_file)
    with open(os.environ['FOOTBALL_HOME'] + "//league_config//formation.yaml", "r") as file:
        formations = yaml.safe_load(file)
    starters = {}
    players = list(to_write["player"].keys())
    for formation in formations["offense"]:
        starters[formation] = [players[i] for i in range(11)]
    for formation in formations["defense"]:
        starters[formation] = [players[i] for i in range(11, 22)]
    for formation in formations["special"]:
        starters[formation] = [players[i] for i in range(11)]
    with open(os.environ['FOOTBALL_HOME'] + "//teams//orders//" + team_name + "-formation.yaml", "w") as file:
        yaml.safe_dump(starters, file)
    percentages = {"offense": dict(), "defense": dict()}

    percentages["offense"]["1 Deep Attack"] = {1: 30, 2: 30, 3: 20, 4: 70}
    percentages["offense"]["4 HB Dive"] = {1: 40, 2: 35, 3: 30, 4: 20}
    percentages["offense"]["1 Cross Up"] = {1: 20, 2: 25, 3: 30, 4: 10}
    percentages["offense"]["4 kick off"] = {1: 0, 2: 0, 3: 0, 4: 0}
    percentages["offense"]["10 Double TE QB Sneak"] = {1: 10, 2: 10, 3: 20, 4: 0}
    with open(os.environ['FOOTBALL_HOME'] + "//league_config//plays.yaml", "r") as file:
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
    with open(os.environ['FOOTBALL_HOME'] + "//teams//orders//" + team_name + "-orders.yaml", "w") as file:
        yaml.safe_dump(percentages, file)
    # TODO: Make stats file
    return team_name


def create_low_attrib(week):
    maximum = int((12 - week) / 2) * 20 + 300
    return randint(0, maximum)


def create_high_attrib(week, special):
    total = 5
    maxes = int((11 - week) / 2)
    tot = 0
    number = 600
    if special:
        tot += max(randint(0, number), max(0, randint(- 1.6 * number, number)), max(0, randint(-0.5 * number, number)))
    for _ in range(special, maxes):
        tot += max(randint(0, number), max(0, randint(- 1.6 * number, number)))
    for _ in range(maxes, total):
        tot += randint(0, number)
    return 500 + tot / total - 100 * (tot > 200 * total)


def create_player(nationality, team, team_id, week, attrib, ideal_weight, ideal_height):
    with open(os.environ['FOOTBALL_HOME'] + "//players//ref//player_id.yaml", "r") as file:
        names = yaml.safe_load(file)
    new_name = smallest_missing_in_list(names)
    if names:
        names = names[:new_name] + [new_name] + names[new_name:]
    else:
        names = [0]
    player_id = "Player_" + str(new_name)
    with open(os.environ['FOOTBALL_HOME'] + "//players//ref//player_id.yaml", "w") as file:
        yaml.safe_dump(names, file)
    player = dict()
    player["name"] = name_player(nationality)
    with open(os.environ['FOOTBALL_HOME'] + "//players//ref//player_stats.yaml", "r") as file:
        att = yaml.safe_load(file)
    low_att = att["low attributes"]
    pos_att = att["positional attributes"]
    high_att = att["high attributes"]
    player["nationality"] = nationality
    player["team"] = team
    player["team_id"] = team_id
    player["contract_value"] = 1000
    player["franchised"] = False
    player["franchise next season"] = False
    player["guarantee"] = 0
    player["age"] = 16 + randint(0, 3)
    height = [generate_height(player["age"]), generate_height(player["age"])]
    if abs(height[0] - ideal_height) < abs(height[1] - ideal_height) or ideal_height < 0:
        player["height"] = height[0]
    else:
        player["height"] = height[1]
    weight = [generate_weight(player["height"]), generate_weight(player["height"])]
    if abs(weight[0] - ideal_weight) < abs(weight[1] - ideal_weight) or ideal_weight:
        player["weight"] = weight[0]
    else:
        player["weight"] = weight[1]
    player["base_weight"] = player["weight"]
    player["years_left"] = 0
    player["retiring"] = False
    player["id"] = new_name
    while len(attrib) < 3:
        add = high_att[randint(0, len(high_att) - 1)]
        while add in attrib:
            add = high_att[randint(0, len(high_att) - 1)]
        attrib.append(add)
    for attribute in low_att:
        player[attribute] = 100 + create_low_attrib(week)
    for attribute in pos_att:
        player[attribute] = 150 + randint(0, 100)
    for attribute in high_att:
        player[attribute] = create_high_attrib(week, attribute in attrib)
    with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + player_id + ".yaml", "w") as file:
        yaml.safe_dump(player, file)
    training = {"file name": os.environ['FOOTBALL_HOME'] + "//players//players//" + player_id + ".yaml", "focus": "",
                "route assignment": "", "weight direction": ""}
    with open(os.environ['FOOTBALL_HOME'] + "//players//training//" + player_id + ".yaml", "w") as file:
        yaml.safe_dump(training, file)
    return {player_id: player["name"]}


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
    with open(os.environ['FOOTBALL_HOME'] + "//league_config//list_of_names.yaml", "r") as file:
        names = yaml.safe_load(file)
    random_first = randint(0, 99)
    random_second = randint(0, 99)
    first_name = names[nationality]["first"][random_first]
    second_name = names[nationality]["second"][random_second]
    return first_name + " " + second_name


def add_player(team_id, maximum, week, attrib, ideal_height, ideal_weight):
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams"
    with open(team_folder + "//" + team_id + ".yaml", "r") as team_file:
        team = yaml.safe_load(team_file)
    if team["player"] < maximum:
        team_name = team["team name"]
        team["player"].append(create_player(team["nationality"], team_name, team_id, attrib=attrib, week=week,
                                            ideal_height=ideal_height, ideal_weight=ideal_weight))
        team["salary"] += 1000
        with open(team_folder + "//" + team_id + ".yaml", "w") as team_file:
            yaml.safe_dump(team, team_file)


def add_player_old(team_id, player_id, maximum, max_salary_amount):
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams"
    player_folder = os.environ['FOOTBALL_HOME'] + "//players"
    with open(team_folder + "//" + team_id + ".yaml", "r") as team_file:
        team = yaml.safe_load(team_file)
    with open(player_folder + "//" + player_id + ".yaml", "r") as player_file:
        player = yaml.safe_load(player_file)
    if team["player"] < maximum and team["salary"] + player["contract_value"] <= max_salary_amount:
        team["player"].append(player_id)
        team["salary"] += player["contract_value"]
        with open(team_folder + "//" + team_id + ".yaml", "w") as team_file:
            yaml.safe_dump(team, team_file)

        player["team_id"] = team_id
        player["team"] = team["team name"]
        with open(player_folder + "//" + player_id + ".yaml", "w") as player_file:
            yaml.safe_dump(player, player_file)
        return True
    return False


def ensure_team_has_minimum(minimum):
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams"
    for file in os.listdir(team_folder + "//teams"):
        with open(team_folder + "//teams//" + file, "r") as team_file:
            team = yaml.safe_load(team_file)
        while len(team["player"]) < minimum:

            add_player(file[:len(file) - 5], 999, attrib=[], ideal_height=-1, ideal_weight=-1, week=11)
        with open(team_folder + "//teams//" + file, "w") as team_file:
            yaml.safe_dump(team, team_file)


def remove_player(player_id, team_id, minimum, force=False):
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams"
    player_folder = os.environ['FOOTBALL_HOME'] + "//players"
    with open(team_folder + "//teams//" + team_id + ".yaml", "r") as team_file:
        team = yaml.safe_load(team_file)

    if len(team["player"]) > minimum or force is True:
        del team["player"][player_id]
        potential_players = list(team["player"].keys())[:11]
        with open(team_folder + "//teams//" + team_id + ".yaml", "w") as team_file:
            yaml.safe_dump(team, team_file)
        with open(team_folder + "//orders//" + team_id + "-formation.yaml", "r") as formation_file:
            team_formation = yaml.safe_load(formation_file)
        for form in team_formation:
            replaced = False
            counter = 0
            if player_id in team_formation[form] and not force:
                team_formation[form].remove(player_id)
                while replaced is False:
                    if potential_players[counter] not in team_formation[form]:
                        team_formation[form].append(potential_players[counter])
                        replaced = True
                    else:
                        counter += 1
        with open(team_folder + "//orders//" + team_id + "-formation.yaml", "2") as formation_file:
            yaml.safe_dump(team_formation, formation_file)
        with open(player_folder + "//players//" + player_id + ".yaml", "r") as player_file:
            player = yaml.safe_load(player_file)
        player["team_id"] = "N/A"
        team_name = player["team"]
        player["team"] = "N/A"
        with open(player_folder + "//players//" + player_id + ".yaml", "w") as player_file:
            yaml.safe_dump(player, player_file)
        with open(player_folder + "//free_agents.yaml", "r") as free_agent_file:
            free_agents = yaml.safe_load(free_agent_file)
        free_agents.update({player_id: {"team_id": team_id, "team": team_name, "asking": 1000}})
        # TODO: Change the below to open a bid file on the player
        with open(player_folder + "//free_agents.yaml", "w") as free_agent_file:
            yaml.safe_dump(free_agents, free_agent_file)
        with open(team_folder + "//dead_money//" + team_id + ".yaml", "r") as dead_money_file:
            dead_money = yaml.safe_load(dead_money_file)
        dead_money.update({player_id: {"years": player["years_left"],
                                       "amount": player["guarantee"] * player["contract_value"]}})
        with open(team_folder + "//dead_money//" + str(team_id) + ".yaml", "w") as dead_money_file:
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


def make_team(name, nationality, season_number, tier_adjust=0):
    league_folder = os.environ['FOOTBALL_HOME'] + "//leagues//" + str(season_number)
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams"

    files = os.listdir(league_folder)
    tier = 0

    for file in files:
        if "round" not in file and "cup" not in file and "promotions" not in file and 'season' not in file:
            if int(file) > int(tier):
                tier = int(file)

    tier -= tier_adjust
    teams = []
    for league in os.listdir(league_folder + "//" + str(tier)):
        with open(league_folder + "//" + str(tier) + "//" + league + "//teams.yaml") as file:
            teams += yaml.safe_load(file)["teams"]
    for team in teams:
        with open(team_folder + "//teams//" + team + ".yaml") as team_file:
            bot = yaml.safe_load(team_file)["bot"]
        if bot is False:
            teams.remove(team)
    print("adksljf")
    print(teams)
    if len(teams) == 0:
        if tier > 1:
            make_team(name, nationality, season_number, tier_adjust + 1)
        else:
            print("No teams available")
    place = randint(0, len(teams) - 1)
    print(team_folder + "//teams//" + teams[place] + ".yaml")
    with open(team_folder + "//teams//" + teams[place] + ".yaml", "r") as team_file:
        team_stuff = yaml.safe_load(team_file)
    team_stuff["bot"] = False
    team_stuff["nationality"] = nationality
    team_stuff["team name"] = name
    team_stuff["salary"] = 22000
    team_stuff["draft picks"] = list(range(1, 12))
    print("team")
    print(team_stuff)
    new_table = []
    print(tier)
    print(teams[place])
    with open(league_folder + "//" + str(tier) + "//" + team_stuff["leagues name"] + "//table.csv", "r") as csv_file:
        table = csv.reader(csv_file, delimiter=',', quotechar="~")
        for row in table:
            new_table.append(row)

    for row in new_table:
        print(row)
        print(team_stuff["leagues name"])
        print(teams[place])
        if teams[place] == row[1]:
            print("XXX")
            row[2] = name
    with open(league_folder + "//" + str(tier) + "//" + team_stuff["leagues name"] + "//table.csv", 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        for row in new_table:
            writer.writerow(row)
    for player in team_stuff["player"]:
        remove_player(player, teams[place], -1, True)
    with open(team_folder + "//teams//" + teams[place] + ".yaml", "r") as team_file:
        print(yaml.safe_load(team_file))
    team_stuff["player"] = {}
    for i in range(22):
        team_stuff["player"].update(create_player(team_stuff["nationality"], name, teams[place], attrib=[], week=8,
                                                  ideal_height=-1, ideal_weight=-1))
    formation = list(team_stuff["player"].keys())[:11]
    with open(team_folder + "//orders//" + teams[place] + "-formation.yaml", "r") as formation_file:
        formations = yaml.safe_load(formation_file)
    for style in formations:
        formations[style] = formation
    with open(team_folder + "//orders//" + teams[place] + "-formation.yaml", "w") as formation_file:
        yaml.safe_dump(formations, formation_file)

    team_stuff["trophies"] = {'cup': [0]}
    with open(team_folder + "//teams//" + teams[place] + ".yaml", "w") as team_file:
        yaml.safe_dump(team_stuff, team_file)

    with open(team_folder + "//ref//team_id.yaml", "r") as id_file:
        ids = yaml.safe_load(id_file)
    while name in list(ids.keys()):
        name = input("please enter a new name as that one is taken")
    ids.update({name: teams[place]})
    with open(team_folder + "//ref//team_id.yaml", "w") as id_file:
        yaml.safe_dump(ids, id_file)
    # TODO: Change name in cup - cup fixtures file and latest round.


def update_draft_picks(week):
    team_folder = os.environ['FOOTBALL_HOME'] + "//teams"
    for team in os.listdir(team_folder + "//teams"):
        with open(team_folder + "//teams//" + team + ".yaml", "r") as team_file:
            team_stuff = yaml.safe_load(team_file)
        team_stuff["draft picks"] = draft_pick_single_team(team_stuff["draft picks"], week)
        with open(team_folder + "//teams//" + team + ".yaml", "r") as team_file:
            yaml.safe_dump(team_stuff, team_file)


def draft_pick_single_team(draft_picks, week):
    while week in draft_picks:
        draft_picks.remove(week)
    draft_picks.append(week)
    return week

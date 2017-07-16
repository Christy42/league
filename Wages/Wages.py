import os
import random
import yaml
import datetime

from math import floor

import create_team


def wage_function(position, skill, age, contract_length):
    with open(os.environ['FOOTBALL_HOME'] + "//wages_config//" + "wages.yaml") as wages_file:
        value = yaml.safe_load(wages_file)[position]
    age_factor = min(max((30 - age) / 10.0, 0), 1)
    skill += (100 - skill) * contract_length * age_factor / 10.0
    wage = value["exp_value"] ** (skill / 10.0) * value["multiplication"] + value["const"]
    minimum = random.randint(800, 900) / 1000.0
    wage = round(wage, 2)
    return [wage, round(minimum * wage, 2)]


def guaranteed():
    minimum = random.randint(800, 900) / 1000.0
    guarantee = min(random.randint(0, 50), random.randint(0, 50)) / 100.0
    return [guarantee, guarantee * minimum]


def decision_matrix(bids, guarantee, min_guarantee, min_wage, wage, factor, base_team, age, contract_length):
    bids["Minimum"] = {"guarantee": min_guarantee, "wages": min_wage[contract_length], "length": contract_length}
    extra_guarantee = {team: min(max(bids[team]["guarantee"] - guarantee * factor, 0), 0.3) * wage[3] for team in bids}
    extra_wages = {team: extra_guarantee[team] + max((bids[team]["wages"] - wage[bids[team]["length"]]), 0)
                   for team in bids}
    lower_wages = {team: extra_wages[team] - max(wage[bids[team]["length"]] - bids[team]["wages"], 0)
                   for team in bids}
    lower_guarantee = {team: lower_wages[team] - max(guarantee - bids[team]["guarantee"] * factor, 0) * wage[5]
                       for team in lower_wages}
    home_team = {team: lower_guarantee[team] * (1 + 0.1 * (team == base_team)) * (1 + random.randint(0, 10) / 10.0)
                 for team in bids}
    best_bid = home_team["Minimum"]
    winner_list = []
    for bid in home_team:
        if home_team[bid] >= best_bid:
            if home_team[bid] > best_bid:
                winner_list = []
                best_bid = home_team[bid]
            winner_list.append(bid)
    print(winner_list)
    return winner_list[random.randint(0, len(winner_list) - 1)]


def check_position(player_id):
    with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + player_id) as player_file:
        player_stats = yaml.safe_load(player_file)
    with open(os.environ['FOOTBALL_HOME'] + "//wages_config//" + "position_decision.yaml") as position_file:
        position_stats = yaml.safe_load(position_file)
    wages = {position: 0 for position in position_stats}
    pos = ""
    wage = 0
    value = 0
    for position in position_stats:
        position_sum = 0.0
        for part in position_stats[position]:
            if part != "names":
                position_sum += float(part)
                wages[position] += float(part) * floor(float(player_stats[position_stats[position][part]])) / 10.0
        position_jump = 0
        for place in position_stats[position]["names"]:
            position_jump = max(position_jump, min(player_stats[place + "_exp"] / 10.0, 35.0) * 5)
        wages[position] += position_jump
        wages[position] /= (2.5 + position_sum)
        wages[position] = round(wages[position])

        result = wage_function(position, wages[position], player_stats["age"], 3)[0]
        if result > wage:
            pos = position
            wage = result
            value = wages[position]
    return [pos, value, player_stats["age"]]


def generate_wages(player):
    guarantee = guaranteed()
    pos = check_position(player)
    wage = {}
    for i in range(3, 7):
        wage.update({i: wage_function(pos[0], pos[1], pos[2], i)})
    return [wage, guarantee]


def add_player_to_free_agency(player_file):
    with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + player_file, "r") as player_file_name:
        player_stats = yaml.safe_load(player_file_name)
    with open(os.environ['FOOTBALL_HOME'] + "//players//ref//player_stats.yaml", "r") as stat_file:
        low_stats = yaml.safe_load(stat_file)["low attributes"]
    wages = generate_wages(player_file)
    with open(os.environ['FOOTBALL_HOME'] + "//teams//ref//team_id.yaml") as team_file:
        team = yaml.safe_load(team_file)
    if player_stats["team"] in team.keys():
        team = team[player_stats["team"]]
    else:
        team = "bot"
    factor = random.randint(1, 75) / 100.0 + 1
    wage_stats = {length: {"wage": wages[0][length][0], "min_wage": wages[0][length][1]} for length in range(3, 7)}
    print_stats = {"team": team, "min_guarantee": wages[1][1], "guarantee": wages[1][0], "factor": factor,
                   "create_time": datetime.datetime.now(), "bids": {}, "age": player_stats["age"]}
    print_stats.update(wage_stats)
    max_exp = 0
    exp_style = ""
    for stat in player_stats:
        if stat in low_stats:
            print_stats[stat] = round(int(player_stats[stat]), -1)
        if "exp" in stat and player_stats[stat] > max_exp:
            max_exp = player_stats[stat]
            print_stats[stat] = player_stats[stat]

            if exp_style != "":
                print_stats.pop(exp_style)
                exp_style = stat
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + player_file, "w") as trading_file:
        yaml.safe_dump(print_stats, trading_file)


def add_free_agency_bid(player, team, wage, length, guarantee):
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + player + ".yaml", "r") as trade_file:
        trade = yaml.safe_load(trade_file)
    trade["bids"].update({team: {"wages": wage, "length": length, "guarantee": guarantee}})
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + player + ".yaml", "w") as trade_file:
        yaml.safe_dump(trade, trade_file)


def decide_bids(minimum_team, maximum_team, salary_limit):
    for file in os.listdir(os.environ["FOOTBALL_HOME"] + "//trading//trades"):
        with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + file, "r") as bid_file:
            bid_decision = yaml.safe_load(bid_file)
        if 3 in bid_decision.keys():
            if (datetime.datetime.now() - bid_decision["create_time"]).days < 8:
                continue
        wages = {3: bid_decision[3]["wage"], 4: bid_decision[4]["wage"],
                 5: bid_decision[5]["wage"], 6: bid_decision[6]["wage"]}
        min_wages = {3: bid_decision[3]["min_wage"], 4: bid_decision[4]["min_wage"],
                     5: bid_decision[5]["min_wage"], 6: bid_decision[6]["min_wage"]}
        team_transfer = decision_matrix(bid_decision["bids"], bid_decision["guarantee"], bid_decision["min_guarantee"],
                                        min_wages, wages,
                                        bid_decision["factor"], bid_decision["team"], bid_decision["age"], 3)
        if team_transfer == "Minimum":
            bid_decision["create_time"] = datetime.datetime.now()
            bid_decision["bids"] = {}
            bid_decision[3]["min_wage"] *= (0.75 + random.random() / 2.0)
            bid_decision[3]["wage"] *= (0.75 + random.random() / 2.0)
            bid_decision[4]["min_wage"] *= (0.75 + random.random() / 2.0)
            bid_decision[4]["wage"] *= (0.75 + random.random() / 2.0)
            bid_decision[5]["min_wage"] *= (0.75 + random.random() / 2.0)
            bid_decision[5]["wage"] *= (0.75 + random.random() / 2.0)
            bid_decision[6]["min_wage"] *= (0.75 + random.random() / 2.0)
            bid_decision[6]["wage"] *= (0.75 + random.random() / 2.0)
            create_team.remove_player(file[:-5], bid_decision["team"], minimum_team, True)
            with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + file, "w") as bid_file:
                yaml.safe_dump(bid_decision, bid_file)
        elif bid_decision["team"] == team_transfer:
            os.remove(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + file)
            with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + file, "r") as player_file:
                player = yaml.safe_load(player_file)
            player["guarantee"] = bid_decision["bids"][team_transfer]["guarantee"]
            player["years_left"] = bid_decision["bids"][team_transfer]["length"]
            player["contract_value"] = bid_decision["bids"][team_transfer]["wages"]
            with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + file, "w") as player_file:
                yaml.safe_dump(player, player_file)
        else:
            os.remove(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + file)
            create_team.remove_player(file[:-5], bid_decision["team"], minimum_team, True)
            create_team.add_player_old(team_transfer, file[:-5], maximum_team, salary_limit)
            with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + file, "r") as player_file:
                player = yaml.safe_load(player_file)
            player["guarantee"] = bid_decision["bids"][team_transfer]["guarantee"]
            player["years_left"] = bid_decision["bids"][team_transfer]["length"]
            player["contract_value"] = bid_decision["bids"][team_transfer]["wages"]
            with open(os.environ['FOOTBALL_HOME'] + "//players//players//" + file, "w") as player_file:
                yaml.safe_dump(player, player_file)

values = []
greater30 = 0
less20 = 0
for i in range(1000):
    inc = guaranteed()[0]
    values.append(inc)
    if inc > 0.3:
        greater30 += 1
    elif inc < 0.2:
        less20 += 1

# add_free_agency_bid("Player_1096", "Team_46", 6700000, 6, 0.9)
# add_free_agency_bid("Player_1096", "Team_15", 2100000, 3, 2)
# decide_bids(10, 80, 130000000)


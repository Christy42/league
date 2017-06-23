import os
import random
import yaml
import datetime

from math import floor


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
    bids["Minimum"] = {"Guarantee": min_guarantee, "Wages": min_wage, "Length": contract_length}
    age_factor = min(max((30 - age) / 10.0, 0), 1)
    for bid in bids:
        bids["Wages"] = bid["Wages"] * (1 + contract_length * age_factor / 10.0) / \
                        (1 + bids["Length"] * age_factor / 10.0)
        bids["Length"] = contract_length
    bid_value = {team: min(bids[team]["Guarantee"], guarantee) * factor + min(bids[team]["Wages"], wage)
                 for team in bids}
    extra_guarantee = {team: bid_value[team] + max(min(guarantee, bids[team]["Guarantee"] - guarantee) *
                                                   ((factor - 1) / 3 + 1), 0)
                       for team in bid_value}
    extra_wages = {team: extra_guarantee[team] + max((bids[team]["Wages"] - wage) * 0.93, 0) for team in bid_value}
    lower_wages = {team: extra_wages[team] - max(wage - max(bids[team]["Wages"], min_wage) * 0.07, 0) -
                   max(min_wage - bids[team]["Wages"], 0) * 0.15 for team in bid_value}
    lower_guarantee = {team: lower_wages[team] - max(guarantee - max(bids[team]["Guarantee"], min_guarantee) *
                                                     (factor - 0.93), 0) -
                       max(min_guarantee - bids[team]["Guarantee"], 0) * (factor - 0.85) for team in lower_wages}
    home_team = {team: lower_guarantee[team] * (1 + 0.1 * (team == base_team)) * (1 + random.randint(0, 10) / 10.0)
                 for team in bid_value}
    best_bid = home_team["Minimum"]
    winner_list = []
    for bid in home_team:
        if home_team[bid] <= best_bid:
            if home_team[bid] < best_bid:
                winner_list = []
                best_bid = home_team[bid]
            winner_list.append(bid)
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
        if random.randint(0, 99) != 0:
            return 0
        team = "bot"
    wage_stats = {length: {"wage": wages[0][length][0], "min_wage": wages[0][length][1]} for length in range(3, 7)}
    print_stats = {"team": team, "min_guarantee": wages[1][1], "guarantee": wages[1][0],
                   "create_time": datetime.datetime.now(), "bids": {}}
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
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + player_file + ".yaml", "w") as trading_file:
        yaml.safe_dump(print_stats, trading_file)
    return 1


def add_free_agency_bid(player, team, wage, length, guarantee):
    with open(os.environ['FOOTBALL_HOME'] + "//trading//trades//" + player + ".yaml", "r") as trade_file:
        trade = yaml.safe_load(trade_file)
    trade["bids"].update({team: {"wages": wage, "length": length, "guarantee": guarantee}})

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


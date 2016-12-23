import csv
import yaml
import pandas
import operator

from random import randint


# reorder columns
def set_column_sequence(dataframe, seq, front=True):

     # Takes a dataframe and a subsequence of its columns,
     #  returns dataframe with seq as first columns if "front" is True,
     #  and seq as last columns if "front" is False.

    cols = seq[:] # copy so we don't mutate seq
    for x in dataframe.columns:
        if x not in cols:
            if front: # we want "seq" to be in the front
                # so append current column to the end of the list
                cols.append(x)
            else:
                # we want "seq" to be last, so insert this
                # column in the front of the new column list
                # "cols" we are building:
                cols.insert(0, x)
    return dataframe[cols]


class LeagueTable:
    def __init__(self, team_ids, yaml_file, csv_file, name):
        self._name = name
        self._yaml_file = yaml_file
        self._csv_file = csv_file
        self._team_ids = team_ids

    def create_schedule(self):
        """ Create a schedule for the teams in the list and return it"""
        s = []
        ids = list(self._team_ids.keys())
        if len(ids) % 2 == 1:
            ids = ids + ["BYE"]

        for i in range(len(ids)-1):
            mid = int(len(ids) / 2)
            l1 = ids[:mid]
            l2 = ids[mid:]
            l2.reverse()
            # Switch sides after each week
            if i % 2 == 1:
                s = s + [zip(l1, l2)]
            else:
                s = s + [zip(l2, l1)]
            ids.insert(1, ids.pop())

        week_count = 1
        fixtures = {}
        for week in s:
            match_count = 1
            fixtures[week_count] = {}
            for match in week:
                fixtures[week_count][match_count] = [match[0], match[1]]
                match_count += 1
            week_count += 1
        with open(self._yaml_file, "w") as file:
            yaml.safe_dump(fixtures, file)

    def play_week(self, week_number):
        with open(self._yaml_file, "r") as file:
            games = yaml.safe_load(file)[week_number]
        scores = []
        print(self._yaml_file)
        print(games)
        for g in games:
            print(g)
            print(games[g])
            # Looking for [team_id, for]
            result_0 = [games[g][0], randint(0, 30)]
            result_1 = [games[g][1], randint(0, 30)]
            scores.append((result_0, result_1))
        # Need to actually play the above games
        self.update_scores(scores)

    def change_name(self, team_id, new_name):
        with open(self._csv_file, "r") as file:
            data = yaml.safe_load(file)
        pass

    def update_scores(self, scores):
        # TODO: Read in the values as some sort of structure, ignore first line and column though
        with open(self._csv_file, "r") as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            count_row = 0
            stats = {}
            title_row = []
            for row in reader:
                if count_row == 0:
                    title_row = row[1:]
                    stats = {row[i]: [] for i in range(1, len(row))}
                else:
                    for i in range(0, len(row[1:])):
                        stats[title_row[i]].append(row[i+1])
                count_row += 1
        # TODO: Amend the values
        for result_0, result_1 in scores:
            print(stats)
            stats["played"][stats["team id"].index(result_0[0])] = stats["played"][stats["team id"].index(result_0[0])]
            stats["played"][stats["team id"].index(result_0[0])] = \
                int(stats["played"][stats["team id"].index(result_0[0])]) + 1
            stats["played"][stats["team id"].index(result_1[0])] = \
                int(stats["played"][stats["team id"].index(result_1[0])]) + 1
            stats["for"][stats["team id"].index(result_0[0])] = \
                int(stats["for"][stats["team id"].index(result_0[0])]) + result_0[1]
            stats["for"][stats["team id"].index(result_1[0])] = \
                int(stats["for"][stats["team id"].index(result_1[0])]) + result_1[1]
            stats["against"][stats["team id"].index(result_0[0])] = \
                int(stats["against"][stats["team id"].index(result_0[0])]) + result_1[1]
            stats["against"][stats["team id"].index(result_1[0])] = \
                int(stats["against"][stats["team id"].index(result_1[0])]) + result_0[1]
            if int(result_0[1]) > int(result_1[1]):
                stats["wins"][stats["team id"].index(result_0[0])] = \
                   int(stats["wins"][stats["team id"].index(result_0[0])]) + 1
                stats["losses"][stats["team id"].index(result_1[0])] = \
                    int(stats["losses"][stats["team id"].index(result_1[0])]) + 1
            elif int(result_0[1]) == int(result_1[1]):
                stats["draws"][stats["team id"].index(result_0[0])] = \
                   int(stats["draws"][stats["team id"].index(result_0[0])]) + 1
                stats["draws"][stats["team id"].index(result_1[0])] = \
                    int(stats["draws"][stats["team id"].index(result_1[0])]) + 1
            else:
                stats["wins"][stats["team id"].index(result_1[0])] = \
                   int(stats["wins"][stats["team id"].index(result_1[0])]) + 1
                stats["losses"][stats["team id"].index(result_0[0])] = \
                    int(stats["losses"][stats["team id"].index(result_0[0])]) + 1
            stats["win%"][stats["team id"].index(result_0[0])] = \
                ((int(stats["wins"][stats["team id"].index(result_0[0])]) +
                 int(stats["draws"][stats["team id"].index(result_0[0])]) / 2) /
                 int(stats["played"][stats["team id"].index(result_0[0])]))
            stats["win%"][stats["team id"].index(result_1[0])] = \
                ((int(stats["wins"][stats["team id"].index(result_1[0])]) +
                 int(stats["draws"][stats["team id"].index(result_1[0])]) / 2) /
                 int(stats["played"][stats["team id"].index(result_1[0])]))
            stats["win%"][stats["team id"].index(result_1[0])] = \
                str(round(float(stats["win%"][stats["team id"].index(result_1[0])]), 2) * 100) + "%"
            stats["wins"][stats["team id"].index(result_0[0])] = int(stats["wins"][stats["team id"].index(result_0[0])])
            stats["wins"][stats["team id"].index(result_1[0])] = int(stats["wins"][stats["team id"].index(result_1[0])])
            stats["points difference"][stats["team id"].index(result_0[0])] = \
                (int(stats["for"][stats["team id"].index(result_0[0])]) -
                 int(stats["against"][stats["team id"].index(result_0[0])]))
            stats["points difference"][stats["team id"].index(result_1[0])] = \
                (int(stats["for"][stats["team id"].index(result_1[0])]) -
                 int(stats["against"][stats["team id"].index(result_1[0])]))
        print(stats)
        stats["position"] = [x for x in range(1, 13)]
        stats_1 = pandas.DataFrame(stats)
        # TODO: Sort the values
        cols = set_column_sequence(stats_1, ["position", "team name", "team id", "played", "wins", "draws", "losses",
                                             "win%", "for",
                                             "against", "points difference"])
        with open(self._csv_file, "w") as file:
            file.write(cols.to_csv())

    def initialise_file(self):
        with open(self._csv_file, 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["position", "team id", "team name", "played", "wins", "draws", "losses",
                            "win%", "for", "against", "points difference"])
            position = 1
            for row in self._team_ids:
                writer.writerow([position, row, self._team_ids[row], "0", '0', '0', '0', '0', '0', '0', '0'])
                position += 1

    def display_file(self):
        # Will display the file in an easy to read format (maybe csv for the moment)
        pass

# TODO: Create set of leagues each with 12 teams.  Sets us a schedule and holds it ready to play

# TODO: Amend leagues files on the basis of the games

# TODO: Amend stat files on the basis of the games for both teams and players

# TODO: Figures out promotion and demotion

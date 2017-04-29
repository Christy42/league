import create_team


def test_create_low_attrib():
    list_of_ans = []
    random_length = 10000
    for _ in range(random_length):
        list_of_ans.append(create_team.create_low_attrib(3))
    assert max(list_of_ans) <= 380
    assert sum([1 if list_of_ans[i] < 100 else 0 for i in range(len(list_of_ans))]) < 0.33 * random_length
    assert sum([1 if list_of_ans[i] < 200 else 0 for i in range(len(list_of_ans))]) < 0.6 * random_length
    assert sum([1 if list_of_ans[i] < 300 else 0 for i in range(len(list_of_ans))]) < 8.5 * random_length


def test_create_high_attrib():
    list_of_ans = []
    random_length = 10000
    for _ in range(random_length):
        list_of_ans.append(create_team.create_high_attrib(3, 2))
    assert max(list_of_ans) <= 880
    assert sum([1 if list_of_ans[i] < 100 else 0 for i in range(len(list_of_ans))]) < 0.33 * random_length
    assert sum([1 if list_of_ans[i] < 400 else 0 for i in range(len(list_of_ans))]) < 0.7 * random_length
    assert sum([1 if list_of_ans[i] < 800 else 0 for i in range(len(list_of_ans))]) < 0.9 * random_length


def test_smallest_missing_in_list():
    assert create_team.smallest_missing_in_list([1, 2]) == 0
    assert create_team.smallest_missing_in_list([0, 1, 3]) == 2
    assert create_team.smallest_missing_in_list([0, 1, 2]) == 3

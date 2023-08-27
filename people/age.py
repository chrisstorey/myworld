import random

from faker import Faker

fake = Faker()
Faker.seed(0)

age_under18_names = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
]

age_under18_weights = [
    5075,
    5280,
    5451,
    5631,
    5622,
    5677,
    5814,
    6004,
    5910,
    5815,
    5746,
    5819,
    5647,
    5561,
    5346,
    5306,
    5171,
    5125,
]

age_non_dep_names = ["16", "17"]

age_non_dep_weights = [5171, 5125]

age_over18_names = [
    "18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    "30",
    "31",
    "32",
    "33",
    "34",
    "35",
    "36",
    "37",
    "38",
    "39",
    "40",
    "41",
    "42",
    "43",
    "44",
    "45",
    "46",
    "47",
    "48",
    "49",
    "50",
    "51",
    "52",
    "53",
    "54",
    "55",
    "56",
    "57",
    "58",
    "59",
    "60",
    "61",
    "62",
    "63",
    "64",
    "65",
    "66",
    "67",
    "68",
    "69",
    "70",
    "71",
    "72",
    "73",
    "74",
    "75",
    "76",
    "77",
    "78",
    "79",
    "80",
    "81",
    "82",
    "83",
    "84",
    "85",
    "86",
    "87",
    "88",
    "89",
    "90+",
]

age_over18_weights = [
    1388,
    1316,
    1377,
    1414,
    1489,
    1516,
    1527,
    1611,
    1617,
    1671,
    1709,
    1681,
    1676,
    1696,
    1656,
    1675,
    1676,
    1640,
    1657,
    1656,
    1671,
    1678,
    1614,
    1506,
    1486,
    1515,
    1547,
    1577,
    1647,
    1721,
    1780,
    1737,
    1781,
    1778,
    1806,
    1804,
    1814,
    1796,
    1755,
    1714,
    1651,
    1581,
    1544,
    1509,
    1450,
    1395,
    1342,
    1344,
    1322,
    1279,
    1284,
    1304,
    1333,
    1400,
    1508,
    1151,
    1106,
    1088,
    998,
    880,
    778,
    792,
    769,
    729,
    673,
    618,
    565,
    499,
    451,
    411,
    365,
    314,
    1188,
]

age_working_age_names = [
    "18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    "30",
    "31",
    "32",
    "33",
    "34",
    "35",
    "36",
    "37",
    "38",
    "39",
    "40",
    "41",
    "42",
    "43",
    "44",
    "45",
    "46",
    "47",
    "48",
    "49",
    "50",
    "51",
    "52",
    "53",
    "54",
    "55",
    "56",
    "57",
    "58",
    "59",
    "60",
    "61",
    "62",
    "63",
    "64",
]

age_working_age_weights = [
    1388,
    1316,
    1377,
    1414,
    1489,
    1516,
    1527,
    1611,
    1617,
    1671,
    1709,
    1681,
    1676,
    1696,
    1656,
    1675,
    1676,
    1640,
    1657,
    1656,
    1671,
    1678,
    1614,
    1506,
    1486,
    1515,
    1547,
    1577,
    1647,
    1721,
    1780,
    1737,
    1781,
    1778,
    1806,
    1804,
    1814,
    1796,
    1755,
    1714,
    1651,
    1581,
    1544,
    1509,
    1450,
    1395,
    1342,
]

age_over65_names = [
    "65",
    "66",
    "67",
    "68",
    "69",
    "70",
    "71",
    "72",
    "73",
    "74",
    "75",
    "76",
    "77",
    "78",
    "79",
    "80",
    "81",
    "82",
    "83",
    "84",
    "85",
    "86",
    "87",
    "88",
    "89",
    "90",
]

age_over65_weights = [
    1344,
    1322,
    1279,
    1284,
    1304,
    1333,
    1400,
    1508,
    1151,
    1106,
    1088,
    998,
    880,
    778,
    792,
    769,
    729,
    673,
    618,
    565,
    499,
    451,
    411,
    365,
    314,
    1188,
]


def age_under18() -> int:
    age = random.choices(age_under18_names, weights=age_under18_weights)
    return_age = int(age[0])
    return return_age


def age_non_dep() -> int:
    age = random.choices(age_non_dep_names, weights=age_non_dep_weights)
    return_age = int(age[0])
    return return_age


def age_over18() -> int:
    age = random.choices(age_over18_names, weights=age_over18_weights)
    return_age = int(age[0])
    return return_age


def age_working_age() -> int:
    age = random.choices(age_working_age_names, weights=age_working_age_weights)
    return_age = int(age[0])
    return return_age


def age_over65() -> int:
    age = random.choices(age_over65_names, weights=age_over65_weights)
    return_age = int(age[0])
    return return_age


def year_of_birth(age: int) -> int:
    import datetime

    now = datetime.datetime.now()
    year = now.year - age
    return year


def fake_dob(year_of_b: int):
    birth = fake.date_of_birth()
    birth = birth.replace(year=year_of_b)
    return birth


def dob_over65():
    age = age_over65()
    year = year_of_birth(age)
    dob = fake_dob(year)
    return dob, age


def dob_working_age():
    age = age_working_age()
    year = year_of_birth(age)
    dob = fake_dob(year)
    return dob, age


def dob_under18():
    age = age_under18()
    year = year_of_birth(age)
    dob = fake_dob(year)
    return dob, age


def dob_over18():
    age = age_over18()
    year = year_of_birth(age)
    dob = fake_dob(year)
    return dob, age


def dob_non_dep():
    age = age_non_dep()
    year = year_of_birth(age)
    dob = fake_dob(year)
    return dob, age

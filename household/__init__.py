import random

household_options = [
    "One person household: Aged 65 and over",
    "One person household: Other",
    "One family only: All aged 65 and over",
    "One family only: Married couple: No children",
    "One family only: Married couple: One dependent child",
    "One family only: Married couple: Two or more dependent children",
    "One family only: Married couple: All children non-dependent",
    "One family only: Same-sex civil partnership couple: No children",
    "One family only: Same-sex civil partnership couple: One dependent child",
    "One family only: Same-sex civil partnership couple: Two or more dependent children",
    "One family only: Same-sex civil partnership couple: All children non-dependent",
    "One family only: Cohabiting couple: No children",
    "One family only: Cohabiting couple: One dependent child",
    "One family only: Cohabiting couple: Two or more dependent children",
    "One family only: Cohabiting couple: All children non-dependent",
    "One family only: Lone parent: One dependent child",
    "One family only: Lone parent: Two or more dependent children",
    "One family only: Lone parent: All children non-dependent",
    "Other household types: With one dependent child",
    "Other household types: With two or more dependent children",
    "Other household types: All full-time students",
    "Other household types: All aged 65 and over",
    "Other household types: Other",
]

household_weights = [
    122328,
    172407,
    82117,
    123188,
    59304,
    97471,
    57919,
    1187,
    72,
    58,
    27,
    51620,
    19780,
    20742,
    5007,
    39794,
    31700,
    35216,
    13510,
    13870,
    5562,
    2796,
    44325,
]


def household():
    household_type = random.choices(household_options, weights=household_weights, k=100)
    return household_type

import random

country_names = ["en_GB",
                 "en_IE",
                 "en_IN",
                 "ro_RO",
                 "pl_PL",
                 "lt_LT",
                 "de_DE",
                 "en_US",
                 "zh_CN",
                 "tw_GH"
                 ]

country_names_weights = [840,
                         10,
                         61,
                         26,
                         24,
                         6,
                         6,
                         5,
                         4,
                         18
                         ]


def country_name():
    name = random.choices(country_names, weights=country_names_weights)
    return name

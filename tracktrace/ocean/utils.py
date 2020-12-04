import copy
import re
import pandas as pd


LETTERS = {
    "A": 10,
    "B": 12,
    "C": 13,
    "D": 14,
    "E": 15,
    "F": 16,
    "G": 17,
    "H": 18,
    "I": 19,
    "J": 20,
    "K": 21,
    "L": 23,
    "M": 24,
    "N": 25,
    "O": 26,
    "P": 27,
    "Q": 28,
    "R": 29,
    "S": 30,
    "T": 31,
    "U": 32,
    "V": 34,
    "W": 35,
    "X": 36,
    "Y": 37,
    "Z": 38,
}


def validate_container_number(number, separate=False, crp=None):
    number = number.upper()
    number = number.replace(" ", "").replace("/", "").replace("-","").strip()
    last_digit_ok = False
    valid_format = False

    if not crp:
        crp = re.compile("(\D{4})(\d{7})")

    found = crp.search(number)
    if found:
        check_against = number[-1]
        values = []

        prefix = found.group(1)
        values.append(LETTERS[prefix[0]] * 1)
        values.append(LETTERS[prefix[1]] * 2)
        values.append(LETTERS[prefix[2]] * 4)
        values.append(LETTERS[prefix[3]] * 8)

        num = found.group(2)
        values.append(int(num[0]) * 16)
        values.append(int(num[1]) * 32)
        values.append(int(num[2]) * 64)
        values.append(int(num[3]) * 128)
        values.append(int(num[4]) * 256)
        values.append(int(num[5]) * 512)

        total1 = sum(values)
        cd = total1 - (int(total1 / 11) * 11)
        if cd > 9:
            cd = int(str(cd)[-1])  # take last digit if 10 or greater
        if int(cd) == int(check_against):
            last_digit_ok = True
        else:
            raise ValueError("incorrect container number")
            print("incorrect container number")

    else:
        raise ValueError("incorrect container number")
        print("incorrect container number")

    match = crp.findall(number)
    if len(match) == 1:
        valid_format = True
    else:
        raise ValueError("invalid container number format")
        print("invalid container number format")

    if valid_format and last_digit_ok:
        if separate:
            return (found.group(1), found.group(2))
        else:
            return number
    else:
        raise ValueError("incorrect format or number")


def create_df(updates_dict):
    updates = copy.copy(updates_dict)
    df = pd.DataFrame(updates)
    df["date"] = pd.to_datetime(df["date"])
    return df

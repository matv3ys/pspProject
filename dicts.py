language_dict = {
    1: "Python",
    2: "C"
}

status_dict = {
    0: "OK",
    1: "WA",
    2: "CE",
    3: "RE",
    4: "TL",
    5: "Waiting",
    6: "Testing"
}

def get_status_code(status):
    for k, v in status_dict.items():
        if v == status:
            return int(k)
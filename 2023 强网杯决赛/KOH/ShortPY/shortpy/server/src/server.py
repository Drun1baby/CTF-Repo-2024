import docker
import string
import random
import tempfile
import datetime
import os
import sys
import struct
import json
import hashlib
import secrets
import time

from filelock import FileLock
from typing import Dict

WELCOME = """
   _____ _      ___       _   _____       _ 
  / ____| |    / _ \     | | |  __ \     | |
 | (___ | |__ | | | |_ __| |_| |__) |   _| |
  \___ \| '_ \| | | | '__| __|  ___/ | | | |
  ____) | | | | |_| | |  | |_| |   | |_| |_|
 |_____/|_| |_|\___/|_|   \__|_|    \__, (_)
                                     __/ |  
                                    |___/   
"""

client = docker.from_env()


def calc_payload_score(payload: str) -> int:
    return sum(ord(char) for char in payload)

# Flag is under /flag/
def gernrate_flag(team_index: int) -> str:
    flag_name = f"flag{secrets.token_hex()[:24]}.txt"
    flag_path = os.path.join(f"/flag{team_index}", flag_name)
    with open(flag_path, "w") as f:
        f.write("flag{%s}" % secrets.token_hex()[:32])

    os.chmod(flag_path, 0o655)

    return flag_path


def get_team_name_index(teams_data: Dict[str, str], token: str) -> int:
    key_list = list(teams_data.keys())

    return key_list.index(token) + 1


def valid_payload(team_index: int, payload: str) -> bool:
    global client

    # Store the payload into the file
    f = tempfile.NamedTemporaryFile(delete=False, mode="w")
    f.write(payload)
    os.chmod(f.name, 0o655)
    f.close()

    flag_path = gernrate_flag(team_index)

    container_name = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(0x10)
    )

    try:
        container = client.containers.run(
            "koh_python",
            f"/usr/bin/python3.11 chall.py {f.name}",
            name=container_name,
            detach=False,
            cpu_count=1,
            mem_limit="128m",
            network_disabled=True,
            user="pwn",
            volumes={
                "temp-directory": {"bind": "/tmp", "mode": "ro"},
                f"flag{team_index}": {"bind": "/flag", "mode": "ro"},
            },
            read_only=True,
            remove=True,
        )
    except docker.errors.ContainerError as exc:
        container = b"Exceptions\n"

    os.remove(f.name)

    with open(flag_path) as f:
        flag = f.read()

    os.remove(flag_path)

    if flag == container.decode():
        print(f"Congratulations! Here is your flag: {flag}\n")
        return True

    
    return False


def gen_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def check_data_and_add_timestamp(data):
    ranklist = []
    tokenlist = []
    for it in data["data"]:
        if it["teamtoken"] in tokenlist:
            print("dup teamtokoen")
            return False
        tokenlist.append(it["teamtoken"])
        ranklist.append(it["rank"])
    ranklist.sort()
    for i in range(len(ranklist)):
        if ranklist[i] != i + 1 and ranklist[i] != ranklist[i - 1]:
            print("wrong rank")
            return False

    data["updatetime"] = time.time()
    return data


if __name__ == "__main__":
    print(WELCOME)
    print(
        "Welcome to shortpy chal!\nNow It's time to show your python skill.\nIn addition, the team with the lowest ASCII value of the payload will get a higher ranking.\nGood luck!\nTips:Flag is under /flag/"
    )
    teams_data = json.load(open("/app/teams.json", "r"))
    print("[*] Pls choose options:\n\t[V]iew leaderboard\n\t[R]un chal")
    choice = input("Your choice: ").lower().strip()
    if choice == "v":
        time.sleep(1)
        with FileLock("/app/scores.json.lock", timeout=1):
            leaderb = json.load(open("/app/scores.json", "r"))
        print("------------LEADERBOARD------------")
        temp = sorted(leaderb.values())
        for t, s in sorted(leaderb.items(), key=lambda x: x[1]):
            print("{0:2} | {1:15} | {2}".format(temp.index(s) + 1, teams_data[t], s))
        print("-----------------------------------")
        exit(0)
    elif choice == "r":
        challenge = gen_random_string()
        team_token = input("[*] Please input your team token: ")
        if team_token not in teams_data:
            print("No such team!")
            exit(1)
        team_name = teams_data[team_token]
        payload = input("Give me your payload >> ")
        team_index = get_team_name_index(teams_data, team_token)
        if valid_payload(team_index, payload):
            score = calc_payload_score(payload)
            with FileLock("/app/scores.json.lock", timeout=1):
                leaderb = json.load(open("/app/scores.json", "r"))
                if team_token not in leaderb or score < leaderb[team_token]:
                    leaderb[team_token] = score
                    json.dump(leaderb, open("/app/scores.json", "w"))
                    data = {"data": [], "challenge": "shortpy"}
                    temp = sorted(leaderb.values())
                    for t in leaderb:
                        data['data'].append({"teamtoken":t, "rank":temp.index(leaderb[t])+1})
                    data=check_data_and_add_timestamp(data)
                    json.dump(data, open("/app/rank.json", "w"))
                print("------------LEADERBOARD------------")
                temp = sorted(leaderb.values())
                for t, s in sorted(leaderb.items(), key=lambda x: x[1]):
                    print("{0:2} | {1:15} | {2}".format(temp.index(s) + 1, teams_data[t], s))
                print("-----------------------------------")
                exit(0)

        else:
            print("Your payload is unsuccessful")

    else:
        print("You should select valid choice!")

    exit(0)

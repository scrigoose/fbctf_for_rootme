import requests
import re
import config


class UserScores:
    def __init__(self, username):
        self.username = username
        self.points = 0
        self.resolved = dict()
    def __repr__(self):
        return '{}::{}::{}'.format(self.username, self.points, self.resolved)


def retrieve_stats(user):
    print("Collecting statistics for user {}".format(user))
    r = requests.get(config.params['url_stats'].format(user), cookies=config.params['cookies_rootme'], proxies=config.params['proxies'])
    ret = dict()
    if r.status_code == 200:
        raw = re.findall('evolution_data_total.push.*Array\((.*)\)\)', r.text)
        for entry in raw:
            tokens = re.findall('"(.*?)"', entry)
            resolved_date = tokens[0]
            resolved_challenge = tokens[2]
            ret[resolved_challenge] = resolved_date
    else:
        print("Cannot check user {} statistics".format(user))
    return ret


def retrieve_points(users):
    print("Getting scores from root-me")
    scores = []
    for user in users:
        r = requests.get(config.params['url_rootme'].format(user), cookies=config.params['cookies_rootme'], proxies=config.params['proxies'])
        if r.status_code == 200:
            score = re.search('Score.*<span>(\d*)</span>*', r.text)
            if score and score.group(1):
                us = UserScores(user)
                print('{0: <15}'.format(user), score.group(1))
                us.points = score.group(1)
                us.resolved = retrieve_stats(user)
                scores.append(us)

            else:
                print("Cannot check points for {}".format(user))
        else:
            print("User {} not found".format(user))
    return scores

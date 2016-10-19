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


def search(content):
    print("Searching for {}".format(content))
    r = requests.get(config.params['url_search'].format(content))
    if r.status_code == 200:
        regexp = re.compile('(auteurs.*|No results for.*)<b>"{}".*?</div'.format(content), re.MULTILINE|re.DOTALL)
        raw = regexp.search(r.text)
        profile = re.findall('Profil of.*href="/(.*)\?', raw.group(0))
        if len(profile) == 0:
            print("  No results found for {}".format(content))
        elif len(profile) == 1:
            print("  Found profile: {}".format(profile[0]))
            return profile[0]
        else:
            print("  Too many results found: ", profile)

    else:
        print("Search query failed")
    return None


def get_stats(user):
    r = requests.get(config.params['url_stats'].format(user))
    ret = dict()
    if r.status_code == 200:
        raw = re.findall('evolution_data_total.push.*Array\((.*)\)\)', r.text)
        for entry in raw:
            tokens = re.findall('"(.*?)"', entry)
            resolved_date = tokens[0]
            resolved_challenge = tokens[2]
            ret[resolved_challenge] = resolved_date
    else:
        print("  Cannot check user {} statistics".format(user))
    return ret


def get_points(user):
    r = requests.get(config.params['url_rootme'].format(user))
    if r.status_code == 200:
        score = re.search('Score.*<span>(\d*)</span>*', r.text)
        if score and score.group(1):
            us = UserScores(user)
            print('{0: <15}'.format(user), score.group(1))
            us.points = score.group(1)
            us.resolved = get_stats(user)
            return us
        else:
            print("Cannot check points for {}".format(user))
    else:
        print("User {} not found".format(user))
        found = search(user)
        if found:
            points = get_points(found)
            points.username = user # replace found profile username with fbctf db team name
            return points
    return None


def retrieve_scores(users):
    print("Getting scores from root-me")
    scores = []
    for user in users:
        score = get_points(user)
        if score:
            scores.append(score)
    return scores

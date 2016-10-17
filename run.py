#! /usr/bin/python3
import time
import rootme_connector as rootme
import fbctf_connector_mysql as fb


if __name__ == '__main__':
    fb.create_categories_db()
    fb.create_flags()
    while(True):
        users = fb.get_users_from_db()
        scores = rootme.retrieve_points(users)
        fb.update_scores_in_db(scores)
        time.sleep(15)

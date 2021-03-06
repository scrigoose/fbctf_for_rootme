#! /usr/bin/python3
import time
import config
import rootme_connector as rootme
import fbctf_connector_mysql as fb


if __name__ == '__main__':
    sleep_time = 10
    fb.create_categories_db()
    fb.create_flags()
    while(True):
        users = fb.get_users_from_db()
        scores = rootme.retrieve_scores(users)
        fb.update_scores_in_db(scores)
        print("All done... going to sleep, c'ya for {} seconds".format(sleep_time))
        time.sleep(sleep_time)

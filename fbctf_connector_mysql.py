import mysql.connector
import time
import challenges
import config
from random import shuffle


def get_users_from_db():
    print("Retriving users from db")
    cnx = mysql.connector.connect(user=config.params['db_user'], password=config.params['db_pass'], database=config.params['database'])
    cursor = cnx.cursor()
    query = "SELECT name FROM teams;"
    cursor.execute(query)
    q_res = cursor.fetchall()
    users = [u[0] for u in q_res]
    cursor.close()
    cnx.close()
    return users


def get_user_id(username):
    cnx = mysql.connector.connect(user=config.params['db_user'], password=config.params['db_pass'], database=config.params['database'])
    cursor = cnx.cursor()
    query = "SELECT id FROM teams WHERE name='{}'".format(username)
    cursor.execute(query)
    uid = cursor.fetchall()
    cursor.close()
    cnx.close()
    return uid[0][0] if uid else None


def get_level_id(level):
    cnx = mysql.connector.connect(user=config.params['db_user'], password=config.params['db_pass'], database=config.params['database'])
    cursor = cnx.cursor()
    query = "SELECT id FROM levels WHERE title='{}'".format(level)
    cursor.execute(query)
    uid = cursor.fetchall()
    cursor.close()
    cnx.close()
    return uid[0][0] if uid else None


def get_level_points(level):
    cnx = mysql.connector.connect(user=config.params['db_user'], password=config.params['db_pass'], database=config.params['database'])
    cursor = cnx.cursor()
    query = "SELECT points FROM levels WHERE title='{}'".format(level)
    cursor.execute(query)
    uid = cursor.fetchall()
    cursor.close()
    cnx.close()
    return uid[0][0] if uid else None


def is_resolve_logged(level, uid):
    cnx = mysql.connector.connect(user=config.params['db_user'], password=config.params['db_pass'], database=config.params['database'])
    cursor = cnx.cursor()
    query = "SELECT * FROM scores_log WHERE team_id='{}' AND level_id='{}'".format(uid, level)
    cursor.execute(query)
    match = cursor.fetchall()
    cursor.close()
    cnx.close()
    return True if match else False


def update_scores_in_db(scores):
    print("Updating db")
    cnx = mysql.connector.connect(user=config.params['db_user'], password=config.params['db_pass'], database=config.params['database'])
    cursor = cnx.cursor()
    for score in scores:
        query = "UPDATE teams SET points={} WHERE name='{}';".format(score.points, score.username)
        res = cursor.execute(query)
        cnx.commit()
        user_id = get_user_id(score.username)
        if user_id:
            for resolved_challenge, resolved_date in score.resolved.items():
                tokens = resolved_challenge.split("/")
                level = tokens[3]
                level_id = get_level_id(level)
                points = get_level_points(level)
                if level_id and points and not is_resolve_logged(level_id, user_id):
                    query = ("INSERT INTO scores_log (ts, team_id, points, level_id, type)"
                        " VALUES (%s, %s, %s, %s, 'flag');")
                    data = (resolved_date, user_id, points, level_id)
                    cursor.execute(query, data)
                    cnx.commit()
    cursor.close()
    cnx.close()


def get_category_id(cat):
    print('Getting category id for {}'.format(cat))
    cnx = mysql.connector.connect(user=config.params['db_user'], password=config.params['db_pass'], database=config.params['database'])
    cursor = cnx.cursor()
    query = "SELECT id FROM categories WHERE category = '{}';".format(cat)
    cursor.execute(query)
    q_res = cursor.fetchall()
    cursor.close()
    cnx.close()
    return q_res[0][0] if q_res else None


def create_categories_db():
    for cat in challenges.categories:
        if not get_category_id(cat):
            print("Creating category {}".format(cat))
            cnx = mysql.connector.connect(user=config.params['db_user'], password=config.params['db_pass'], database=config.params['database'])
            cursor = cnx.cursor()
            query = ("INSERT INTO categories (category, protected, created_ts)"
                " VALUES (%s, 0, %s);")
            data = (cat, time.strftime('%Y-%m-%d %H:%M:%S'))
            cursor.execute(query, data)
            cnx.commit()
            cursor.close()
            cnx.close()
        else:
            print("Category {} already exists".format(cat))


def create_flag_db(title, descr, country, cat, points):
    if not get_level_id(title):
        print('Creating level: {}'.format(title))
        cnx = mysql.connector.connect(user=config.params['db_user'], password=config.params['db_pass'], database=config.params['database'])
        cursor = cnx.cursor()
        query = ("INSERT INTO levels (active, type, title, description, entity_id, category_id, points, bonus, bonus_dec, bonus_fix, flag, hint, penalty, created_ts)"
            " VALUES (1, 'flag', %s, %s, %s, %s, %s, 0, 0, 0, %s, '', 0, %s);")
        data = (title, descr, country, cat, points, config.params['flag_key'], time.strftime('%Y-%m-%d %H:%M:%S'))
        cursor.execute(query, data)
        cnx.commit()
        cursor.close()
        cnx.close()
    else:
        print("Level {} already exists".format(title))


def create_flags():
    cat_ids = dict()
    countries = list(range(1, 177))
    shuffle(countries)
    for challenge, points in challenges.all.items():
        if points < 50:
            tokens = challenge.split('/')
            cat = tokens[2]
            if cat not in cat_ids:
                cat_ids[cat] = get_category_id(cat)
            # create_flag_rest(tokens[3], 'https://www.root-me.org/' + challenge, cat_ids[cat], points)
            create_flag_db(tokens[3], 'https://www.root-me.org/' + challenge, countries.pop(), cat_ids[cat], points)


import requests
import re
import config


def login_fbctf():
    path = 'page=login'
    r = requests.get(config.params['url_fbctf'].format(path), verify=False)
    config.params['cookies_fbctf']['FBCTF'] = r.headers['set-cookie'].split(';')[0].split('=')[1]
    data = {
        'action':'login_team',
        'password':config.params['admin_pass'],
        'teamname':config.params['admin_user']
    }
    path = 'p=index&ajax=true'
    r = requests.post(config.params['url_fbctf'].format(path), cookies=config.params['cookies_fbctf'], verify=False, data=data)
    config.params['cookies_fbctf']['FBCTF'] = r.headers['set-cookie'].split(';')[0].split('=')[1]
    cnx = mysql.connector.connect(user=config.params['db_user'], password=config.params['db_pass'], database=config.params['database'])
    cursor = cnx.cursor()
    query = "SELECT data FROM sessions WHERE cookie = '{}';".format(config.params['cookies_fbctf']['FBCTF'])
    cursor.execute(query)
    q_res = cursor.fetchall()
    csrf = re.search('"(.*)"', q_res[0][0].split(';')[2])
    config.params['csrf_token'] = csrf.group(1)


def create_categories():
    path = 'p=admin&ajax=true'
    for cat in challenges.categories:
        data = {'action':'create_category', 'category':cat, 'csrf_token':config.params['csrf_token']}
        r = requests.post(config.params['url_fbctf'].format(path), cookies=config.params['cookies_fbctf'], verify=False, data=data)
        print('Category {0} :: result {1} :: {2}'.format(cat, r.status_code, r.text))


def create_flag_rest(title, descr, cat, points):
    print('Creating flag: {}'.format(title))
    path = 'p=admin&ajax=true'
    data = {
        'action':'create_flag',
        'title':title,
        'description':descr,
        'flag':config.params['flag_key'],
        'entity_id':'0',
        'category_id':cat,
        'points':points,
        'hint':'',
        'penalty':'',
        'csrf_token':config.params['csrf_token']
    }
    r = requests.post(config.params['url_fbctf'].format(path), cookies=config.params['cookies_fbctf'], verify=False, data=data)
    print(r.status_code, r.text)

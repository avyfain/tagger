import os
import ast
import pocket
# from flask import Flask, render_template

# app = Flask(__name__)

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
TOKEN_PAIRS = os.environ.get('TOKENS')

# @app.route('/tag')
# def tag():
#     names = tag_it_all()
#     return "We've tagged your stuff: " + ', '.join(names)

# @app.route('/')
# def hello():
#     return 'Hello World! This is our pocket tagger'

# @app.route('/read')
# def read():
#     for pocketier in pocketiers:
#         names.append(pocketier['name'])
#     return render_template('read.html', name=name)

def tag_it_all():
    pocketiers = ast.literal_eval(TOKEN_PAIRS)
    names = []
    for pocketier in pocketiers:
        names.append(pocketier['name'])
        try:
            tag_user_articles(CONSUMER_KEY, pocketier['token'])
        except (pocket.InvalidQueryException, pocket.AuthException):
            print(pocketier['token'], 'failed. Retrying...')
    return names

def tag_art(art, pocket_client):
    try:
        w = int(art['word_count'])
        if w < 100: tag = "whoops"
        elif w < 500: tag = "quick"
        elif w < 1000: tag = "short"
        elif w < 1500: tag = "mid"
        elif w < 2000: tag = "mid-long"
        else: tag = "long"
        pocket_client = pocket_client.tags_add(int(art['item_id']), tag)
    except KeyError:
        print('Missing')
    return pocket_client

def tag_user_articles(consumer_key, token, qty=1000):
    client = pocket.Pocket(consumer_key, token)

    r = client.get(state='all',count = qty)
    art_list = r[0]['list']

    count = 0
    visited = set()

    for art_id, art in art_list.items():
        count += 1
        if count % 50 == 0:
            print('committed chunk')
            client.commit()

        #sometimes things are added twice to pocket
        try:
            if art['resolved_title'] in visited or art['resolved_url'] in visited:
                continue
            visited.add(art['resolved_title'])
            visited.add(art['resolved_url'])
        except:
            print('Fail')
        client.tags_clear(art_id)
        tag_art(art, client)

    client.commit()

# def get_union():
#     pocketiers = ast.literal_eval(TOKEN_PAIRS)
#     for pocketier in pocketiers:
#         client = pocket.Pocket(CONSUMER_KEY, pocketier['token'])
#         data, headers = client.get(count=1000)
#         try: 
#             union = union & set(data['list'].keys())
#         except:
#             union = set(data['list'].keys())

#     union_strings = []
#     for item in union:
#         union_strings.append(data['list'][item]['resolved_title'] +' '+ data['list'][item]['resolved_url'])
#     return union_strings

if __name__ == '__main__':
    tag_it_all()    

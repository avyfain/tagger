import os
import ast
import pocket
from flask import Flask
from apscheduler.schedulers.blocking import BlockingScheduler

app = Flask(__name__)

CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
TOKEN_PAIRS = os.environ.get('TOKENS')
sched = BlockingScheduler()

sched.start()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=23)
@app.route('/tag')
def tag():
	pocketiers = ast.literal_eval(TOKEN_PAIRS)
	names = []
	for pocketier in pocketiers:
		names.append(pocketier['name'])
		tag_user_articles(CONSUMER_KEY, pocketier['key'])
	return "We've tagged your stuff: " + ', '.join(names)

@app.route('/')
def hello():
    return 'Hello World! This is our pocket tagger'


def tag_art(art, pocket_instance):
	try:
		w = int(art['word_count'])
		if w < 100: tag = "whoops"
		elif w < 500: tag = "quick"
		elif w < 1000: tag = "short"
		elif w < 1500: tag = "mid"
		elif w < 2000: tag = "mid-long"
		else: tag = "long"
		pocket_instance = pocket_instance.tags_add(int(art['item_id']), tag)
	except:
		print 'Missing'
	return pocket_instance

def tag_user_articles(consumer_key, token, qty=100):
	client = pocket.Pocket(consumer_key, token)

	r = client.get(state='all',count = qty)
	art_list = r[0]['list']

	count = 0
	visited = {}

	for art_id, art in art_list.iteritems():
		count += 1
		if count % 50 == 0:
			print 'committed chunk'
			client.commit()

		#sometimes things are added twice to pocket
		try:
			if art['resolved_title'] in visited or art['resolved_url'] in visited:
				continue
			visited[art['resolved_title']] = True
			visited[art['resolved_url']] = True
		except:
			print 'Fail'
		client.tags_clear(art_id)
		tag_art(art, client)

	client.commit()
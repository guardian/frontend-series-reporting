import sys, json, boto3
from queries import series_published_sql, top_10_engagement_sql, top_10_loyalty_sql, x_n_sql, top_10_visits_sql 

s3 = boto3.resource('s3')
bucket = s3.Bucket('ahughes')

#obj = s3.Object(bucket_name='ahughes', key='top_10_series_url.json')

# Makes sql dates suitable for json
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def groupby(data, key, mapfn=lambda x: x):
    ret = {}
    for item in data:
        if item[key] not in ret:
            ret[item[key]] = []
        ret[item[key]].append(mapfn(item))
    return ret

def build_series(data, series_key):
	return {'name': series_key, 'data': [entry[series_key] for entry in data]}

def build_data(data, category_key, series_keys):
	categories = [entry[category_key] for entry in data]
	series = [build_series(data, series_key) for series_key in series_keys]
	return {'categories': categories, 'series': series}

def build_sections(data, category_key, series_keys):
	sections = {}
	for section_name, section_data in groupby(data, 'section').iteritems():
		sections[section_name] = build_data(section_data, category_key, series_keys)
	return sections

def get_series(url):
	before_match, after_match = url.split('/series/')
	return after_match

def main():

	# visits_data = top_10_visits_sql()
	publishing_data = series_published_sql()
	engagement_data = top_10_engagement_sql()
	loyalty_data = top_10_loyalty_sql()

	# visits_sections = build_sections(visits_data, 'series_url', ['visits'])
	publishing_sections = build_sections(publishing_data, 'publication_date', ['series_published_to', 'episodes_published'])
	engagement_sections = build_sections(engagement_data, 'series_url', ['multi_episode_visit_visitors', 'single_episode_visit_visitors'])
	loyalty_sections = build_sections(loyalty_data, 'series_url', ['multi_session_visit_visitors', 'single_session_visit_visitors'])

	x_n_data = x_n_sql()
	x_n_data_sorted = sorted(x_n_data, key=lambda x: x['n'])

	x_n_sections = {}
	for section_name, section_data in groupby(x_n_data_sorted, 'section').iteritems():
		section_categories = range(1, max(entry['n'] for entry in section_data) + 1)
 
		section_visitors = groupby(section_data, 'series_url', lambda x: x['visitors'])
		section_series = [{'name': url, 'data': visitors} for url, visitors in section_visitors.iteritems()]

		x_n_sections[section_name] = {'categories': section_categories, 'series': section_series}

	# processed_data = {'visits': visits_sections, 'publishing': publishing_sections, 'engagement': engagement_sections, 'loyalty': loyalty_sections, 'x_n': x_n_sections}
	processed_data = {'publishing': publishing_sections, 'engagement': engagement_sections, 'loyalty': loyalty_sections, 'x_n': x_n_sections}

	print json.dumps(processed_data, default=date_handler)

	# print json.dumps(series, default=date_handler), json.dumps(categories, default=date_handler)
	# Upload to s3
	# data = json.dumps(records, default=date_handler)
	# bucket.put_object(Key='top_10_series_url.json', Body=data)
 
if __name__ == '__main__':
	main()


	# Top 10 episode titles with publication dates
	# cursor.execute("SELECT ts.series_url, episode_url, sc.web_publication_date FROM series_content_30_day sc INNER JOIN top_10_series ts ON sc.series_url = ts.series_url ORDER BY series_url, web_publication_date;")
	# episode_url_records = cursor.fetchall()
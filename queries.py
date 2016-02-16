import psycopg2
import psycopg2.extras #extras library
from string import Template
import credentials

sql_file = open('series_dash_tables.sql', 'r').read()

conn_string = credentials.getRedshiftCredentials()
print 'Connecting to database\n	->%s' % (conn_string)
conn = psycopg2.connect(conn_string)
cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

print 'Connected'

# # Execute sql to create tables
cursor.execute(sql_file)

# define functions to execute sql queries 
# Series and episodes published last 30 days
def series_published_sql():
	cursor.execute("""
	SELECT publication_date,
	section,
	COUNT(series_url) AS series_published_to,
	SUM(episodes_published_per_series) AS episodes_published
	FROM
	(SELECT
	publication_date,
	series_url,
	section,
	COUNT(episode_url) AS episodes_published_per_series
	FROM series_content_30_day
	GROUP BY publication_date, series_url, section
	)
	GROUP BY publication_date, section
	ORDER BY publication_date;
	""")
	return cursor.fetchall()

# # Top 10 series for visitors
# def top_10_visits_sql():
# 	cursor.execute("""
# 	SELECT tv.* FROM
# 	(
# 		SELECT 
# 		section,
# 		series_url,
# 		SUM(session_visit_number) AS visits,
# 		RANK () OVER (PARTITION BY section ORDER BY visits DESC) AS rank
# 		FROM series_visitors_by_session_visit_number
# 		GROUP BY section, series_url
# 	) tv
# 	WHERE Rank <= 10
# 	ORDER BY section, rank
# 	""")
# 	return cursor.fetchall()

# Top 10 series for multi episode visit visitors
def top_10_engagement_sql():
	cursor.execute("""
	SELECT te.* FROM 
	(
		SELECT section,
		series_url,
		COUNT(CASE WHEN episode_visit_number>1 THEN 1 END) AS multi_episode_visit_visitors,
		COUNT(CASE WHEN episode_visit_number=1 THEN 1 END) AS single_episode_visit_visitors,
		Rank () OVER (PARTITION BY section ORDER BY multi_episode_visit_visitors DESC) AS rank
		FROM series_visitors_by_episode_visit_number
		GROUP BY section, series_url
	) te
	WHERE Rank <= 10
	ORDER BY section, rank
	""")
	return cursor.fetchall()

# # Top 10 series for multi session visit visitors
def top_10_loyalty_sql():
	cursor.execute("""
	SELECT tl.* FROM 
	(
		SELECT section,
		series_url,
		COUNT(CASE WHEN session_visit_number>1 THEN 1 END) AS multi_session_visit_visitors,
		COUNT(CASE WHEN session_visit_number=1 THEN 1 END) AS single_session_visit_visitors,
		Rank () OVER (PARTITION BY section ORDER BY multi_session_visit_visitors DESC) AS rank
		FROM series_visitors_by_session_visit_number
		GROUP BY section, series_url
	) tl
	WHERE Rank <= 10
	ORDER BY section, rank
	""")
	return cursor.fetchall()



def x_n_sql():
	# top 10 urls and episode counts
	cursor.execute("""
	SELECT se.section,
	se.series_url, 
	COUNT(episode_url) as episodes 
	FROM series_content_30_day sc 
	INNER JOIN
	(
	SELECT te.* FROM 
	(
		SELECT section,
		series_url,
		COUNT(CASE WHEN episode_visit_number>1 THEN 1 END) AS multi_episode_visit_visitors,
		COUNT(CASE WHEN episode_visit_number=1 THEN 1 END) AS single_episode_visit_visitors,
		Rank () OVER (PARTITION BY section ORDER BY multi_episode_visit_visitors DESC) AS rank
		FROM series_visitors_by_episode_visit_number
		GROUP BY section, series_url
	) te
	WHERE Rank <= 10
	ORDER BY section, rank
	) se
	ON sc.series_url = se.series_url
	GROUP BY se.section, se.series_url;""")
	episode_counts_records = cursor.fetchall()
	# top 10 x of n visitors
	for record in episode_counts_records:
		section = record['section']
		episodes = record['episodes']
		series_url = record['series_url']
		tmpl = Template("""
			INSERT INTO x_n_visitors SELECT \'$section\', \'$url\', $numi, COUNT(CASE WHEN episode_visit_number = $numi THEN $numi END) 
			FROM series_visitors_by_episode_visit_number 
			WHERE series_url = \'$url\' 
			GROUP BY series_url;""")
		i=0
		for i in range(1,episodes):
			x_script = tmpl.substitute(numi=str(i), url=series_url, section=section.replace('\'', '\\\''))
			cursor.execute(x_script)
			i+=1		
	cursor.execute("SELECT * FROM x_n_visitors;")
	return cursor.fetchall()

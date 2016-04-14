from string import Template
#import credentials
from pyhive import presto

# conn_string = credentials.getRedshiftCredentials()
print 'Connecting to database\n	->%s' % ('"presto.ophan.co.uk", port=8889, catalog="hive", schema="temp_ah"')
conn = presto.connect("presto.ophan.co.uk", port=8889, catalog="hive", schema="temp_ah")
print 'Connected'

def presto_query(conn, query):
    cur = conn.cursor()
    cur.execute(query)
    cols = [column[0] for column in cur.description]
    fetch = cur.fetchall()
    results = []
    for row in fetch:
        results.append(dict(zip(cols, row)))
    return results

# define functions to execute sql queries 
# Series and episodes published last 30 days
def series_published_sql():
	return presto_query(conn, """
	SELECT publication_date,
	       section,
	       COUNT(series_url) AS series_published_to,
	       SUM(episodes_published_per_series) AS episodes_published
	FROM (SELECT publication_date,
	             series_url,
	             section,
	             COUNT(episode_url) AS episodes_published_per_series
	      FROM temp_ah.series_content_30_day
	      GROUP BY publication_date,
	               series_url,
	               section)
	GROUP BY publication_date,
	         section
	ORDER BY publication_date
	""")

# Top 10 series for pageviews
# To replace ""
def top_10_pageviews_sql():
	return presto_query(conn, """
	SELECT series_url,
	       section,
	       browser_id,
	       SUM(pageviews) AS pageviews
	FROM (SELECT series_url,
	             section,
	             browser_id,
	             COUNT(*) AS pageviews
	      FROM temp_ah.series_content_30_day sc
	        INNER JOIN temp_ah.series_visitors_30_day sv ON sc.episode_url = sv.episode_url
	      --WHERE ds_session_key IS NOT NULL
	      --SEE WHERE NULLS COME FROM. ~1% OF RECORDS...
	      GROUP BY browser_id,
	               series_url,
	               section,
	               ds_session_key)
	GROUP BY 1,
	         2,
	         3
	""")

# Top 10 series for multi episode visit visitors
def top_10_engagement_sql():
	return presto_query(conn, """
	SELECT te.* FROM 
	(
		SELECT section,
		series_url,
		COUNT(CASE WHEN episode_visit_number>1 THEN 1 END) AS multi_episode_visit_visitors,
		COUNT(CASE WHEN episode_visit_number=1 THEN 1 END) AS single_episode_visit_visitors,
		Rank () OVER (PARTITION BY section ORDER BY COUNT(CASE WHEN episode_visit_number>1 THEN 1 END) DESC) AS rank
		FROM temp_ah.series_visitors_by_episode_visit_number
		GROUP BY section, series_url
	) te
	WHERE Rank <= 10
	ORDER BY section, rank
	""")

# # Top 10 series for multi day visit visitors
def top_10_loyalty_sql():
	return presto_query(conn, """
	SELECT tl.* FROM 
	(
		SELECT section,
		series_url,
		COUNT(CASE WHEN days_visiting>1 THEN 1 END) AS multi_day_visit_visitors,
		COUNT(CASE WHEN days_visiting=1 THEN 1 END) AS single_day_visit_visitors,
		Rank () OVER (PARTITION BY section ORDER BY COUNT(CASE WHEN days_visiting>1 THEN 1 END) DESC) AS rank
		FROM temp_ah.series_visitors_by_days_visited
		GROUP BY section, series_url
	) tl
	WHERE Rank <= 10
	ORDER BY section, rank
	""")

def x_n_sql():
	# top 10 urls and episode counts
	return presto_query(conn, """ with top_10_urls_and_episode_counts as (SELECT se.section,
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
		Rank () OVER (PARTITION BY section ORDER BY COUNT(CASE WHEN episode_visit_number>1 THEN 1 END) DESC) AS rank
		FROM temp_ah.series_visitors_by_episode_visit_number
		GROUP BY section, series_url
	) te
	WHERE Rank <= 10
	ORDER BY section, rank
	) se
	ON sc.series_url = se.series_url
	GROUP BY se.section, se.series_url)

	SELECT e.section,
	       e.series_url,
	       map_num,
	       count(browser_id) AS visitors
	FROM top_10_urls_and_episode_counts e
	  JOIN temp_ah.number_wang nm ON e.episodes = nm.group_num
	  JOIN temp_ah.series_visitors_by_episode_visit_number sv
	    ON map_num = sv.episode_visit_number
	   AND e.section = sv.section
	   AND e.series_url = sv.series_url
	GROUP BY 1,
	         2,
	         3
	         """)

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

# def x_n_sql():
# 	# top 10 urls and episode counts
# 	cursor.execute("""
# 	SELECT se.section,
# 	se.series_url, 
# 	COUNT(episode_url) as episodes 
# 	FROM series_content_30_day sc 
# 	INNER JOIN
# 	(
# 	SELECT te.* FROM 
# 	(
# 		SELECT section,
# 		series_url,
# 		COUNT(CASE WHEN episode_visit_number>1 THEN 1 END) AS multi_episode_visit_visitors,
# 		COUNT(CASE WHEN episode_visit_number=1 THEN 1 END) AS single_episode_visit_visitors,
# 		Rank () OVER (PARTITION BY section ORDER BY multi_episode_visit_visitors DESC) AS rank
# 		FROM series_visitors_by_episode_visit_number
# 		GROUP BY section, series_url
# 	) te
# 	WHERE Rank <= 10
# 	ORDER BY section, rank
# 	) se
# 	ON sc.series_url = se.series_url
# 	GROUP BY se.section, se.series_url;""")
# 	episode_counts_records = cursor.fetchall()
# 	# top 10 x of n visitors
# 	for record in episode_counts_records:
# 		section = record['section']
# 		episodes = record['episodes']
# 		series_url = record['series_url']
# 		tmpl = Template("""
# 			INSERT INTO x_n_visitors SELECT \'$section\', \'$url\', $numi, COUNT(CASE WHEN episode_visit_number = $numi THEN $numi END) 
# 			FROM series_visitors_by_episode_visit_number 
# 			WHERE series_url = \'$url\' 
# 			GROUP BY series_url;""")
# 		i=0
# 		for i in range(1,episodes):
# 			x_script = tmpl.substitute(numi=str(i), url=series_url, section=section.replace('\'', '\\\''))
# 			cursor.execute(x_script)
# 			i+=1		
# 	cursor.execute("SELECT * FROM x_n_visitors;")
# 	return cursor.fetchall()

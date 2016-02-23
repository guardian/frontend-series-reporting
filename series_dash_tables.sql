SET query_group TO long_running;

--last 30 days series content
DROP TABLE IF EXISTS series_content_30_day;
CREATE TEMPORARY TABLE series_content_30_day AS
(
	SELECT tag_web_url AS series_url,
	web_url AS episode_url,
	section_name AS section,
	web_publication_date::DATE AS publication_date 	
	FROM content_dim cd INNER JOIN content_tag_lookup ctl
	ON cd.content_key = ctl.content_key
	WHERE ctl.tag_type = 'series' 
	AND web_publication_date::DATE <= GETDATE()::DATE
	AND web_publication_date::DATE >= (GETDATE()::DATE - 30)
	--BETWEEN (GETDATE()::DATE) AND (GETDATE()::DATE - 30) --30 days before query run
	GROUP BY tag_web_url, web_url, section_name, web_publication_date
);

--last 30 days series visitors
DROP TABLE IF EXISTS series_visitors_30_day;
CREATE TEMPORARY TABLE series_visitors_30_day AS
(
	SELECT sc.episode_url, 
	ophan_visitor_id,
--	pvf.ds_session_key,
	pvf.page_view_timestamp::DATE as visit_date,
	COUNT(*) AS pageviews
	FROM series_content_30_day sc INNER JOIN content_dim cd 
		ON sc.episode_url = cd.web_url INNER JOIN page_view_fact pvf 
		ON cd.content_key = pvf.content_key
	WHERE pvf.page_view_timestamp::DATE <= GETDATE()::DATE
	AND pvf.page_view_timestamp::DATE >= (GETDATE()::DATE - 30)
	GROUP BY 1,2,3
);

-- --last 30 days series visitors
-- DROP TABLE IF EXISTS series_visitors_30_day;
-- CREATE TEMPORARY TABLE series_visitors_30_day AS
-- (
-- 	SELECT sc.episode_url, 
-- 	ophan_visitor_id,
-- --	pvf.ds_session_key,
-- 	COUNT(*) AS visits
-- 	FROM series_content_30_day sc INNER JOIN content_dim cd 
-- 		ON sc.episode_url = cd.web_url INNER JOIN page_view_fact pvf 
-- 		ON cd.content_key = pvf.content_key
-- 	WHERE pvf.page_view_timestamp::DATE <= GETDATE()::DATE
-- 	AND pvf.page_view_timestamp::DATE >= (GETDATE()::DATE - 30)
-- 	GROUP BY 1,2,3
-- );

--SERIES VISITORS BY NUMBER OF EPISODES VISITED
DROP TABLE IF EXISTS series_visitors_by_episode_visit_number;
CREATE TEMPORARY TABLE series_visitors_by_episode_visit_number AS
(
	SELECT series_url,
	section, 
	ophan_visitor_id,
	COUNT(sc.episode_url) AS episode_visit_number
	FROM series_content_30_day sc INNER JOIN series_visitors_30_day sv 
		ON sc.episode_url = sv.episode_url
	GROUP BY series_url, section, ophan_visitor_id
);

-- -- SERIES VISITORS BY NUMBER OF SESSIONS VISITED
-- DROP TABLE IF EXISTS series_visitors_by_session_visit_number;
-- CREATE TEMPORARY TABLE series_visitors_by_session_visit_number AS
-- (
-- 	SELECT series_url,
-- 	section, 
-- 	ophan_visitor_id,
-- 	COUNT(ds_session_key) AS session_visit_number
-- 	FROM 
-- 	(
-- 		SELECT series_url,
-- 		section,
-- 		ophan_visitor_id,
-- 		ds_session_key,
-- 		COUNT(*) AS episodes_in_session
-- 		FROM series_content_30_day sc INNER JOIN series_visitors_30_day sv 
-- 			ON sc.episode_url = sv.episode_url
-- 			WHERE ds_session_key IS NOT NULL  --SEE WHERE NULLS COME FROM. ~1% OF RECORDS...
-- 		GROUP BY ophan_visitor_id, series_url, section, ds_session_key
-- 	)
-- 	GROUP BY 1,2,3
-- );

-- SERIES VISITORS BY DAYS VISITED
-- TO REPLACE SERIES VISITORS BY NUMBER OF SESSIONS VISITED
DROP TABLE IF EXISTS series_visitors_by_days_visited;
CREATE TEMPORARY TABLE series_visitors_by_days_visited AS
(
	SELECT series_url, 
	section, 
	ophan_visitor_id, 
	COUNT(visit_date) AS days_visiting
	FROM
	(
		SELECT 
		series_url,
		section,
		ophan_visitor_id,
		visit_date
		FROM series_content_30_day sc INNER JOIN series_visitors_30_day sv 
			ON sc.episode_url = sv.episode_url 
		GROUP BY 1,2,3,4
	)
	GROUP BY 1,2,3
);	

DROP TABLE IF EXISTS x_n_visitors;
CREATE TEMPORARY TABLE x_n_visitors
(
section VARCHAR(220), series_url VARCHAR(220), n INT, visitors INT
);


-- -------- NOT READY TO UNCOMMENT --------


-- 	SELECT publication_date,
-- 	section,
-- 	COUNT(series_url) AS series_published_to,
-- 	SUM(episodes_published_per_series) AS episodes_published
-- 	FROM
-- 	(SELECT
-- 	publication_date,
-- 	series_url,
-- 	section,
-- 	COUNT(episode_url) AS episodes_published_per_series
-- 	FROM series_content_30_day
-- 	GROUP BY publication_date, series_url, section
-- 	)
-- 	GROUP BY publication_date
-- 	ORDER BY publication_date;


-- CREATE TEMPORARY TABLE series_by_visit_number_buckets AS
-- (
-- SELECT
-- series_url,
-- COUNT(CASE WHEN visit_number BETWEEN 1 AND 5 THEN 1 END) AS one_to_five,
-- COUNT(CASE WHEN visit_number BETWEEN 6 AND 10 THEN 1 END) AS six_to_ten,
-- COUNT(CASE WHEN visit_number BETWEEN 11 AND 15 THEN 1 END) AS eleven_to_fifteen,
-- COUNT(CASE WHEN visit_number BETWEEN 16 AND 20 THEN 1 END) AS sixteen_to_twenty,
-- COUNT(CASE WHEN visit_number BETWEEN 21 AND 25 THEN 1 END) AS twenty_one_to_twenty_five,
-- COUNT(CASE WHEN visit_number>25 THEN 1 END) AS more_than_tewnty_five
-- FROM series_visitors_by_episode_visit_number
-- GROUP BY series_url
-- );

-------- NOT READY TO UNCOMMENT --------

--need to query mercury for new fronts data
-- CREATE TABLE _ah.content_front AS
-- ( 
-- SELECT web_url, front_boolian AS front_boolean FROM _ah.url_title_count_front
-- );

-----------------------------------------


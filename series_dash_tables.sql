CREATE TABLE IF NOT EXISTS temp_ah.series_content_30_day (series_url STRING, episode_url STRING, section STRING, publication_date DATE);
CREATE TABLE IF NOT EXISTS temp_ah.series_visitors_30_day (episode_url STRING, browser_id STRING, visit_date DATE, pageviews DATE);
CREATE TABLE IF NOT EXISTS temp_ah.series_visitors_by_episode_visit_number (series_url STRING, section STRING, browser_id STRING, episode_visit_number INT);
CREATE TABLE IF NOT EXISTS temp_ah.series_visitors_by_days_visited (series_url STRING, section STRING, ophan_visitor_id STRING, days_visiting INT);

INSERT OVERWRITE TABLE temp_ah.series_content_30_day
SELECT series_tag series_url,
       content_path episode_url,
       section_name section,
       CAST(web_publication_date AS DATE) publication_date
FROM clean.content LATERAL VIEW explode (series_tags) t AS series_tag
WHERE series_tags IS NOT NULL
AND   web_publication_date <= to_date (from_unixtime (unix_timestamp ()))
AND   web_publication_date >= date_add (to_date (from_unixtime (unix_timestamp ())),-30)
GROUP BY series_tag,
         content_path,
         section_name,
         web_publication_date;

INSERT OVERWRITE TABLE temp_ah.series_visitors_30_day
SELECT p.url_path episode_url,
       browser_id,
       CAST(event_timestamp AS DATE) visit_date,
       COUNT(*) AS pageviews
FROM clean.pageviews p
WHERE event_timestamp <= to_date (from_unixtime (unix_timestamp ()))
AND   event_timestamp >= date_add (to_date (from_unixtime (unix_timestamp ())),-30)
AND   p.date <= to_date (from_unixtime (unix_timestamp ()))
AND   p.date >= date_add (to_date (from_unixtime (unix_timestamp ())),-30)
GROUP BY p.url_path,
         browser_id,
         CAST(event_timestamp AS DATE);

INSERT OVERWRITE TABLE temp_ah.series_visitors_by_episode_visit_number
SELECT series_url,
       section,
       browser_id,
       COUNT(sc.episode_url) AS episode_visit_number
FROM temp_ah.series_visitors_30_day sv
  INNER JOIN temp_ah.series_content_30_day sc ON sc.episode_url = sv.episode_url
GROUP BY series_url,
         section,
         browser_id;

INSERT OVERWRITE TABLE temp_ah.series_visitors_by_days_visited
SELECT series_url,
       section,
       browser_id,
       COUNT(visit_date) AS days_visiting
FROM (SELECT series_url,
             section,
             browser_id,
             visit_date
      FROM temp_ah.series_visitors_30_day AS sv
        INNER JOIN temp_ah.series_content_30_day AS sc ON sc.episode_url = sv.episode_url
      GROUP BY series_url,
               section,
               browser_id,
               visit_date) a
GROUP BY series_url,
         section,
         browser_id;

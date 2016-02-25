DELETE
FROM temp_ah.series_content_30_day;

INSERT INTO temp_ah.series_content_30_day
SELECT ctl.web_url series_url,
       path episode_path,
       cd.section_name section,
       CAST(web_publication_date AS DATE) publication_date,
       CAST(web_publication_date AS DATE) DATE
FROM clean.content cd
  INNER JOIN clean.tag_to_content tc ON cd.id = tc.content_id
  INNER JOIN clean.tag ctl ON tc.tag_id = ctl.id
WHERE ctl.tag_type = 'Series'
AND   web_publication_date <= CURRENT_DATE
AND   web_publication_date >= CURRENT_DATE-INTERVAL '30' DAY
GROUP BY ctl.web_url,
         path,
         cd.section_name,
         web_publication_date;

DELETE
FROM temp_ah.series_visitors_30_day;

INSERT INTO temp_ah.series_visitors_30_day
SELECT pvf.url_path episode_path,
       browser_id,
       CAST(event_timestamp AS DATE) visit_date,
       COUNT(*) AS pageviews,
       'test'
FROM clean.pageviews pvf
WHERE event_timestamp <= CURRENT_DATE
AND   event_timestamp >= CURRENT_DATE-interval '30' day
AND   pvf.date <= CURRENT_DATE
AND   pvf.date >= CURRENT_DATE-interval '30' day
GROUP BY 1,
         2,
         3;

DELETE
FROM temp_ah.series_visitors_by_episode_visit_number;

INSERT INTO temp_ah.series_visitors_by_episode_visit_number
SELECT series_url,
       section,
       browser_id,
       COUNT(sc.episode_path) AS episode_visit_number,
       'test'
FROM temp_ah.series_content_30_day sc
  INNER JOIN temp_ah.series_visitors_30_day sv ON sc.episode_path = sv.episode_path
GROUP BY series_url,
         section,
         browser_id;

DELETE
FROM temp_ah.series_visitors_by_days_visited;

INSERT INTO temp_ah.series_visitors_by_days_visited
SELECT series_url,
       section,
       browser_id,
       COUNT(visit_date) AS days_visiting,
       'test'
FROM (SELECT series_url,
             section,
             browser_id,
             visit_date
      FROM temp_ah.series_content_30_day AS sc
        INNER JOIN temp_ah.series_visitors_30_day AS sv ON sc.episode_path = sv.episode_path
      GROUP BY 1,
               2,
               3,
               4)
GROUP BY 1,
         2,
         3
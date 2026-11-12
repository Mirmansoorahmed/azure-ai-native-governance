-- Open issues by owner
SELECT owner, COUNT(*) AS open_issues FROM issues WHERE status != 'Closed' GROUP BY owner ORDER BY open_issues DESC;

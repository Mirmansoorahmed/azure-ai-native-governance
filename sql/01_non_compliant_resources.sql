-- Non-compliant Azure resources by kind and region
SELECT kind, region, status, COUNT(*) AS n FROM azure_resources GROUP BY kind, region, status ORDER BY n DESC;

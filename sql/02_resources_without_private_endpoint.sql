-- Resources without a private endpoint (network gap)
SELECT resource_id, name, kind FROM azure_resources WHERE status != 'compliant' ORDER BY kind;

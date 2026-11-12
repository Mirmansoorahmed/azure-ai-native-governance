-- Controls with no evidence row yet
SELECT c.code, c.title FROM controls c LEFT JOIN evidence e ON e.control_code = c.code WHERE e.id IS NULL;

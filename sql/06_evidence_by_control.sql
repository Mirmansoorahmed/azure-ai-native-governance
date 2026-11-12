-- Evidence rows per control, latest result first
SELECT control_code, result, COUNT(*) AS n FROM evidence GROUP BY control_code, result ORDER BY control_code;

SELECT 
    pid, 
    usename, 
    state, 
    now() - query_start AS duration,
    wait_event_type, 
    wait_event, 
    query
FROM pg_stat_activity 
WHERE state != 'idle' 
AND pid <> pg_backend_pid()
ORDER BY duration DESC;

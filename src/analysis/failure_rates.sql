\pset border 2
\pset footer 'off'

DROP FUNCTION failure_rates(_tbl text);
CREATE FUNCTION failure_rates(_tbl text)
    RETURNS TABLE (
        recursive text,
        dns_type text,
        total bigint,
        successful_pct numeric,
        pageload_timeout_pct numeric,
        dns_error_pct numeric,
        selenium_error_pct numeric,
        firefox_error_pct numeric,
        other_error_pct numeric
    )
    AS $f$
    BEGIN
        RETURN QUERY EXECUTE format('SELECT
            recursive,
            dns_type,
            total,
            round(100.0 * successful / total, 2) as successful_pct,
            round(100.0 * pageload_timeout / total, 2) as pageload_timeout_pct,
            round(100.0 * error_connection_or_dns / total, 2) as dns_error_pct,
            round(100.0 * error_selenium / total, 2) as selenium_error_pct,
            round(100.0 * error_invalid_har / total, 2) as firefox_error_pct,
            round(100.0 * error_other / total, 2) as other_error_pct
        FROM (
        SELECT
            recursive,
            dns_type,
            round(count(har) * 1.0 /count(uuid), 3) as successful_pct,
            count(uuid) as total,
            count(har) as successful,
            count(case when error like ''%%selenium.common.exceptions.TimeoutException%%'' then 1 end) as pageload_timeout,
            count(case when error like ''%%dnsNotFound%%'' or error like  ''%%connectionFailure%%'' then 1 end) as error_connection_or_dns,
            count(case when error like ''%%selenium.common.exceptions.WebDriverException%%''
                and error not like ''%%dnsNotFound%%''
                and error not like ''%%connectionFailure%%''
                then 1 end) as error_selenium,
            count(case when error like ''%%Invalid \\\\escape%%'' then 1 end) as error_invalid_har,
            count(case when error not like ''%%dnsNotFound%%''
                and error not like ''%%connectionFailure%%''
                and error not like ''%%selenium.common.exceptions.TimeoutException%%''
                and error not like ''%%selenium.common.exceptions.WebDriverException%%''
                and error not like ''%%Invalid \\escape%%''
                then 1 end) as error_other
        FROM
            %s
        GROUP BY
            recursive,
            dns_type
        ORDER BY
            recursive,
            dns_type
        ) AS y;', _tbl);
        END
    $f$
    LANGUAGE plpgsql;

\echo 'Loss 0%'
\echo '======='
SELECT * FROM failure_rates('har_table');

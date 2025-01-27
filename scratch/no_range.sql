-- Results query
WITH
    cte_1 AS (
        SELECT
            anon_1.patient_id AS patient_id,
            anon_1.snomedct_code AS snomedct_code,
            anon_1.numeric_value AS numeric_value
        FROM
            (
                SELECT
                    clinical_events.patient_id AS patient_id,
                    clinical_events.snomedct_code AS snomedct_code,
                    clinical_events.numeric_value AS numeric_value,
                    row_number() OVER (
                        PARTITION BY
                            clinical_events.patient_id
                        ORDER BY
                            clinical_events.date DESC,
                            clinical_events.numeric_value DESC,
                            clinical_events.snomedct_code DESC
                    ) AS anon_2
                FROM
                    clinical_events
                WHERE
                    clinical_events.snomedct_code IN (
                        '889391000000100',
                        '104482006',
                        '1018251000000107',
                        '219651000000107',
                        '201321000000108',
                        '389586005',
                        '219661000000105',
                        '104481004',
                        '34608000',
                        '1013211000000103',
                        '390318006',
                        '250637003',
                        '390961000'
                    )
            ) AS anon_1
        WHERE
            anon_1.anon_2 = 1
    ),
    cte_2 AS (
        SELECT DISTINCT
            cte_1.patient_id AS patient_id
        FROM
            cte_1
    ),
    cte_3 AS (
        SELECT
            cte_2.patient_id AS patient_id
        FROM
            cte_2
            LEFT OUTER JOIN cte_1 ON cte_1.patient_id = cte_2.patient_id
        WHERE
            cte_1.patient_id IS NOT NULL
    )
SELECT
    cte_3.patient_id,
    cte_1.snomedct_code AS last_event_code,
    cte_1.numeric_value AS last_event_value
FROM
    cte_3
    LEFT OUTER JOIN cte_1 ON cte_1.patient_id = cte_3.patient_id;
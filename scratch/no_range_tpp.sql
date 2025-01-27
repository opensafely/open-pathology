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
                        '390961000',
                        '390318006',
                        '250637003',
                        '219661000000105',
                        '219651000000107',
                        '389586005',
                        '34608000',
                        '201321000000108',
                        '1018251000000107',
                        '889391000000100',
                        '104481004',
                        '1013211000000103',
                        '104482006'
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
    LEFT OUTER JOIN cte_1 ON cte_1.patient_id = cte_3.patient_id;-- Setup query 001 / 008
SELECT * INTO [#tmp_1] FROM (SELECT anon_2.patient_id AS patient_id, anon_2.numeric_value AS numeric_value, anon_2.snomedct_code AS snomedct_code 
FROM (SELECT clinical_events.patient_id AS patient_id, clinical_events.numeric_value AS numeric_value, clinical_events.snomedct_code AS snomedct_code, row_number() OVER (PARTITION BY clinical_events.patient_id ORDER BY clinical_events.date DESC, clinical_events.numeric_value DESC, clinical_events.snomedct_code DESC) AS anon_3 
FROM (
            SELECT
                Patient_ID AS patient_id,
                CAST(NULLIF(ConsultationDate, '9999-12-31T00:00:00') AS date) AS date,
                NULL AS snomedct_code,
                CTV3Code AS ctv3_code,
                NumericValue AS numeric_value,
                Consultation_ID AS consultation_id,
                CodedEvent_ID
            FROM CodedEvent
            UNION ALL
            SELECT
                Patient_ID AS patient_id,
                CAST(NULLIF(ConsultationDate, '9999-12-31T00:00:00') AS date) AS date,
                ConceptId AS snomedct_code,
                NULL AS ctv3_code,
                NumericValue AS numeric_value,
                Consultation_ID AS consultation_id,
                CodedEvent_ID
            FROM CodedEvent_SNOMED
        ) AS clinical_events 
WHERE clinical_events.snomedct_code IN ('219651000000107', '201321000000108', '390961000', '219661000000105', '390318006', '34608000', '104482006', '1013211000000103', '104481004', '889391000000100', '389586005', '250637003', '1018251000000107')) AS anon_2 
WHERE anon_2.anon_3 = 1) AS anon_1;

-- Setup query 002 / 008
CREATE CLUSTERED INDEX [ix_#tmp_1_patient_id] ON [#tmp_1] (patient_id);

-- Setup query 003 / 008
SELECT * INTO [#tmp_2] FROM (SELECT [#tmp_1].patient_id AS patient_id 
FROM [#tmp_1] UNION SELECT [PatientsWithTypeOneDissent].[Patient_ID] AS patient_id 
FROM [PatientsWithTypeOneDissent]) AS anon_1;

-- Setup query 004 / 008
CREATE CLUSTERED INDEX [ix_#tmp_2_patient_id] ON [#tmp_2] (patient_id);

-- Setup query 005 / 008
SELECT * INTO [#tmp_3] FROM (SELECT [#tmp_2].patient_id AS patient_id 
FROM [#tmp_2] LEFT OUTER JOIN [#tmp_1] ON [#tmp_1].patient_id = [#tmp_2].patient_id LEFT OUTER JOIN [PatientsWithTypeOneDissent] ON [PatientsWithTypeOneDissent].[Patient_ID] = [#tmp_2].patient_id 
WHERE [#tmp_1].patient_id IS NOT NULL AND [PatientsWithTypeOneDissent].[Patient_ID] IS NULL) AS anon_1;

-- Setup query 006 / 008
CREATE CLUSTERED INDEX [ix_#tmp_3_patient_id] ON [#tmp_3] (patient_id);

-- Setup query 007 / 008
SELECT * INTO [#results] FROM (SELECT [#tmp_3].patient_id AS patient_id, [#tmp_1].snomedct_code AS last_event_code, [#tmp_1].numeric_value AS last_event_value 
FROM [#tmp_3] LEFT OUTER JOIN [#tmp_1] ON [#tmp_1].patient_id = [#tmp_3].patient_id) AS anon_1;

-- Setup query 008 / 008
CREATE CLUSTERED INDEX [ix_#results_patient_id] ON [#results] (patient_id);

-- Results query
SELECT [#results].patient_id, [#results].last_event_code, [#results].last_event_value 
FROM [#results];

-- Cleanup query 001 / 004
DROP TABLE IF EXISTS [#results];

-- Cleanup query 002 / 004
DROP TABLE IF EXISTS [#tmp_3];

-- Cleanup query 003 / 004
DROP TABLE IF EXISTS [#tmp_2];

-- Cleanup query 004 / 004
DROP TABLE IF EXISTS [#tmp_1];


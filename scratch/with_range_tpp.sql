-- Setup query 001 / 008
SELECT * INTO [#tmp_1] FROM (SELECT anon_2.patient_id AS patient_id, anon_2.lower_bound AS lower_bound, anon_2.comparator AS comparator, anon_2.upper_bound AS upper_bound, anon_2.snomedct_code AS snomedct_code, anon_2.numeric_value AS numeric_value 
FROM (SELECT clinical_events_ranges.patient_id AS patient_id, clinical_events_ranges.lower_bound AS lower_bound, clinical_events_ranges.comparator AS comparator, clinical_events_ranges.upper_bound AS upper_bound, clinical_events_ranges.snomedct_code AS snomedct_code, clinical_events_ranges.numeric_value AS numeric_value, row_number() OVER (PARTITION BY clinical_events_ranges.patient_id ORDER BY clinical_events_ranges.date DESC, clinical_events_ranges.comparator DESC, clinical_events_ranges.lower_bound DESC, clinical_events_ranges.numeric_value DESC, clinical_events_ranges.snomedct_code DESC, clinical_events_ranges.upper_bound DESC) AS anon_3 
FROM (
            SELECT
                ce.*,
                cer.LowerBound AS lower_bound,
                cer.UpperBound AS upper_bound,
                CASE cer.Comparator
                    WHEN 3 THEN '~'
                    WHEN 4 THEN '='
                    WHEN 5 THEN '>='
                    WHEN 6 THEN '>'
                    WHEN 7 THEN '<'
                    WHEN 8 THEN '<='
                END COLLATE Latin1_General_CI_AS AS comparator
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
        ) ce
            LEFT JOIN CodedEventRange cer
                ON ce.CodedEvent_ID = cer.CodedEvent_ID
        ) AS clinical_events_ranges 
WHERE clinical_events_ranges.snomedct_code IN ('104481004', '1018251000000107', '104482006', '390318006', '1013211000000103', '219651000000107', '250637003', '389586005', '219661000000105', '390961000', '889391000000100', '201321000000108', '34608000')) AS anon_2 
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
SELECT * INTO [#results] FROM (SELECT [#tmp_3].patient_id AS patient_id, [#tmp_1].snomedct_code AS last_event_code, [#tmp_1].lower_bound AS last_event_lower_bound, [#tmp_1].comparator AS last_event_comparator, [#tmp_1].numeric_value AS last_event_value, [#tmp_1].upper_bound AS last_event_upper_bound 
FROM [#tmp_3] LEFT OUTER JOIN [#tmp_1] ON [#tmp_1].patient_id = [#tmp_3].patient_id) AS anon_1;

-- Setup query 008 / 008
CREATE CLUSTERED INDEX [ix_#results_patient_id] ON [#results] (patient_id);

-- Results query
SELECT [#results].patient_id, [#results].last_event_code, [#results].last_event_lower_bound, [#results].last_event_comparator, [#results].last_event_value, [#results].last_event_upper_bound 
FROM [#results];

-- Cleanup query 001 / 004
DROP TABLE IF EXISTS [#results];

-- Cleanup query 002 / 004
DROP TABLE IF EXISTS [#tmp_3];

-- Cleanup query 003 / 004
DROP TABLE IF EXISTS [#tmp_2];

-- Cleanup query 004 / 004
DROP TABLE IF EXISTS [#tmp_1];


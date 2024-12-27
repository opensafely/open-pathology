# Walking Skeleton

To demonstrate that the skeleton can walk,
each of the following steps must be prefixed with "There is [a | an | some]...":

* **Motivating problem.**
  We agreed to recreate the Service Restoration Observatory [Liver Function Testing][1] key measure.

* **Codelist** on OpenCodelists.
  The key measure depends on [an existing codelist][2] on OpenCodelists.
  Whilst we may choose to update the existing codelist,
  we don't have to do so to demonstrate that the skeleton can walk.

* **Study code.**
  Ideally, we need a dataset definition and [a measure definition][3].
  If it's not possible to recreate the key measure with a measure definition,
  then we need R, Python, or Stata code
  first to aggregate patient-level data and
  then to apply statistical disclosure control.
  Ultimately, the study code must output a measure table.

* **Approved OpenSAFELY Application.**
  This is created by a member of the OpenPathology team and approved by NHSE.
  There can be no application, project, or workspace (see below)
  without an approved OpenSAFELY application.

* **Application and project** on OS Jobs.
  These are created by a member or the IG team.
  There can be no workspace (see below) without a project
  and no project without an application.

* **Workspace** on OS Jobs.
  This is created by a member of the OpenPathology team.
  Outputs, such as measure tables, are released and published to a workspace.

* **Released measure table** on OS Jobs.
  When the study code is run on the TPP backend, outputs are written to Level 4.
  (Outputs are also written to Level 3, but are inaccessible.)
  The measure table must be reviewed (R1 and R2) and released to OS Jobs.

* **Published measure table** on OS Jobs.
  The released measure table must be reviewed (Output Publisher) and published to OS Jobs.

* **Dashboard code.**
  This represents the published measure table, alongside supporting information.

* **Dashboard app.**
  When deployed to Streamlit Community Cloud, the dashboard code is known as an *app*
  (see "[Dashboards](dashboards.md)").
  Merging the dashboard code to the `main` branch automatically deploys it to Streamlit Community Cloud.

[1]: https://reports.opensafely.org/reports/sro-measures/#ALT
[2]: https://www.opencodelists.org/codelist/opensafely/alanine-aminotransferase-alt-tests/2298df3e/
[3]: https://docs.opensafely.org/ehrql/explanation/measures/

## Workflow

```mermaid
flowchart TD
    subgraph Local Development
    create_branch[Create branch] --> update_locally[Update code]
    update_locally --> run_locally[Run code]
    run_locally --> inspect_locally[Inspect outputs]
    inspect_locally --> update_locally
    inspect_locally --> push_to_gh[Push to GitHub]
    end
    subgraph OpenCodelists
    create_codelist[Create/update codelist] --> create_branch
    end
    subgraph GitHub
    push_to_gh --> run_ci[Code is run in CI]
    run_ci -->|CI failure| update_locally
    run_ci -->|CI success| create_pr[Create/Update PR]
    create_pr -->|Code review| request_code_review[Request code review]
    request_code_review -->|"(Time passes)"| code_reviewed[Code reviewed]
    code_reviewed --> receive_code_review[Receive code review]
    receive_code_review -->|Reviewer suggests changes| update_locally
    receive_code_review -->|Reviewer doesn't suggest changes| merge_pr[Merge PR]
    create_pr -->|No code review| merge_pr
    end
    subgraph Streamlit Community Cloud
    merge_pr -->|PR modified dashboard code| end_1[Dashboard is updated]
    end
    subgraph OS Jobs
    merge_pr -->|PR modified study code| submit_job_request[Submit job request]
    submit_job_request -->|"(Time passes)"| job_request_completed[Job request is completed]
    end
    subgraph Airlock
    job_request_completed --> inspect_l4[Inspect outputs/logs]
    inspect_l4 -->|Job request failure: System error| submit_job_request
    inspect_l4 -->|Job request failure: Code error| update_locally
    inspect_l4 -->|Job request success| submit_release_request[Submit release request]
    submit_release_request -->|"(Time passes)"| reviewed_r1[Request reviewed by R1]
    submit_release_request -->|"(Time passes)"| reviewed_r2[Request reviewed by R2]
    reviewed_r1 -->|"(Time passes)"| reviewed_r1_r2[Request reviewed by R1 and R2]
    reviewed_r2 -->|"(Time passes)"| reviewed_r1_r2
    reviewed_r1_r2 -->|"(Time passes)"| receive_response[Receive response to request]
    receive_response -->|Request approved| outputs_released[Outputs are released to OS Jobs]
    receive_response -->|Request denied| update_locally
    end
    subgraph OS Jobs
    outputs_released --> submit_publish_request[Submit publish request]
    submit_publish_request -->|"(Time passes)"| reviewed_r3[Request reviewed by Output Publisher]
    reviewed_r3 --> receive_publication_response[Recieve response to request]
    receive_publication_response -->|Request denied| end_2[Decide what to do next!]
    receive_publication_response -->|Request approved| outputs_published[Outputs are published to web]
    end
    outputs_published -->|Update dashboard| update_locally
    note_1@{shape: notch-rect, label: "Informal communication"}
    note_1 -.- submit_publish_request
    note_2@{shape: notch-rect, label: "Informal communication"}
    note_2 -.- receive_publication_response
```

# HR SIMULATE project audit

## Active application path

The deployed entry point is `app.py`. It invokes `engines/simulation_core.py` for
all seven module simulations. Dashboard, recommendations, comparison, and report
views consume that engine's KPI and series records.

The app's `Data Management` page offers Aggregate Parameter Mode with explicit
module-input mapping, cleaning choices, confirmation, and result provenance.
It also offers Record-Level Analysis Mode for compensation, attrition,
performance, and training records when the required schema is present. That
mode produces descriptive distributions rather than scalar simulations. The
synthetic generator covers all seven modules and exports CSV/XLSX.

## Findings and changes

| Area | Finding | Resolution |
|---|---|---|
| Attrition | Retention was derived from monthly attrition and did not distinguish original employees from replacement hires. Exit counts were also cumulatively subtracted from the current workforce. | Track original and replacement cohorts separately; use monthly mutually exclusive exit outcomes, exposure-based monthly rates, compounded period/annualized rates, and explicit workforce movement. |
| Workforce planning | Productivity was reported but did not affect staffing outputs; total cost used final workforce for every forecast month. | Compute required FTE from workload/productivity, capacity from supply × productivity, positive gap as required minus available FTE, and sum monthly labour costs. |
| Learning | ROI used an uncapped gain proxy and the value assumption was not separated from observed outcomes. | Separate eligibility, participation, enrollment, completion and passes; calculate pre/post score improvement, assumption-based benefit, cost, and ROI; return undefined ROI for zero cost. |
| Employee relations | A capacity arithmetic shortcut replaced queue behavior. | Simulate Poisson case counts scaled to the observation horizon and exponential service in a reproducible FIFO SimPy queue; report observed waits, censored cases, SLA denominator, and utilization. |
| Recruitment | Cost per hire used total budget rather than expenditure; a workload estimate was described as time-to-fill. | Calculate spend from funded applicants × cost per applicant; report undefined cost per hire at zero hires; relabel summed person-days as processing effort; cap screened and interviewed counts at configured scenario capacities. |
| Performance | Reward budget did not affect model outputs; causal and distribution assumptions needed clearer interpretation. | Allocate the full budget evenly among simulated employees rated 4 or higher; explain normal draws, clipping, fixed effect, and non-causal interpretation. Add optional matched descriptive comparison for uploaded performance records. |
| Employee relations | Average queue wait included cases still waiting at the observation boundary. | Calculate observed average only for cases whose investigation started; separate unresolved, waiting, in-service, pending age, and censored waits. |
| Dashboard | Department performance was displayed without a corresponding input dataset. | Removed the fabricated visualization and explain why it is not shown. |
| Uploaded data | No explicit mapping, cleaning confirmation, or simulation integration existed. | Add user-selected Aggregate Parameter Mode and schema-gated Record-Level Analysis Mode, cleaning options, confirmation for simulations, and provenance. |
| Synthetic data | Only incomplete employee/candidate generator functions existed; IDs and dates were not fully reproducible. | Add seed-reproducible records for each module and CSV/XLSX downloads. |

## Scope decisions

The calculations used by the deployed app are corrected in `simulation_core.py`.
Older standalone engine/module wrappers remain in the repository but are not
invoked by the `app.py` navigation or its simulation flow. They are not used as
an alternate path by the updated app.

No external empirical data or research validation is claimed. Record-level
outputs are descriptive summaries, not individual-level predictions or causal
estimates.

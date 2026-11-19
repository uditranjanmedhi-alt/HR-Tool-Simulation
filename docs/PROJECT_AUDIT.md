# HR SIMULATE project audit

## Active application path

The deployed entry point is `app.py`. It invokes `engines/simulation_core.py` for
all seven module simulations. Dashboard, recommendations, comparison, and report
views consume that engine's KPI and series records.

The app's original `Data Management` page parsed and previewed files but did not
feed them into a simulation. The updated page offers an explicit module-input
mapping, cleaning choices, confirmation, and result provenance. The synthetic
generator now covers all seven modules and exports CSV/XLSX.

## Findings and changes

| Area | Finding | Resolution |
|---|---|---|
| Attrition | Retention was derived from monthly attrition and did not distinguish original employees from replacement hires. Exit counts were also cumulatively subtracted from the current workforce. | Track original and replacement cohorts separately; use monthly mutually exclusive exit outcomes, exposure-based monthly rates, compounded period/annualized rates, and explicit workforce movement. |
| Workforce planning | Productivity was reported but did not affect staffing outputs; total cost used final workforce for every forecast month. | Compute required FTE from workload/productivity, capacity from supply × productivity, positive gap as required minus available FTE, and sum monthly labour costs. |
| Learning | ROI used an uncapped gain proxy and the value assumption was not separated from observed outcomes. | Separate eligibility, participation, enrollment, completion and passes; calculate pre/post score improvement, assumption-based benefit, cost, and ROI; return undefined ROI for zero cost. |
| Employee relations | A capacity arithmetic shortcut replaced queue behavior. | Simulate Poisson arrivals and exponential service in a reproducible FIFO SimPy queue with investigators, waiting, open backlog, SLA and utilization outputs. |
| Recruitment | Budget affected screening through an implicit formula with a hard-coded denominator. | Make the candidate-reach assumption explicit as cost per applicant and expose it in the module controls. |
| Performance | Reward budget did not affect model outputs. | Allocate the budget evenly among simulated employees rated 4 or higher and state the assumption in results. |
| Dashboard | Department performance was displayed without a corresponding input dataset. | Removed the fabricated visualization and explain why it is not shown. |
| Uploaded data | No explicit mapping, cleaning confirmation, or simulation integration existed. | Add user-selected mappings and aggregations, validation/cleaning options, confirmation, and provenance. |
| Synthetic data | Only incomplete employee/candidate generator functions existed; IDs and dates were not fully reproducible. | Add seed-reproducible records for each module and CSV/XLSX downloads. |

## Scope decisions

The calculations used by the deployed app are corrected in `simulation_core.py`.
Older standalone engine/module wrappers remain in the repository but are not
invoked by the `app.py` navigation or its simulation flow. They are not used as
an alternate path by the updated app.

No external empirical data or research validation is claimed. Uploaded data is
aggregated into model inputs only through the user's explicit mapping choices;
it is not treated as an individual-level prediction model.

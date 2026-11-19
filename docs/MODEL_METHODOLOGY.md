# Model methodology

The models are educational scenario calculations, not validated forecasts. The
same `run_simulation` functions are used for manually configured and
aggregate-parameter uploads. Record-Level Analysis Mode is a separate
descriptive path and does not convert individual records into scalar inputs.

## Recruitment & Talent Acquisition

- Funded applicants = min(applicants, floor(recruitment budget / cost per applicant)).
- Estimated recruitment spend (INR) = funded applicants × assumed cost per
  applicant. This modeled amount is not verified accounting expenditure;
  unused budget is not treated as modeled spend.
- Cost per hire (INR/hire) = estimated recruitment spend / employees joined;
  it is undefined when no employees join.
- Screened, shortlisted, interviewed, offered, accepted, and joined counts are
  computed sequentially with floors. Joined candidates are capped at vacancies.
- Screening is capped at recruiters × scenario screening capacity; interview
  volume is capped at interviewers × scenario interview capacity. These are
  scenario-wide throughput caps, not calendar schedules.
- Estimated recruitment processing effort (person-days) = screened candidates
  × screening effort per candidate + interviewed candidates × interview effort
  per candidate. This is a work-effort measure, not elapsed calendar
  time-to-fill.

This is a deterministic aggregate funnel, not an individual applicant outcome
model.

## Employee Attrition & Retention

For each month and employee cohort, one mutually exclusive outcome is sampled:
voluntary exit, involuntary exit, retirement, or continued employment. The sum
of exit probabilities cannot exceed 1.

- Closing workforce = opening workforce − exits + hires.
- Monthly workforce attrition (%) = total exits / cumulative opening-workforce
  employee-month exposure × 100.
- Annualized workforce attrition (%) = (1 − (1 − pooled monthly rate)^12) ×
  100. This compounds the pooled monthly exposure rate.
- Compounded period workforce attrition (%) = (1 − the product, across months,
  of (1 − monthly exits / that month's opening workforce)) × 100. Each month's
  denominator is its opening workforce, including replacement hires in later
  months. This is distinct from original-cohort retention.
- Original cohort exits count only employees in the starting workforce who
  exited during the period.
- Original cohort retention (%) = original-cohort employees still employed /
  initial workforce × 100. Replacement hires are tracked separately and do not
  enter this denominator.
- Net workforce change = final workforce − initial workforce.
- Estimated replacement cost (INR) = simulated exits × assumed replacement
  cost per exit.

The monthly, annualized, period, and cohort metrics describe different
denominators and are not interchangeable.

## Learning & Development

- Eligible = floor(employees × eligibility rate).
- Requested enrollment = floor(eligible × participation rate).
- Enrollment is capped by budget / cost per enrollee.
- Completion and assessment passes apply their configured sequential rates.
- Post score = min(100, pre score + assumed gain).
- Estimated financial benefit (INR) = assessment passes × observed score gain ×
  assumed INR value per score point.
- ROI (%) = 100 × (estimated benefit − training cost) / training cost.

Record-Level Analysis Mode summarizes observed scores and uses only records
with both pre- and post-training scores for paired change. ROI is undefined
when training cost is zero. Benefits and observed changes do not establish that
training caused a business outcome.

## Performance Management

Baseline ratings are independent normal draws using the configured mean and
standard deviation, clipped to the 1–5 scale. Clipping creates observations at
the scale boundaries and changes the realized mean. The fixed intervention
adds the same configured point effect to every baseline score, then clips again
to 1–5. It is a scenario assumption, not an estimated intervention effect.

The full reward budget is split equally across simulated employees rated 4 or
higher; if no employee reaches 4, nothing is allocated. Reward inputs and
allocations use INR. The model does not support causal claims or individual
employment decisions.

Record-Level Analysis Mode can optionally calculate matched employee pre/post
rating changes and a difference between two groups' mean changes when two
periods, employee identifiers, ratings, and a stable group column are present.
These are descriptive comparisons only; there is no control for confounding,
no causal estimate, and no significance test.

## Workforce Planning

Demand is a monthly forecast workload in standard-workload FTE units, where an
index of 1.0 corresponds to one FTE's standard capacity.

- Available supply is forecast from initial workforce and monthly turnover.
- Workload is forecast from initial demand and monthly growth.
- Required FTE = forecast workload / productivity index.
- Effective capacity = available FTE × productivity index.
- Workforce gap = required FTE − available FTE; a positive value is a shortage.
- Hiring requirement = ceiling of a positive gap.
- Total labour cost = sum over forecast months of monthly workforce supply ×
  monthly labour cost per employee. The app inputs and totals are in INR over
  the selected forecast horizon.

## Compensation & Benefits

Each employee's annual base salary is sampled from a normal distribution and
clipped to INR 20,000–300,000. Increment, bonus, and benefit costs are each a
configured percentage of annual base payroll. This is a scenario cost model,
not an equity analysis.

Record-Level Analysis Mode summarizes base salary, allowances, variable pay,
benefits, and per-record total compensation for complete records.

## Employee Relations

Unless a grievance count is supplied explicitly, the number of cases during
the observation period is Poisson distributed with expected count = employee
count × monthly grievance rate × observation days / 30. Conditional on the
count, arrival times are uniform over the period. When a count is supplied, it
is fixed and arrival times are still uniform. Cases enter a FIFO SimPy resource
queue with the configured number of investigators; individual service
durations follow an exponential distribution with the configured scale and a
0.01-day minimum.

- Average waiting time uses only cases that started investigation, so each
  included queue wait is observed rather than right-censored.
- Cases unresolved at the period boundary are separated into still waiting and
  already in investigation.
- Pending-case age is the time from arrival to the observation boundary for
  unresolved cases. Censored waiting time is reported separately for cases that
  are still waiting.
- Cases resolved + cases unresolved = total cases in the observation period.
- Average resolution time is arrival to resolution for resolved cases only.
- SLA compliance (%) = resolved within SLA / (all resolved cases + unresolved
  cases whose SLA deadline has passed) × 100. Unresolved cases not yet due are
  excluded; compliance is undefined when the denominator is zero.
- Utilization is observed investigator busy time / available investigator time.

The random seed controls grievance counts, arrivals, categories, and service
times.

## Uploaded-data modes

Aggregate Parameter Mode explicitly maps numeric columns to scalar model
parameters, applies the selected cleaning rules, and runs the same simulation
engine. Unmapped parameters retain their displayed defaults.

Record-Level Analysis Mode is available for compensation, attrition,
performance, and training records only when their required columns are
present. It reports per-measure descriptive statistics and distributions,
counts missing or invalid values, and can exclude exact duplicate rows.
Attrition record analysis reports a snapshot of status, exit categories, and
tenure; it does not infer a period rate without a risk period and person-time
denominator. Recruitment, workforce planning, and employee-relations records
do not currently have implemented record-level summaries.

## Monte Carlo and sensitivity analysis

Monte Carlo is limited to modules with stochastic outputs: attrition,
performance, compensation, and employee relations. Each iteration uses the
next seed. The 5th–95th percentiles are simulation percentiles, not confidence
intervals.

Sensitivity analysis changes one numeric input at a time within module input
bounds, uses a direction that remains valid at a boundary, and reports the
change in one module-specific output. Stochastic comparisons reuse the same
seed. It is a local, one-directional perturbation analysis, not a global
sensitivity measure.

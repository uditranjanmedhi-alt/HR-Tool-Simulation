# Model methodology

The models are educational scenario calculations, not validated forecasts. The
same `run_simulation` functions are used for manually configured, synthetic, and
uploaded-data parameter sets.

## Recruitment & Talent Acquisition

- Applicants available to screen = min(applicants, floor(budget / cost per applicant)).
- Screened candidates are limited by screening rate and recruiter capacity.
- Shortlisted, interviewed, offered, accepted, and joined candidates are computed
  sequentially from the preceding stage and configured rates.
- Joined candidates are capped at vacancies.
- Estimated effort = screened × screening days / recruiters + interviewed ×
  interview days / interviewers.
- The default planning assumption is 100 currency units per candidate reached.

This is a deterministic funnel, not an individual applicant outcome model.

## Employee Attrition & Retention

For each month and employee cohort, one mutually exclusive outcome is sampled:
voluntary exit, involuntary exit, retirement, or continued employment. The sum
of exit probabilities cannot exceed 1.

- Closing workforce = opening workforce − exits + hires.
- Monthly attrition = total exits / cumulative opening-workforce employee-months.
- Annualized attrition = 1 − (1 − average monthly attrition)^12.
- Period attrition compounds each observed month's exit rate.
- Original cohort retention = initial-cohort employees still employed / initial
  workforce. Replacement hires are tracked as another cohort.
- Net workforce change = final workforce − initial workforce.

## Learning & Development

- Eligible = floor(employees × eligibility rate).
- Requested enrollment = floor(eligible × participation rate).
- Enrollment is capped by budget / cost per enrollee.
- Completion and assessment passes apply their configured sequential rates.
- Post score = min(100, pre score + assumed gain).
- Estimated financial benefit = assessment passes × observed score gain ×
  assumed monetary value per score point.
- ROI (%) = 100 × (estimated benefit − training cost) / training cost.

ROI is undefined when training cost is zero. Benefits are assumption-based and
do not establish that training caused a business outcome.

## Performance Management

Pre-intervention ratings are sampled from a normal distribution clipped to 1–5.
The configured intervention points are added and clipped to the same scale.
Employees with an outcome rating of 4 or higher share the reward budget equally.
The intervention is an assumption and is not causal evidence.

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
  monthly labour cost per employee.

## Compensation & Benefits

Each employee's base salary is sampled from a normal distribution and clipped to
20,000–300,000 in the same currency units as the salary input. Increment, bonus,
and benefit costs are each a configured percentage of base payroll. This is a
scenario cost model, not an equity analysis.

## Employee Relations

The number of grievances during the observation period is Poisson distributed
with mean employee count × monthly grievance rate. Given the count, arrival
times are uniform over the period. Cases enter a FIFO SimPy resource queue with
the configured number of investigators; individual service times are
exponentially distributed with the configured mean and a 0.01-day minimum.

- Open grievances are those unresolved at the observation-period boundary.
- Average waiting includes time already spent waiting by open cases.
- Average resolution time includes resolved cases only and measures arrival to
  resolution.
- SLA compliance is the fraction of resolved cases meeting the configured
  arrival-to-resolution deadline.
- Utilization is observed investigator busy time / available investigator time.

The random seed controls grievance counts, arrivals, categories, and service
times.

## Monte Carlo and sensitivity analysis

Monte Carlo is limited to modules with stochastic outputs: attrition,
performance, compensation, and employee relations. Each iteration uses the
next seed. The 5th–95th percentiles are simulation percentiles, not confidence
intervals.

Sensitivity analysis changes one numeric input at a time, holds the seed fixed,
and reports the change in one module-specific output. It is a local,
one-directional perturbation analysis, not a global sensitivity measure.

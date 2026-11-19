# Assumptions and limitations

- All module outputs are educational scenarios and should not be interpreted as
  predictions about individual employees or candidates.
- A seed makes stochastic outputs reproducible for fixed code, parameters, and
  runtime behavior; it does not make assumptions empirically valid.
- Recruitment is a deterministic aggregate funnel. Candidate funding uses the
  assumed cost per applicant; estimated recruitment spend is funded applicants
  multiplied by that assumption and is not verified accounting expenditure.
  Cost per hire is undefined when there are no hires.
- Recruitment processing effort is the sum of screening and interview
  person-days. It is not calendar time-to-fill and does not model queueing,
  stage overlaps, or hiring dates.
- Recruiter and interviewer counts cap screened/interviewed scenario volumes
  using the configured per-person scenario capacities; this is not a timeline
  or elapsed-time model.
- Monthly workforce attrition uses exits per opening-workforce employee-month
  exposure; annualized workforce attrition compounds that pooled monthly rate.
  Compounded period workforce attrition applies each month's exit fraction to
  that month's opening workforce (which includes replacement hires in later
  months). Original-cohort exits and retention use only the starting cohort;
  replacement hires are excluded from the retention denominator.
- Attrition exit categories are mutually exclusive monthly probabilities.
  Replacement hiring is a fixed monthly count; hires are not targeted to
  specific vacancies or skill requirements.
- Learning benefit assigns a configurable monetary amount per score point and
  assessment pass; active-app monetary inputs and results are in INR. No causal
  evaluation or observed financial impact is available.
- Performance ratings assume independent normal draws and are clipped to 1–5;
  clipping changes the distribution. A fixed effect is added to every score,
  and the full reward budget is divided equally among simulated ratings of 4
  or higher. These rules are not estimated from organization data and do not
  establish causality.
- Record-level performance pre/post and group comparisons are matched,
  descriptive changes only. They do not control for confounding, provide
  significance tests, or justify causal or individual-level conclusions.
- Workforce demand is treated as standard workload at productivity index 1.0.
  The model does not distinguish roles, skills, locations, or FTE contract
  fractions.
- Compensation distributions and percentages are aggregate scenarios. The
  active app treats salary and compensation totals as INR/year. The model does
  not assess pay equity, market competitiveness, tax, or currency conversion.
- Unless a fixed count is supplied, employee-relations cases use a Poisson
  count with mean scaled by observation days / 30; arrivals are uniform given
  the count. Service durations use an exponential distribution with a 0.01-day
  minimum. The model has one FIFO queue, identical investigator capacity, and
  no priority classes, case complexity, weekends, or time-varying schedules.
  Average waiting uses only cases whose investigation has started; unresolved
  cases are censored at the observation boundary and reported separately.
  SLA compliance counts resolved cases and unresolved cases already past
  deadline; cases whose deadline has not passed are excluded from that
  denominator.
- Aggregate Parameter Mode maps selected uploaded columns to scalar model
  inputs. Record-Level Analysis Mode summarizes compensation, attrition,
  performance, and training records only when their required columns are
  available; it does not run the scalar simulation. Missing/invalid numeric
  values are excluded per measure and counted. Attrition snapshots do not
  produce a period rate without a specified risk period and person-time
  denominator.
- Monte Carlo intervals reflect the model's configured randomness only; they
  are not statistical confidence intervals or calibrated prediction intervals.
- Sensitivity analysis is one-at-a-time and bounded by module input ranges. It
  does not estimate interactions or prove causality.
- Dashboard summary metrics are explicitly illustrative synthetic scenarios.
  Company data is not used to fabricate department distributions or home-page
  KPIs.
- Scenario state is session-only. Uploaded data is held in Streamlit session
  state and is not sent to an external AI service.

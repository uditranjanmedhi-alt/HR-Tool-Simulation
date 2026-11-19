# Assumptions and limitations

- All module outputs are educational scenarios and should not be interpreted as
  predictions about individual employees or candidates.
- A seed makes stochastic outputs reproducible for fixed code, parameters, and
  runtime behavior; it does not make assumptions empirically valid.
- Recruitment is a deterministic aggregate funnel. Candidate funding uses the
  configured cost per applicant; actual spend is funded applicants multiplied
  by that cost. Cost per hire is undefined when there are no hires.
- Recruitment processing effort is the sum of screening and interview
  person-days. It is not calendar time-to-fill and does not model queueing,
  stage overlaps, or hiring dates.
- Attrition monthly workforce rate uses exits per opening-workforce
  employee-month exposure; annualized rate compounds that pooled rate. Period
  workforce attrition compounds monthly exit fractions using each month's
  opening workforce. Original cohort exits and retention use only the starting
  cohort; replacement hires are excluded from the retention denominator.
- Attrition exit categories are mutually exclusive monthly probabilities.
  Replacement hiring is a fixed monthly count; hires are not targeted to
  specific vacancies or skill requirements.
- Learning benefit assigns a configurable monetary amount per score point and
  assessment pass. No causal evaluation or observed financial impact is
  available.
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
  model does not assess pay equity, market competitiveness, tax, or currency
  conversion.
- Employee-relations cases use Poisson arrivals and exponential service times,
  one FIFO queue, identical investigator capacity, and no priority classes,
  case complexity, weekends, or time-varying schedules. Average waiting uses
  only cases whose investigation has started; unresolved cases are censored at
  the observation boundary and reported separately.
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

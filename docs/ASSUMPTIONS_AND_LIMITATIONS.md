# Assumptions and limitations

- All module outputs are educational scenarios and should not be interpreted as
  predictions about individual employees or candidates.
- A seed makes stochastic outputs reproducible for fixed code, parameters, and
  runtime behavior; it does not make assumptions empirically valid.
- Recruitment is a deterministic aggregate funnel. Candidate budget reach
  assumes 100 currency units per applicant unless the user changes that input.
- Attrition exit categories are mutually exclusive monthly probabilities.
  Replacement hiring is a fixed monthly count; hires are not targeted to
  specific vacancies or skill requirements.
- Learning benefit assigns a configurable monetary amount per score point and
  assessment pass. No causal evaluation or observed financial impact is
  available in this model.
- Performance scores use a clipped normal distribution. The intervention and
  reward allocation rule are assumptions, not evidence-based employee ratings.
- Workforce demand is treated as standard workload at productivity index 1.0.
  The model does not distinguish roles, skills, locations, or FTE contract
  fractions.
- Compensation distributions and percentages are aggregate scenarios. The
  model does not assess pay equity, market competitiveness, tax, or currency
  conversion.
- Employee-relations cases use Poisson arrivals and exponential service times,
  one FIFO queue, identical investigator capacity, and no priority classes,
  case complexity, weekends, or time-varying schedules.
- Upload mappings aggregate selected columns to scalar model inputs. They do
  not preserve employee-level records in simulation outputs, automatically infer
  business definitions, or validate organization-specific policy.
- Monte Carlo intervals reflect the model's configured randomness only; they
  are not statistical confidence intervals or calibrated prediction intervals.
- Sensitivity analysis is one-at-a-time and local. It does not estimate
  interactions or prove causality.
- Dashboard summary metrics are explicitly illustrative synthetic scenarios.
  Company data is not used to fabricate department distributions or home-page
  KPIs.
- Scenario state is session-only. Uploaded data is held in Streamlit session
  state and is not sent to an external AI service.

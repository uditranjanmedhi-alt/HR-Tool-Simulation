# hr_simulate/data/synthetic_generator.py
"""Synthetic data generation utilities for HR Simulate.
Provides functions to generate realistic synthetic datasets for all modules.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import uuid

from .schema import SCHEMA


def _random_dates(start: datetime, end: datetime, n: int) -> list:
    """Generate a list of n random dates between start and end."""
    delta = end - start
    return [start + timedelta(days=np.random.rand() * delta.days) for _ in range(n)]


def generate_employees(num: int = 500, num_departments: int = 5, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    employee_ids = [str(uuid.uuid4()) for _ in range(num)]
    departments = [f"Dept_{i+1}" for i in np.random.randint(0, num_departments, size=num)]
    job_levels = np.random.choice(["Junior", "Mid", "Senior", "Lead"], size=num, p=[0.4, 0.3, 0.2, 0.1])
    salaries = np.random.normal(60000, 15000, size=num).clip(30000, 200000).astype(int)
    hire_dates = _random_dates(datetime.now() - timedelta(days=365*5), datetime.now(), num)
    experience = np.random.exponential(scale=3, size=num).clip(0, 30).round(1)
    performance = np.random.normal(3.0, 0.7, size=num).clip(1, 5).round(2)
    df = pd.DataFrame({
        "employee_id": employee_ids,
        "department": departments,
        "job_level": job_levels,
        "salary": salaries,
        "hire_date": hire_dates,
        "experience_years": experience,
        "performance_score": performance,
    })
    df["synthetic"] = True
    return df[SCHEMA["employees"] + ["synthetic"]]


def generate_candidates(num: int = 300, num_departments: int = 5, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed + 1)
    candidate_ids = [str(uuid.uuid4()) for _ in range(num)]
    sources = np.random.choice(["Referral", "Job Portal", "Agency", "Campus", "Internal"], size=num)
    positions = np.random.choice(["Engineer", "Analyst", "Manager", "Director"], size=num)
    edu_levels = np.random.choice(["High School", "Bachelors", "Masters", "PhD"], size=num, p=[0.1, 0.6, 0.25, 0.05])
    years_exp = np.random.exponential(scale=2, size=num).clip(0, 20).round(1)
    app_dates = _random_dates(datetime.now() - timedelta(days=180), datetime.now(), num)
    df = pd.DataFrame({
        "candidate_id": candidate_ids,
        "source": sources,
        "applied_position": positions,
        "education_level": edu_levels,
        "years_experience": years_exp,
        "application_date": app_dates,
    })
    df["synthetic"] = True
    return df[SCHEMA["candidates"] + ["synthetic"]]

# Additional generators can be added similarly for training, performance, compensation, grievances.

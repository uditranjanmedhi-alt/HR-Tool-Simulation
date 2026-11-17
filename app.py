"""HR SIMULATE: local, educational HR decision and simulation dashboard."""

from __future__ import annotations

import csv
from datetime import datetime
from io import BytesIO
import html
import io
import time
import zipfile

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from config.settings import CHART_COLORS, THEME
from engines.simulation_core import MODULES, run_simulation


st.set_page_config(page_title="HR SIMULATE | Decision Lab", page_icon="🏢", layout="wide")

NAV_ITEMS = [
    "Home Dashboard", *MODULES.keys(), "HR Manager Decision Lab",
    "Scenario Comparison", "Data Management", "AI Recommendations",
    "Reports & Exports", "Settings & Documentation",
]
st.markdown(
    """
    <style>
    :root { --canvas:#0B1220; --surface:#111827; --panel:#172033; --line:#334155;
        --line-strong:#475569; --text:#F8FAFC; --muted:#94A3B8; --primary:#3B82F6;
        --teal:#14B8A6; --accent:#38BDF8; }
    .stApp { background:var(--canvas); color:var(--text); }
    [data-testid="stHeader"] { background:var(--canvas); }
    .main .block-container { max-width: 1540px; padding: 2rem clamp(1rem,3vw,2.7rem) 3rem; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,var(--canvas),var(--surface)); border-right:1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding:1.2rem .85rem; }
    [data-testid="stMetric"] { background:linear-gradient(145deg,var(--panel),var(--surface)); border:1px solid var(--line);
        padding:1rem 1.05rem; border-radius:13px; box-shadow:0 8px 22px rgba(2,6,23,.32); min-height:104px; }
    [data-testid="stMetricLabel"] { color:var(--muted); font-size:.78rem; font-weight:600; letter-spacing:.04em; }
    [data-testid="stMetricValue"] { color:var(--text); font-size:1.65rem; font-weight:700; }
    h1,h2,h3 { color:var(--text); letter-spacing:-.025em; }
    h1 { font-size:2rem; }
    h2 { font-size:1.3rem; }
    p, label { color:var(--muted); }
    div[data-testid="stVerticalBlockBorderWrapper"] { background:var(--surface); border-color:var(--line); border-radius:16px; }
    .brand { display:flex; align-items:center; gap:11px; padding:.35rem .35rem 1rem; }
    .brand-mark { width:38px; height:38px; display:grid; place-items:center; border-radius:12px;
        color:var(--canvas); font-weight:900; background:linear-gradient(140deg,#38BDF8,#2DD4BF); }
    .brand-title { color:var(--text); font-size:1rem; font-weight:800; letter-spacing:.08em; }
    .brand-subtitle { color:var(--muted); font-size:.68rem; margin-top:2px; }
    .nav-section { color:var(--muted); font-size:.68rem; font-weight:700; letter-spacing:.12em;
        text-transform:uppercase; margin:1.1rem .5rem .35rem; }
    .page-eyebrow { color:#38BDF8; font-weight:700; font-size:.72rem; text-transform:uppercase; letter-spacing:.13em; }
    .page-description { color:var(--muted); font-size:1rem; margin-top:-.55rem; margin-bottom:1.05rem; }
    .status-row { display:flex; flex-wrap:wrap; gap:8px; margin:.2rem 0 1rem; }
    .status-pill { color:var(--text); background:var(--panel); border:1px solid var(--line); border-radius:999px;
        padding:5px 10px; font-size:.72rem; font-weight:600; }
    .data-table { overflow-x:auto; margin:.5rem 0 1rem; border:1px solid var(--line); border-radius:10px; }
    .data-table table { border-collapse:collapse; width:100%; color:var(--text); font-size:.88rem; background:var(--surface); }
    .data-table th,.data-table td { border-bottom:1px solid var(--line); padding:9px 11px; text-align:left; }
    .data-table th { color:var(--text); background:#1D4ED8; font-size:.75rem; text-transform:uppercase; letter-spacing:.04em; }
    .data-table tr:last-child td { border-bottom:0; }
    [data-testid="stSidebar"] button { border-radius:9px; border:1px solid var(--line); text-align:left; }
    [data-testid="stSidebar"] button[kind="secondary"] { color:var(--muted); background:var(--surface); }
    [data-testid="stSidebar"] button[kind="secondary"]:hover { color:var(--text); background:var(--panel); border-color:var(--accent); }
    button[kind="primary"] { background:linear-gradient(100deg,#2563EB,#1D4ED8); border:1px solid #60A5FA; color:var(--text); }
    button[kind="primary"]:hover { background:#1D4ED8; border:1px solid #93C5FD; color:var(--text); }
    button[kind="secondary"] { border-color:var(--line-strong); color:var(--text); background:var(--panel); }
    [data-testid="stProgress"] > div > div > div { background:var(--accent); }
    [data-testid="stTabs"] button { color:var(--muted); font-weight:650; }
    [data-testid="stTabs"] button[aria-selected="true"] { color:var(--text); border-bottom-color:var(--accent); }
    [data-testid="stExpander"] { border:1px solid var(--line); border-radius:11px; background:var(--surface); }
    [data-testid="stAlert"] { background:var(--panel); border:1px solid var(--line); color:var(--text); }
    [data-testid="stAlertContainer"] {
        background:var(--panel) !important; border-color:var(--line) !important; color:var(--text) !important;
    }
    [data-testid="stAlert"] p, [data-testid="stAlertContainer"] * {
        color:var(--text) !important; fill:var(--text) !important;
    }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] [role="combobox"] {
        background:var(--surface); color:var(--text); border-color:var(--line-strong);
    }
    input::placeholder, textarea::placeholder { color:var(--muted); }
    [data-testid="stSlider"] [role="slider"] { border-color:#BAE6FD; background:var(--accent); }
    [data-testid="stAlert"] svg { color:var(--text); fill:var(--text); }
    [data-baseweb="menu"], [data-baseweb="popover"] { background:var(--panel); color:var(--text); }
    .small-note { color:var(--muted); font-size:.84rem; }
    [data-testid="stAppViewContainer"]::after {
        content:"Made by Udit Ranjan Medhi";
        position:fixed; right:18px; bottom:10px; z-index:999;
        color:rgba(203,213,225,.78); background:rgba(11,18,32,.82);
        border:1px solid rgba(71,85,105,.72); border-radius:999px;
        padding:6px 10px; font-size:.7rem; font-weight:600; letter-spacing:.02em;
        pointer-events:none; backdrop-filter:blur(6px);
    }
    @media (max-width: 1100px) {
      .main .block-container { padding:1.2rem 1rem 2rem; }
      [data-testid="stMetric"] { padding:.85rem; }
      [data-testid="stMetricValue"] { font-size:1.35rem; }
    }
    @media (max-width: 700px) {
      .main .block-container { padding:.8rem .7rem 1.5rem; }
      h1 { font-size:1.55rem; }
      .status-row { gap:5px; }
      [data-testid="stAppViewContainer"]::after { right:8px; bottom:7px; font-size:.65rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state() -> None:
    default_department_names = ["Engineering", "Operations", "Sales", "Finance", "HR"]
    default_department_counts = np.random.default_rng(42).multinomial(500, [0.32, 0.24, 0.18, 0.16, 0.10])
    defaults = {
        "random_seed": 42,
        "scenarios": [],
        "latest_results": {},
        "uploaded_data": None,
        "department_rows": [
            {"id": index + 1, "name": name, "employees": int(default_department_counts[index])}
            for index, name in enumerate(default_department_names)
        ],
        "next_department_id": len(default_department_names) + 1,
        "decision_case": "Recruitment crisis",
        "active_module": "Recruitment & Talent Acquisition",
        "active_page": "Home Dashboard",
        "control_epoch": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


def render_sidebar() -> str:
    st.sidebar.markdown(
        '<div class="brand"><div class="brand-mark">HR</div><div><div class="brand-title">HR SIMULATE</div>'
        '<div class="brand-subtitle">PEOPLE ANALYTICS • DECISION LAB</div></div></div>',
        unsafe_allow_html=True,
    )
    groups = [
        ("Workspace", [("Home Dashboard", "⌂")]),
        ("People modules", [
            ("Recruitment & Talent Acquisition", "◈"), ("Employee Attrition & Retention", "↗"),
            ("Learning & Development", "✦"), ("Performance Management", "◎"),
            ("Workforce Planning", "▦"), ("Compensation & Benefits", "◇"),
            ("Employee Relations", "✳"),
        ]),
        ("Tools", [
            ("HR Manager Decision Lab", "⚖"), ("Scenario Comparison", "⇄"),
            ("Data Management", "▤"), ("AI Recommendations", "✧"),
            ("Reports & Exports", "⇩"), ("Settings & Documentation", "⚙"),
        ]),
    ]
    for group, items in groups:
        st.sidebar.markdown(f'<div class="nav-section">{group}</div>', unsafe_allow_html=True)
        for label, icon in items:
            if st.sidebar.button(
                f"{icon}   {label}", key=f"nav_{label}", width="stretch",
                type="primary" if st.session_state.active_page == label else "secondary",
            ):
                st.session_state.active_page = label
                st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.caption("Illustrative data · Local session")
    return st.session_state.active_page


page = render_sidebar()


def styled_chart(fig):
    for trace in fig.data:
        if isinstance(trace, go.Bar) and trace.text is not None:
            trace.textposition = "outside"
            trace.textfont = {"color": THEME["text_light"]}
            trace.cliponaxis = False
        elif isinstance(trace, go.Funnel):
            trace.textposition = "outside"
            trace.textfont = {"color": THEME["text_light"]}
    fig.update_layout(
        template="none", paper_bgcolor=THEME["card_bg"], plot_bgcolor=THEME["card_bg"],
        margin=dict(l=12, r=12, t=55, b=12),
        font=dict(color=THEME["text_light"], family="Inter, Segoe UI, sans-serif"),
        colorway=CHART_COLORS,
        legend=dict(font=dict(color=THEME["muted"])),
        hoverlabel=dict(bgcolor=THEME["panel"], font=dict(color=THEME["text_light"])),
        xaxis=dict(gridcolor=THEME["border"], linecolor=THEME["border_strong"],
                   zerolinecolor=THEME["border"], tickfont=dict(color=THEME["muted"]),
                   title_font=dict(color=THEME["text_light"])),
        yaxis=dict(gridcolor=THEME["border"], linecolor=THEME["border_strong"],
                   zerolinecolor=THEME["border"], tickfont=dict(color=THEME["muted"]),
                   title_font=dict(color=THEME["text_light"])),
    )
    return fig


def records_to_csv(records: list[dict], columns: list[str] | None = None) -> bytes:
    headers = columns or (list(records[0]) if records else [])
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue().encode("utf-8")


def rows_to_csv(columns: list[str], rows: list[list]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(columns)
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def render_table(columns: list[str], rows: list[list]) -> None:
    header = "".join(f"<th>{html.escape(str(column))}</th>" for column in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape('' if value is None else str(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
    st.markdown(f'<div class="data-table"><table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table></div>',
                unsafe_allow_html=True)


def show_kpis(kpis: list[dict], per_row: int = 4) -> None:
    for start in range(0, len(kpis), per_row):
        batch = kpis[start:start + per_row]
        columns = st.columns(len(batch))
        for column, row in zip(columns, batch):
            value = row["Value"]
            if isinstance(value, (float, np.floating)):
                display_value = f"{value:,.2f}"
            elif isinstance(value, (int, np.integer)):
                display_value = f"{value:,}"
            else:
                display_value = str(value)
            column.metric(str(row["KPI"]), display_value)


def page_header(title: str, description: str, section: str = "HR SIMULATE • DECISION LAB") -> None:
    st.markdown(f'<div class="page-eyebrow">{html.escape(section)}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="page-description">{html.escape(description)}</div>', unsafe_allow_html=True)


def kpi_values(result: dict) -> dict:
    return {row["KPI"]: row["Value"] for row in result["kpis"]}


def render_insights(module: str, params: dict, result: dict) -> None:
    values = kpi_values(result)
    insights: list[tuple[str, str]] = []
    if module == "Recruitment & Talent Acquisition":
        attainment = values["Hiring Target Attainment (%)"]
        counts = result["series"]
        conversions = [
            (counts[index]["Stage"], counts[index + 1]["Stage"],
             counts[index + 1]["Count"] / max(1, counts[index]["Count"]))
            for index in range(len(counts) - 1)
        ]
        bottleneck = min(conversions, key=lambda item: item[2])
        insights = [
            ("What worked", f"Budget and capacity produced {values['Employees Joined']} hires "
             f"({attainment:.1f}% of the {values['Vacancies']} vacancy target)."),
            ("Bottleneck", f"{bottleneck[0]} → {bottleneck[1]} conversion is "
             f"{bottleneck[2] * 100:.1f}%, the lowest step in this funnel."),
            ("Manager action", "Test additional screening capacity or recruiter availability, then compare the funnel and time-to-fill."),
            ("Trade-off", f"Budget spend is {values['Budget']:,.0f}; improving conversion can lower cost per hire, "
             "but may require more sourcing or interviewer time."),
        ]
    elif module == "Employee Attrition & Retention":
        rate = values["Annualized Attrition Rate (%)"]
        insights = [
            ("What changed", f"Workforce moves from {values['Initial Workforce']} to {values['Final Workforce']} "
             f"over {params['months']} months."),
            ("Pressure point", f"Annualized attrition is {rate:.1f}%; simulated replacement cost is "
             f"{values['Estimated Replacement Cost']:,.0f}."),
            ("Manager action", "Test a lower voluntary-exit assumption alongside replacement hiring and compare final headcount."),
            ("Trade-off", "More replacement hiring stabilizes headcount but increases hiring demand and associated costs."),
        ]
    elif module == "Learning & Development":
        insights = [
            ("Participation", f"{values['Enrolled']} of {values['Employees']} employees are funded for training."),
            ("Learning outcome", f"{values['Training Completion Rate (%)']:.1f}% completion; estimated ROI "
             f"is {values['Estimated Training ROI (%)']:.1f}%."),
            ("Manager action", "If completion is low, test schedule, delivery method and manager support before increasing spend."),
            ("Trade-off", f"Budget utilization is {values['Budget Utilization (%)']:.1f}%; broader reach may limit per-person investment."),
        ]
    elif module == "Performance Management":
        insights = [
            ("Baseline", f"Average simulated score starts at {values['Baseline Average Performance Score']:.2f}."),
            ("Intervention", f"Estimated post-intervention score is {values['Average Performance Score After Intervention']:.2f}; "
             f"{values['Employees Requiring Support (%)']:.1f}% remain below the support threshold."),
            ("Manager action", "Use the distribution to target coaching and development resources."),
            ("Safeguard", "Ratings are synthetic scenario outputs and must not be used to automate individual employment decisions."),
        ]
    elif module == "Workforce Planning":
        gap = values["Workforce Gap"]
        insights = [
            ("Forecast", f"Supply is {values['Forecast Workforce Supply']} against demand of "
             f"{values['Forecast Workforce Demand']} at the end of the horizon."),
            ("Staffing", f"{'Shortage' if gap < 0 else 'Surplus'} of {abs(gap)} employees; "
             f"estimated hiring requirement is {values['Hiring Requirement']}."),
            ("Manager action", "Compare recruitment, internal mobility, retention and productivity assumptions."),
            ("Trade-off", f"Forecast labour cost is {values['Estimated Labour Cost']:,.0f}; demand growth may increase spend."),
        ]
    elif module == "Compensation & Benefits":
        insights = [
            ("Cost outlook", f"Total simulated compensation is {values['Total Compensation Cost']:,.0f}."),
            ("Pay movement", f"Increment cost is {values['Increment Cost']:,.0f}; benefits cost is "
             f"{values['Benefits Cost']:,.0f}."),
            ("Manager action", "Compare total rewards with an appropriate, validated market benchmark."),
            ("Safeguard", "This model does not assess individual pay equity or recommend employee-level compensation decisions."),
        ]
    else:
        insights = [
            ("Case volume", f"{values['Total Grievances']} simulated grievances; "
             f"{values['Pending Grievances']} remain pending."),
            ("Resolution", f"{values['Resolution Rate (%)']:.1f}% resolved in-period at an average "
             f"{values['Average Resolution Time (days)']} days."),
            ("Manager action", "Review case capacity and recurring categories; prioritize fair and timely process."),
            ("Safeguard", "The simulation does not assess individual grievances or automate disciplinary decisions."),
        ]
    columns = st.columns(2)
    for index, (title, body) in enumerate(insights):
        with columns[index % 2]:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(body)


def control_key(module: str, name: str) -> str:
    epoch = st.session_state.control_epoch.get(module, 0)
    return f"control_{MODULES[module]}_{epoch}_{name}"


def module_parameters(module: str) -> dict:
    def number(label: str, *args, **kwargs):
        return st.number_input(label, *args, key=control_key(module, label), **kwargs)

    def slider(label: str, *args, **kwargs):
        return st.slider(label, *args, key=control_key(module, label), **kwargs)

    if module == "Recruitment & Talent Acquisition":
        requirements, capacity_tab, conversion = st.tabs(
            ["Hiring requirements", "Recruitment capacity", "Conversion parameters"])
        with requirements:
            left, right = st.columns(2)
            with left:
                vacancies = number("Vacancies", 1, 1000, 50)
                applicants = number("Applicants", 1, 10000, 500)
            with right:
                budget = number("Recruitment budget", 0.0, 10000000.0, 75000.0, step=5000.0)
        with capacity_tab:
            left, right, third = st.columns(3)
            with left:
                recruiters = slider("Recruiters", 1, 30, 3)
            with right:
                interviewers = slider("Interviewers available", 1, 30, 5)
            with third:
                screen_capacity = number("Screening capacity per recruiter", 1, 5000, 200, step=25)
            left, right = st.columns(2)
            with left:
                screen_days = slider("Screening effort (days per candidate)", 0.1, 5.0, 0.5, 0.1)
            with right:
                interview_days = slider("Interview duration (days)", 0.1, 5.0, 1.0, 0.1)
        with conversion:
            left, middle, right = st.columns(3)
            with left:
                screen_rate = slider("Screening rate", 0.0, 1.0, 0.8, 0.05)
                shortlist_rate = slider("Screen-to-shortlist rate", 0.0, 1.0, 0.35, 0.05)
            with middle:
                dropout_rate = slider("Interview dropout rate", 0.0, 1.0, 0.1, 0.05)
                offer_rate = slider("Interview-to-offer rate", 0.0, 1.0, 0.9, 0.05)
            with right:
                acceptance_rate = slider("Offer acceptance rate", 0.0, 1.0, 0.75, 0.05)
                joining_rate = slider("Joining rate after acceptance", 0.0, 1.0, 0.9, 0.05)
        return {"vacancies": vacancies, "applicants": applicants, "recruiters": recruiters,
                "interviewers": interviewers, "screen_capacity": screen_capacity, "budget": budget,
                "screen_rate": screen_rate, "shortlist_rate": shortlist_rate,
                "dropout_rate": dropout_rate, "offer_rate": offer_rate,
                "acceptance_rate": acceptance_rate, "joining_rate": joining_rate,
                "screen_days": screen_days, "interview_days": interview_days}

    if module == "Employee Attrition & Retention":
        staffing, assumptions = st.tabs(["Workforce & horizon", "Exit assumptions & cost"])
        with staffing:
            workforce = number("Current workforce", 1, 100000, 500)
            months = slider("Simulation duration (months)", 1, 36, 12)
            hires = slider("Replacement hires per month", 0, 500, 15, 5)
        with assumptions:
            voluntary = slider("Monthly voluntary exit probability", 0.0, 0.2, 0.02, 0.005)
            involuntary = slider("Monthly involuntary exit probability", 0.0, 0.1, 0.005, 0.001)
            retirement = slider("Monthly retirement probability", 0.0, 0.1, 0.002, 0.001)
            replacement_cost = number("Estimated replacement cost per exit", 0.0, 1000000.0, 12000.0, step=1000.0)
        return {"workforce": workforce, "months": months, "voluntary": voluntary,
                "involuntary": involuntary, "retirement": retirement, "hires": hires,
                "replacement_cost": replacement_cost}

    if module == "Learning & Development":
        program, outcomes = st.tabs(["Program & budget", "Learning outcomes"])
        with program:
            employees = number("Employees in scope", 1, 100000, 500)
            left, right = st.columns(2)
            with left:
                budget = number("Training budget", 0.0, 100000000.0, 50000.0, step=5000.0)
                cost_per_person = number("Training cost per enrollee", 0.0, 100000.0, 500.0, step=100.0)
            with right:
                participation = slider("Participation rate", 0.0, 1.0, 0.7, 0.05)
                completion = slider("Completion rate", 0.0, 1.0, 0.82, 0.05)
        with outcomes:
            left, right = st.columns(2)
            with left:
                pass_rate = slider("Assessment pass rate", 0.0, 1.0, 0.75, 0.05)
                learning_gain = slider("Average learning gain (points)", 0.0, 5.0, 1.2, 0.1)
            with right:
                value_per_gain = number("Estimated value per gain point", 0.0, 100000.0, 150.0, step=25.0)
        return {"employees": employees, "budget": budget, "cost_per_person": cost_per_person,
                "participation": participation, "completion": completion, "pass_rate": pass_rate,
                "learning_gain": learning_gain, "value_per_gain": value_per_gain}

    if module == "Performance Management":
        population, intervention = st.tabs(["Review population", "Development & rewards"])
        with population:
            employees = number("Employees in scope", 1, 100000, 500)
            mean_rating = slider("Expected rating (1–5)", 1.0, 5.0, 3.2, 0.1)
            rating_spread = slider("Rating variation", 0.1, 2.0, 0.8, 0.1)
        with intervention:
            training_effect = slider("Training intervention (estimated points)", 0.0, 2.0, 0.2, 0.1)
            reward_budget = number("Reward budget", 0.0, 100000000.0, 50000.0, step=5000.0)
        return {"employees": employees, "mean_rating": mean_rating, "rating_spread": rating_spread,
                "training_effect": training_effect, "reward_budget": reward_budget}

    if module == "Workforce Planning":
        demand_tab, cost_tab = st.tabs(["Supply & demand", "Productivity & cost"])
        with demand_tab:
            workforce = number("Current workforce", 1, 100000, 500)
            demand = number("Current workforce demand", 1, 100000, 540)
            months = slider("Forecast horizon (months)", 1, 60, 12)
            growth = slider("Monthly demand growth", -0.1, 0.2, 0.01, 0.01)
            turnover = slider("Monthly supply attrition", 0.0, 0.2, 0.015, 0.005)
        with cost_tab:
            productivity = slider("Productivity index", 0.1, 2.0, 1.0, 0.05)
            monthly_cost = number("Monthly labour cost per employee", 0.0, 1000000.0, 5000.0, step=500.0)
        return {"workforce": workforce, "demand": demand, "months": months, "growth": growth,
                "turnover": turnover, "productivity": productivity, "monthly_cost": monthly_cost}

    if module == "Compensation & Benefits":
        pay, rewards = st.tabs(["Pay structure", "Rewards & benefits"])
        with pay:
            employees = number("Employees in scope", 1, 100000, 500)
            salary = number("Average annual base salary", 10000.0, 1000000.0, 60000.0, step=5000.0)
            spread = slider("Salary variation (standard deviation)", 1000, 200000, 15000, 1000)
        with rewards:
            increment = slider("Annual salary increment", 0.0, 0.3, 0.04, 0.01)
            bonus = slider("Bonus as share of salary", 0.0, 0.5, 0.05, 0.01)
            benefits = slider("Benefits as share of salary", 0.0, 0.5, 0.12, 0.01)
        return {"employees": employees, "salary": salary, "spread": spread, "increment": increment,
                "bonus": bonus, "benefits": benefits}

    volume, capacity_tab = st.tabs(["Grievance volume", "Resolution capacity"])
    with volume:
        employees = number("Employees in scope", 1, 100000, 500)
        grievance_rate = slider("Monthly grievance rate per employee", 0.0, 0.2, 0.025, 0.005)
    with capacity_tab:
        capacity = slider("HR case capacity (parallel cases)", 1, 100, 8)
        resolution_days = slider("Average resolution time (days)", 1.0, 90.0, 12.0, 1.0)
    return {"employees": employees, "grievance_rate": grievance_rate,
            "capacity": capacity, "resolution_days": resolution_days}


def chart_result(module: str, series: list[dict]):
    if module == "Recruitment & Talent Acquisition":
        fig = go.Figure(go.Funnel(y=[row["Stage"] for row in series], x=[row["Count"] for row in series],
                                  textinfo="value+percent previous"))
        fig.update_layout(title="Recruitment funnel")
    elif module == "Employee Attrition & Retention":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[row["Month"] for row in series], y=[row["Workforce"] for row in series],
                                 mode="lines+markers", name="Workforce"))
        fig.add_trace(go.Bar(x=[row["Month"] for row in series], y=[row["Exits"] for row in series],
                             name="Exits", opacity=0.45, yaxis="y2"))
        fig.update_layout(title="Workforce and monthly exits", xaxis_title="Month",
                          yaxis=dict(title="Workforce"), yaxis2=dict(title="Exits", overlaying="y", side="right"))
    elif module == "Learning & Development":
        fig = go.Figure(go.Bar(x=[row["Method"] for row in series],
                               y=[row["Completion (%)"] for row in series], text=[row["Completion (%)"] for row in series]))
        fig.update_layout(title="Illustrative completion by training method", yaxis_title="Completion (%)", yaxis_range=[0, 100])
    elif module == "Performance Management":
        fig = go.Figure(go.Bar(x=[row["Rating"] for row in series], y=[row["Employees"] for row in series]))
        fig.update_layout(title="Simulated performance rating distribution", xaxis_title="Rating", yaxis_title="Employees")
    elif module == "Workforce Planning":
        months = [row["Month"] for row in series]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=[row["Workforce Supply"] for row in series],
                                 name="Workforce Supply", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=months, y=[row["Workforce Demand"] for row in series],
                                 name="Workforce Demand", mode="lines+markers"))
        fig.update_layout(title="Forecast workforce supply vs demand", xaxis_title="Month", yaxis_title="Employees")
    elif module == "Compensation & Benefits":
        fig = go.Figure(go.Histogram(x=[row["Salary"] for row in series], nbinsx=25))
        fig.update_layout(title="Simulated salary distribution", xaxis_title="Salary", yaxis_title="Employees")
    else:
        fig = go.Figure(go.Bar(x=[row["Category"] for row in series], y=[row["Grievances"] for row in series]))
        fig.update_layout(title="Illustrative grievance categories", xaxis_title="Category", yaxis_title="Grievances")
    return styled_chart(fig)


def render_module(module: str) -> None:
    descriptions = {
        "Recruitment & Talent Acquisition": ("Explore funnel conversion, hiring capacity and cost per hire.",
            "Learning objectives: interpret selection ratios and identify bottlenecks in sourcing, screening and offers."),
        "Employee Attrition & Retention": ("Explore how assumed monthly exits and replacement hiring affect workforce size.",
            "Learning objectives: distinguish monthly from annualized attrition and estimate replacement costs."),
        "Learning & Development": ("Estimate training participation, completion, learning gains and illustrative ROI.",
            "Learning objectives: connect participation and learning transfer to workforce outcomes."),
        "Performance Management": ("Explore rating distributions and the implications of development interventions.",
            "Learning objectives: interpret score distributions; this tool does not make employment decisions."),
        "Workforce Planning": ("Forecast headcount demand and supply under growth and attrition assumptions.",
            "Learning objectives: quantify staffing gaps, utilization and a simplified labour-cost forecast."),
        "Compensation & Benefits": ("Model total compensation cost from base pay and configurable reward assumptions.",
            "Learning objectives: understand the budget impact of increments, bonus and benefits."),
        "Employee Relations": ("Explore the effect of grievance volume and HR case capacity on resolution backlogs.",
            "Learning objectives: interpret resolution rate and pending cases; no disciplinary decisions are automated."),
    }
    page_header(module, descriptions[module][0], "PEOPLE ANALYTICS • SIMULATION")
    st.markdown(
        '<div class="status-row"><span class="status-pill">◉ LIVE PARAMETER PREVIEW</span>'
        '<span class="status-pill">▣ SYNTHETIC / ILLUSTRATIVE</span>'
        '<span class="status-pill">⌂ LOCAL SESSION</span></div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown("#### Simulation controls")
        st.caption(descriptions[module][1])
        params = module_parameters(module)
        seed = int(st.number_input("Random seed", min_value=0, max_value=2147483647,
                                   value=int(st.session_state.random_seed),
                                   key=control_key(module, "Random seed")))
        preview = run_simulation(module, params, seed)

        if module == "Recruitment & Talent Acquisition":
            values = kpi_values(preview)
            recruitment_cards = [
                {"KPI": "Vacancies", "Value": params["vacancies"]},
                {"KPI": "Applicants", "Value": params["applicants"]},
                {"KPI": "Expected hires", "Value": values["Employees Joined"]},
                {"KPI": "Time to hire (days)", "Value": values["Estimated Time to Fill (days)"]},
                {"KPI": "Cost per hire", "Value": values["Cost per Hire"]},
                {"KPI": "Selection ratio", "Value": f"{values['Recruitment Conversion (%)']:.1f}%"},
            ]
            show_kpis(recruitment_cards, per_row=3)
        else:
            highlights = {
                "Employee Attrition & Retention": ["Final Workforce", "Annualized Attrition Rate (%)",
                                                     "Estimated Replacement Cost", "Retention Rate (%)"],
                "Learning & Development": ["Enrolled", "Training Completion Rate (%)",
                                           "Estimated Training ROI (%)", "Training Cost"],
                "Performance Management": ["Average Performance Score After Intervention",
                                          "Goal Achievement Rate (%)", "High Performer Share (%)",
                                          "Employees Requiring Support (%)"],
                "Workforce Planning": ["Forecast Workforce Supply", "Forecast Workforce Demand",
                                       "Workforce Gap", "Hiring Requirement"],
                "Compensation & Benefits": ["Average Salary", "Total Compensation Cost",
                                            "Increment Cost", "Benefits Cost"],
                "Employee Relations": ["Total Grievances", "Resolved in Period",
                                       "Pending Grievances", "Resolution Rate (%)"],
            }[module]
            values = kpi_values(preview)
            show_kpis([{"KPI": key, "Value": values[key]} for key in highlights])

        action_cols = st.columns([1.15, 1.35, 1, 1.5])
        run = action_cols[0].button("Run simulation", type="primary", width="stretch",
                                    key=f"run_{MODULES[module]}")
        real_time = action_cols[1].button("Real-time simulation", width="stretch",
                                          key=f"realtime_{MODULES[module]}")
        reset = action_cols[2].button("Reset", width="stretch", key=f"reset_{MODULES[module]}")
        save_name = action_cols[3].text_input("Scenario name", value=f"{MODULES[module].title()} baseline",
                                             key=f"name_{MODULES[module]}")
        if reset:
            st.session_state.control_epoch[module] = st.session_state.control_epoch.get(module, 0) + 1
            st.session_state.latest_results.pop(module, None)
            st.rerun()

        if run or real_time:
            stored = dict(preview)
            stored.update({"params": dict(params), "seed": seed, "module": module,
                           "timestamp": datetime.now().isoformat(timespec="seconds")})
            st.session_state.latest_results[module] = stored
            if real_time:
                progress = st.progress(0, text="Starting simulation")
                status = st.empty()
                stages = ["Configure scenario", "Process workforce events", "Calculate outcomes", "Render analysis"]
                for step, label in enumerate(stages, start=1):
                    status.write(label)
                    progress.progress(step / len(stages), text=label)
                    time.sleep(0.18)
                progress.empty()
                status.success("Simulation completed")

        save = st.button("Save scenario", width="stretch", key=f"save_{MODULES[module]}")
        if save:
            if len(st.session_state.scenarios) >= 5:
                st.warning("The scenario library is limited to five. Remove a saved scenario before adding another.")
            else:
                saved = dict(preview)
                saved.update({"params": dict(params), "seed": seed, "module": module,
                              "timestamp": datetime.now().isoformat(timespec="seconds"),
                              "name": save_name.strip() or module})
                st.session_state.scenarios.append(saved)
                st.success("Scenario saved for comparison.")

    st.markdown("#### Results & decision support")
    if module == "Recruitment & Talent Acquisition":
        funnel_tab, capacity_tab, insight_tab = st.tabs(["Funnel & conversion", "Capacity & cost", "Manager insights"])
        with funnel_tab:
            left, right = st.columns(2)
            with left:
                st.plotly_chart(chart_result(module, preview["series"]), width="stretch")
            with right:
                stages = preview["series"]
                labels = [f"{stages[i]['Stage']} → {stages[i + 1]['Stage']}" for i in range(len(stages) - 1)]
                conversion_rates = [100 * stages[i + 1]["Count"] / max(1, stages[i]["Count"])
                                    for i in range(len(stages) - 1)]
                conversion_fig = go.Figure(go.Bar(x=labels, y=conversion_rates,
                                                  text=[f"{rate:.1f}%" for rate in conversion_rates],
                                                  textposition="auto"))
                conversion_fig.update_layout(title="Candidate conversion by stage", yaxis_title="Conversion (%)",
                                             yaxis_range=[0, 100], xaxis_tickangle=-18)
                st.plotly_chart(styled_chart(conversion_fig), width="stretch")
        with capacity_tab:
            values = kpi_values(preview)
            left, right = st.columns(2)
            with left:
                workload = params["applicants"] / max(1, params["recruiters"])
                workload_fig = go.Figure(go.Indicator(
                    mode="number+gauge", value=workload, title={"text": "Applicants per recruiter"},
                    gauge={"axis": {"range": [0, max(100, workload * 1.25)],
                                    "tickcolor": THEME["muted"]},
                           "bar": {"color": THEME["primary"]},
                           "bgcolor": THEME["card_bg"], "bordercolor": THEME["border"]},
                ))
                workload_fig.update_layout(title="Recruiter workload", height=300)
                st.plotly_chart(styled_chart(workload_fig), width="stretch")
            with right:
                hiring_fig = go.Figure(go.Bar(
                    x=["Vacancies", "Expected hires"], y=[params["vacancies"], values["Employees Joined"]],
                    marker_color=[CHART_COLORS[0], CHART_COLORS[1]],
                    text=[params["vacancies"], values["Employees Joined"]],
                    textposition="outside", textfont={"color": THEME["text_light"]},
                ))
                hiring_fig.update_layout(title="Hiring outcomes", yaxis_title="Candidates")
                st.plotly_chart(styled_chart(hiring_fig), width="stretch")
            costs = [
                {"KPI": "Recruitment budget", "Value": f"{params['budget']:,.2f}"},
                {"KPI": "Cost per hire", "Value": f"{values['Cost per Hire']:,.2f}"},
                {"KPI": "Screening capacity", "Value": f"{params['screen_capacity'] * params['recruiters']:,}"},
                {"KPI": "Applicants / recruiter", "Value": f"{workload:,.1f}"},
            ]
            render_table(["Cost & capacity measure", "Value"], [[row["KPI"], row["Value"]] for row in costs])
            efficiency = go.Figure(go.Indicator(
                mode="gauge+number", value=values["Hiring Target Attainment (%)"],
                title={"text": "Hiring target attainment"},
                gauge={"axis": {"range": [0, 100], "tickcolor": THEME["muted"]},
                       "bar": {"color": THEME["accent"]},
                       "steps": [{"range": [0, 60], "color": THEME["card_bg"]},
                                 {"range": [60, 85], "color": THEME["panel"]},
                                 {"range": [85, 100], "color": THEME["secondary"]}]},
            ))
            efficiency.update_layout(height=280)
            st.plotly_chart(styled_chart(efficiency), width="stretch")
        with insight_tab:
            render_insights(module, params, preview)
    else:
        results_tab, insight_tab = st.tabs(["Simulation results", "Manager insights"])
        with results_tab:
            left, right = st.columns([1.5, 1])
            with left:
                st.plotly_chart(chart_result(module, preview["series"]), width="stretch")
            with right:
                render_table(["KPI", "Value"], [[row["KPI"], row["Value"]] for row in preview["kpis"]])
        with insight_tab:
            render_insights(module, params, preview)
    st.download_button("Download module results (CSV)", records_to_csv(preview["kpis"]),
                       file_name=f"{MODULES[module]}_results.csv", mime="text/csv")


def render_department_editor() -> tuple[list[str], list[int]]:
    entries = []
    with st.expander("Edit workforce distribution", expanded=False):
        st.caption("Enter one row per department. The dashboard chart and total employee count update immediately.")
        if st.button("Add department", key="add_department"):
            department_id = st.session_state.next_department_id
            st.session_state.department_rows.append({
                "id": department_id, "name": f"Department {department_id}", "employees": 0,
            })
            st.session_state.next_department_id += 1
            st.rerun()

        for row in list(st.session_state.department_rows):
            name_col, count_col, remove_col = st.columns([2, 1, .7])
            name = name_col.text_input(
                "Department name", value=row["name"], key=f"department_name_{row['id']}",
            )
            count = count_col.number_input(
                f"Employees in department {row['id']}", min_value=0, step=1,
                value=int(row["employees"]), key=f"department_count_{row['id']}",
            )
            if remove_col.button("Remove", key=f"remove_department_{row['id']}"):
                st.session_state.department_rows = [
                    item for item in st.session_state.department_rows if item["id"] != row["id"]
                ]
                st.rerun()
            entries.append((name.strip(), int(count)))

    totals: dict[str, tuple[str, int]] = {}
    for name, count in entries:
        if not name:
            continue
        key = name.casefold()
        if key in totals:
            display_name, total = totals[key]
            totals[key] = (display_name, total + count)
        else:
            totals[key] = (name, count)
    return [item[0] for item in totals.values()], [item[1] for item in totals.values()]


def render_home() -> None:
    page_header("People analytics, in motion.",
                "A decision workspace to test workforce assumptions, compare outcomes and learn from the trade-offs.")
    st.markdown(
        '<div class="status-row"><span class="status-pill">✦ OFFLINE-FIRST DECISION LAB</span>'
        '<span class="status-pill">SYNTHETIC DATA • ILLUSTRATIVE</span></div>',
        unsafe_allow_html=True,
    )
    st.warning("Illustrative scenarios are learning tools—not factual assessments or individual predictions.")
    rng = np.random.default_rng(42)
    departments, department_counts = render_department_editor()
    employees = sum(department_counts)
    attrition_demo = run_simulation("Employee Attrition & Retention", {
        "workforce": employees, "months": 12, "voluntary": 0.012, "involuntary": 0.004,
        "retirement": 0.002, "hires": 10, "replacement_cost": 12000,
    }, 42)
    learning_demo = run_simulation("Learning & Development", {
        "employees": employees, "budget": 50000, "cost_per_person": 500, "participation": 0.7,
        "completion": 0.82, "pass_rate": 0.75, "learning_gain": 1.2, "value_per_gain": 150,
    }, 42)
    workforce_demo = run_simulation("Workforce Planning", {
        "workforce": employees, "demand": 460, "months": 12, "growth": 0.005, "turnover": 0.01,
        "productivity": 0.91, "monthly_cost": 5000,
    }, 42)
    recruitment_demo = run_simulation("Recruitment & Talent Acquisition", {
        "vacancies": 50, "applicants": 250, "recruiters": 6, "interviewers": 10,
        "screen_capacity": 250, "budget": 75000, "screen_rate": .8, "shortlist_rate": .35,
        "dropout_rate": .1, "offer_rate": .9, "acceptance_rate": .75, "joining_rate": .9,
        "screen_days": .5, "interview_days": 1,
    }, 42)
    demo_values = {row["KPI"]: row["Value"] for row in attrition_demo["kpis"]}
    learning_values = {row["KPI"]: row["Value"] for row in learning_demo["kpis"]}
    workforce_values = {row["KPI"]: row["Value"] for row in workforce_demo["kpis"]}
    recruitment_values = {row["KPI"]: row["Value"] for row in recruitment_demo["kpis"]}
    dashboard_metrics = [
        ("Total employees", f"{employees:,}"),
        ("Annualized attrition", f"{demo_values['Annualized Attrition Rate (%)']}%"),
        ("Open positions", f"{max(0, recruitment_values['Vacancies'] - recruitment_values['Employees Joined']):,}"),
        ("Avg. time to hire", f"{recruitment_values['Estimated Time to Fill (days)']} days"),
        ("Training completion", f"{learning_values['Training Completion Rate (%)']}%"),
        ("Workforce productivity", f"{workforce_values['Productivity Index']}%"),
    ]
    for row_start in (0, 3):
        metric_cols = st.columns(3)
        for column, (label, value) in zip(metric_cols, dashboard_metrics[row_start:row_start + 3]):
            column.metric(label, value)

    st.markdown("#### Workforce overview")
    left, right = st.columns(2)
    attrition_series = attrition_demo["series"]
    hires_exits = go.Figure()
    hires_exits.add_trace(go.Scatter(x=[row["Month"] for row in attrition_series],
                                    y=[row["Hires"] for row in attrition_series],
                                    name="Hires", mode="lines+markers"))
    hires_exits.add_trace(go.Scatter(x=[row["Month"] for row in attrition_series],
                                    y=[row["Exits"] for row in attrition_series],
                                    name="Exits", mode="lines+markers"))
    hires_exits.update_layout(title="Illustrative monthly hires and exits", xaxis_title="Month", yaxis_title="Employees")
    left.plotly_chart(styled_chart(hires_exits), width="stretch")
    if departments and sum(department_counts):
        slice_colors = [CHART_COLORS[index % len(CHART_COLORS)]
                        for index in range(len(departments))]
        distribution_fig = go.Figure(go.Pie(
            labels=departments, values=department_counts, hole=.58, textinfo="label+percent",
            textposition="outside", marker={"colors": slice_colors},
            textfont={"color": THEME["text_light"]},
            hovertemplate="%{label}: %{value} employees (%{percent})<extra></extra>",
        ))
        distribution_fig.update_layout(title="Workforce distribution by department")
        right.plotly_chart(styled_chart(distribution_fig), width="stretch")
        right.caption(f"{employees:,} employees across {len(departments)} departments · based on your inputs.")
    else:
        right.info("Add department names and employee counts to display the workforce distribution.")

    st.markdown("#### Talent performance")
    left, right = st.columns(2)
    left.plotly_chart(styled_chart(chart_result("Recruitment & Talent Acquisition",
                                                recruitment_demo["series"])),
                      width="stretch")
    department_performance = rng.normal(3.25, .22, len(departments)).clip(1, 5)
    performance_fig = go.Figure(go.Bar(x=departments, y=department_performance,
                                       marker_color=THEME["primary"], text=[f"{v:.2f}" for v in department_performance],
                                       textposition="auto"))
    performance_fig.update_layout(title="Illustrative department performance",
                                  xaxis_title="Department", yaxis_title="Average rating (1–5)",
                                  yaxis_range=[0, 5])
    right.plotly_chart(styled_chart(performance_fig), width="stretch")

    st.markdown("#### Recent simulation activity")
    activity = sorted(st.session_state.latest_results.values(),
                      key=lambda result: result["timestamp"], reverse=True)
    if activity:
        rows = [[item["timestamp"], item["module"], item["seed"],
                 next((row["Value"] for row in item["kpis"] if row["KPI"] in
                       ("Employees Joined", "Final Workforce", "Total Compensation Cost",
                        "Training Completion Rate (%)", "Pending Grievances")), "—")]
                for item in activity[:6]]
        render_table(["Run time", "Module", "Seed", "Headline outcome"], rows)
    else:
        st.caption("No runs yet. Open a module from the sidebar and run a simulation to see it here.")


CASE_STUDIES = {
    "Recruitment crisis": ("50 vacancies with insufficient hiring capacity.", "Add recruiter capacity and improve interview availability."),
    "Attrition crisis": ("Rising voluntary turnover is increasing replacement costs.", "Test engagement and retention measures by reducing the assumed exit rate."),
    "Training failure": ("Employees complete training but do not apply new skills.", "Compare participation, completion and learning-gain assumptions."),
    "Performance crisis": ("A low average performance score is affecting productivity.", "Explore targeted development rather than automated employment decisions."),
    "Workforce shortage": ("Forecast demand exceeds available workforce.", "Compare recruitment, retention and productivity assumptions."),
    "Compensation crisis": ("Salary expectations rise while the budget is constrained.", "Model increments and benefits against total compensation cost."),
    "Employee relations crisis": ("Grievance volume and resolution delays are creating a backlog.", "Increase case capacity or reduce average resolution time."),
}


def render_decision_lab() -> None:
    st.title("HR Manager Decision Lab")
    st.caption("Educational case studies with transparent, illustrative scoring—not professional performance assessment.")
    case = st.selectbox("Choose a case study", list(CASE_STUDIES), key="decision_case")
    problem, approach = CASE_STUDIES[case]
    st.markdown(f"### Business problem\n{problem}")
    st.write("Suggested model approach:", approach)
    selected_module = {
        "Recruitment crisis": list(MODULES)[0], "Attrition crisis": list(MODULES)[1],
        "Training failure": list(MODULES)[2], "Performance crisis": list(MODULES)[3],
        "Workforce shortage": list(MODULES)[4], "Compensation crisis": list(MODULES)[5],
        "Employee relations crisis": list(MODULES)[6],
    }[case]
    st.info(f"Use the **{selected_module}** navigation page to adjust decisions and run the relevant simulation.")
    desired = st.multiselect("Decision principles applied", ["Evidence-based", "Considers employee wellbeing",
                             "Budget-aware", "Checks unintended consequences", "Uses appropriate safeguards"])
    score = round(100 * len(desired) / 5)
    st.metric("Transparent learning checklist score", f"{score}/100")
    st.caption("One point per selected principle. This checklist is educational and does not rate HR professionals.")


def render_scenarios() -> None:
    st.title("Scenario Comparison")
    scenarios = st.session_state.scenarios
    st.caption(f"{len(scenarios)} of 5 scenarios saved in the current browser session.")
    if not scenarios:
        st.info("Run a module and choose “Save current result to scenario comparison” to add a scenario.")
        return
    labels = [f"{i + 1}. {s['name']} — {s['module']}" for i, s in enumerate(scenarios)]
    selected = st.multiselect("Scenarios to compare", labels, default=labels[:min(3, len(labels))])
    if st.button("Clear all saved scenarios"):
        st.session_state.scenarios = []
        st.rerun()
    chosen = [s for label, s in zip(labels, scenarios) if label in selected]
    if chosen:
        comparison_rows = []
        for scenario in chosen:
            comparison_rows.extend([[scenario["name"], row["KPI"], row["Value"]]
                                    for row in scenario["kpis"]])
        render_table(["Scenario", "KPI", "Value"], comparison_rows)
        if len({scenario["module"] for scenario in chosen}) == 1:
            metric_names = list(dict.fromkeys(row[1] for row in comparison_rows
                                               if isinstance(row[2], (int, float, np.number))))
            fig = go.Figure()
            for scenario in chosen:
                values = {row["KPI"]: row["Value"] for row in scenario["kpis"]}
                fig.add_trace(go.Bar(name=scenario["name"], x=metric_names,
                                     y=[values.get(metric, 0) for metric in metric_names]))
            fig.update_layout(title="Comparable scenario KPIs", barmode="group")
            st.plotly_chart(styled_chart(fig), width="stretch")
        elif comparison_rows:
            st.caption("Chart comparison is shown only when scenarios share a module; the KPI table above remains available across modules.")
        st.download_button("Download comparison (CSV)",
                           rows_to_csv(["Scenario", "KPI", "Value"], comparison_rows),
                           "scenario_comparison.csv", "text/csv")


def render_data_management() -> None:
    st.title("Data Management")
    st.info("Files are processed in this local Streamlit session; no employee data is sent to external services.")
    upload = st.file_uploader("Upload CSV or Excel data", type=["csv", "xlsx"])
    if upload is not None:
        try:
            content = upload.getvalue()
            if upload.name.lower().endswith(".csv"):
                parsed = list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))
            else:
                workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
                worksheet = workbook.active
                parsed = [list(row) for row in worksheet.iter_rows(values_only=True)]
                workbook.close()
            if not parsed:
                raise ValueError("The uploaded file contains no rows.")
            headers = [str(value) if value is not None else f"Column {index + 1}"
                       for index, value in enumerate(parsed[0])]
            data_rows = [row + [None] * (len(headers) - len(row)) for row in parsed[1:]]
            data_rows = [row[:len(headers)] for row in data_rows]
            st.session_state.uploaded_data = {"columns": headers, "rows": data_rows}
        except (ValueError, OSError, UnicodeDecodeError, csv.Error, zipfile.BadZipFile,
                InvalidFileException) as error:
            st.error(f"Could not read the uploaded file: {error}")
            return
        st.success(f"Loaded {len(data_rows):,} rows and {len(headers):,} columns. This data is not silently mapped to a simulation.")
    data = st.session_state.uploaded_data
    if data is not None:
        st.subheader("Preview")
        headers = data["columns"]
        rows = data["rows"]
        render_table(headers, rows[:20])
        missing = [sum(value is None or value == "" for value in (row[index] for row in rows))
                   for index in range(len(headers))]
        duplicate_rows = len(rows) - len({tuple(str(value) for value in row) for row in rows})
        validation_rows = []
        for index, column in enumerate(headers):
            values = [row[index] for row in rows if row[index] is not None and row[index] != ""]
            if not values:
                data_type = "empty"
            elif all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
                data_type = "numeric"
            else:
                data_type = "mixed/text"
            validation_rows.append([column, data_type, missing[index]])
        st.subheader("Validation report")
        st.write(f"Duplicate rows: **{duplicate_rows:,}** · Missing cells: **{sum(missing):,}**")
        render_table(["Column", "Data type", "Missing values"], validation_rows)
        st.download_button("Download validation report",
                           rows_to_csv(["Column", "Data type", "Missing values"], validation_rows),
                           "validation_report.csv", "text/csv")
        st.download_button("Download uploaded data as CSV", rows_to_csv(headers, rows),
                           "data_export.csv", "text/csv")
        st.caption("Column mappings are intentionally explicit: review the preview and align the uploaded columns with the module inputs before using the data.")
    else:
        st.write("Synthetic datasets and module-level parameter controls are available without uploading a file.")


def render_recommendations() -> None:
    st.title("AI Recommendations")
    st.caption("Offline rule-based recommendations with an explanation. No external AI or employee-level risk scoring.")
    if not st.session_state.latest_results:
        st.info("Run a module simulation to receive recommendations based on its outputs.")
        return
    for module, result in st.session_state.latest_results.items():
        values = {row["KPI"]: row["Value"] for row in result["kpis"]}
        st.subheader(module)
        advice = []
        if module == "Employee Attrition & Retention" and values.get("Annualized Attrition Rate (%)", 0) > 15:
            advice.append("Review workload, engagement, career growth and compensation; annualized attrition exceeds the illustrative 15% threshold.")
        if module == "Recruitment & Talent Acquisition" and values.get("Estimated Time to Fill (days)", 0) > 30:
            advice.append("Review recruiter capacity and interview scheduling; estimated time to fill is above 30 days.")
        if module == "Learning & Development" and values.get("Training Completion Rate (%)", 0) < 70:
            advice.append("Investigate scheduling, relevance and manager support; simulated completion is below 70%.")
        if module == "Workforce Planning" and values.get("Workforce Gap", 0) < 0:
            advice.append(f"Forecast supply is below demand by {abs(int(values['Workforce Gap']))} employees; assess hiring, internal mobility and productivity.")
        if module == "Employee Relations" and values.get("Pending Grievances", 0) > 0:
            advice.append("Review case capacity and resolution processes; pending grievances remain in the simulation.")
        if module == "Compensation & Benefits":
            advice.append("Compare simulated total compensation against a validated market benchmark before making budget decisions.")
        if module == "Performance Management":
            advice.append("Use results to plan coaching and development; never treat simulated ratings as individual employee facts.")
        st.write("\n".join(f"- {item}" for item in advice) if advice else "No threshold-based alert for this illustrative result. Review assumptions and context.")


def render_reports() -> None:
    st.title("Reports & Exports")
    results = list(st.session_state.latest_results.values())
    if not results:
        st.info("Run at least one simulation to build a report.")
        return
    options = [f"{r['module']} — {r['timestamp']}" for r in results]
    selected_index = options.index(st.selectbox("Select a simulation", options))
    report = results[selected_index]
    st.subheader(report["module"])
    st.write(f"Simulation time: {report['timestamp']} · Random seed: {report['seed']}")
    st.write("Objective: explore the effect of configurable HR assumptions using an illustrative simulation.")
    render_table(["KPI", "Value"], [[row["KPI"], row["Value"]] for row in report["kpis"]])
    csv_bytes = records_to_csv(report["kpis"])
    st.download_button("Download KPI report (CSV)", csv_bytes, "hr_simulation_report.csv", "text/csv")
    excel = BytesIO()
    workbook = Workbook()
    kpi_sheet = workbook.active
    kpi_sheet.title = "KPIs"
    kpi_sheet.append(["KPI", "Value"])
    for row in report["kpis"]:
        kpi_sheet.append([row["KPI"], row["Value"]])
    series_sheet = workbook.create_sheet("Simulation Data")
    series = report["series"]
    series_columns = list(series[0]) if series else []
    if series_columns:
        series_sheet.append(series_columns)
        for row in series:
            series_sheet.append([row.get(column) for column in series_columns])
    inputs_sheet = workbook.create_sheet("Inputs")
    inputs_sheet.append(["Input", "Value"])
    for key, value in report["params"].items():
        inputs_sheet.append([key, value])
    workbook.save(excel)
    st.download_button("Download report (Excel)", excel.getvalue(), "hr_simulation_report.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet

        pdf_buffer = BytesIO()
        document = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        styles["Title"].textColor = colors.HexColor("#0F172A")
        styles["Normal"].textColor = colors.HexColor("#334155")
        styles["Heading2"].textColor = colors.HexColor("#1D4ED8")
        styles["BodyText"].textColor = colors.HexColor("#0F172A")
        table_data = [["KPI", "Value"]] + [[str(row["KPI"]), str(row["Value"])] for row in report["kpis"]]
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D4ED8")),
                                   ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#FFFFFF")),
                                   ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#0F172A")),
                                   ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                                   ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                                    [colors.HexColor("#EFF6FF"), colors.HexColor("#FFFFFF")])]))
        report_content = [Paragraph("HR SIMULATE — Simulation Report", styles["Title"]),
                          Paragraph(f"{report['module']} · {report['timestamp']}", styles["Normal"]),
                          Spacer(1, 14), Paragraph("Inputs", styles["Heading2"]),
                          Paragraph(str(report["params"]), styles["BodyText"]),
                          Spacer(1, 14), Paragraph("Key outcomes", styles["Heading2"]), table,
                          Spacer(1, 14), Paragraph("Limitations: illustrative simulation based on stated assumptions; not a prediction or decision about an individual.", styles["BodyText"])]
        def draw_report_background(canvas, _document):
            canvas.saveState()
            canvas.setFillColor(colors.HexColor("#FFFFFF"))
            canvas.rect(0, 0, letter[0], letter[1], stroke=0, fill=1)
            canvas.restoreState()

        document.build(report_content, onFirstPage=draw_report_background, onLaterPages=draw_report_background)
        st.download_button("Download report (PDF)", pdf_buffer.getvalue(), "hr_simulation_report.pdf", "application/pdf")
    except ImportError:
        st.caption("PDF export requires ReportLab. CSV and Excel exports are available.")


def render_documentation() -> None:
    st.title("Settings & Documentation")
    st.subheader("Simulation methodology")
    st.markdown(
        """
        - **Attrition:** monthly exits are sampled from the configured combined exit probability; the annualized rate compounds the simulated monthly rate.
        - **Recruitment:** counts flow through a configurable funnel; estimated time-to-fill reflects screening and interview effort divided by available capacity.
        - **Learning:** participation, completion and assessment outcomes are sequential rates; ROI uses the entered estimated value per learning point.
        - **Performance:** ratings are reproducibly sampled from a clipped normal distribution; this is not an individual prediction.
        - **Workforce planning:** headcount demand and supply are compounded over the forecast horizon using stated growth and attrition assumptions.
        - **Compensation:** salaries are reproducibly sampled and clipped to a plausible range, then adjusted by the entered reward percentages.
        - **Employee relations:** grievance volume is sampled from a Poisson model; available monthly throughput is limited by parallel capacity and resolution time.

        **Glossary:** Attrition — employees leaving during a period; time to fill — estimated duration to fill a vacancy; training ROI — estimated net return divided by training cost; workforce gap — supply minus demand.

        All outputs are educational estimates. Validate assumptions and applicable policies before real-world use. This application does not make hiring, firing, promotion, compensation, or disciplinary decisions.
        """
    )
    st.subheader("Session settings")
    st.number_input("Default random seed", min_value=0, max_value=2147483647, key="random_seed")
    st.write("Scenario data is retained in Streamlit session state for the current session only.")


if page == "Home Dashboard":
    render_home()
elif page in MODULES:
    render_module(page)
elif page == "HR Manager Decision Lab":
    render_decision_lab()
elif page == "Scenario Comparison":
    render_scenarios()
elif page == "Data Management":
    render_data_management()
elif page == "AI Recommendations":
    render_recommendations()
elif page == "Reports & Exports":
    render_reports()
else:
    render_documentation()

st.sidebar.markdown("---")
st.sidebar.caption("v1.0 · Offline-first educational simulation")

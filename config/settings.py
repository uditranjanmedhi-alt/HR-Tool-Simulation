"""Application-wide settings and theme configuration for HR SIMULATE."""

APP_NAME = "HR SIMULATE"
APP_TAGLINE = "Learn HR. Simulate Decisions. Analyse Outcomes. Improve Strategies."
APP_VERSION = "1.0.0"

THEME = {
    "primary": "#3B82F6",
    "secondary": "#14B8A6",
    "accent": "#38BDF8",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "bg_dark": "#0B1220",
    "bg_light": "#F8FAFC",
    "card_bg": "#111827",
    "panel": "#172033",
    "border": "#334155",
    "border_strong": "#475569",
    "muted": "#94A3B8",
    "text_light": "#F8FAFC",
    "text_dark": "#0F172A",
}

DEPARTMENTS = [
    "Human Resources", "Finance", "Engineering", "Marketing", "Sales",
    "Operations", "IT", "Legal", "Customer Service", "R&D",
]

JOB_LEVELS = ["Junior", "Mid-Level", "Senior", "Lead", "Manager", "Director", "VP", "C-Suite"]

EDUCATION_LEVELS = ["High School", "Bachelors", "Masters", "PhD"]

RECRUITMENT_SOURCES = [
    "Employee Referral", "Job Portal", "Recruitment Agency",
    "Campus Recruitment", "Internal Transfer", "Social Media", "Company Website",
]

TRAINING_METHODS = [
    "Classroom", "Online Learning", "Blended Learning",
    "On-the-Job Training", "Workshop", "Seminar", "Mentoring",
]

GRIEVANCE_CATEGORIES = [
    "Workplace Harassment", "Discrimination", "Compensation Dispute",
    "Work Conditions", "Management Issues", "Policy Violation",
    "Interpersonal Conflict", "Safety Concerns", "Workload", "Other",
]

PERFORMANCE_RATING_SCALE = {
    1: "Needs Improvement",
    2: "Below Expectations",
    3: "Meets Expectations",
    4: "Exceeds Expectations",
    5: "Outstanding",
}

SIMULATION_MODES = ["Instant Simulation", "Real-Time Animation", "Scenario Comparison"]

AI_PROVIDERS = [
    {"name": "OpenAI", "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]},
    {"name": "Google", "models": ["gemini-1.5-pro", "gemini-1.5-flash"]},
    {"name": "Anthropic", "models": ["claude-3-opus", "claude-3-sonnet"]},
]

PAGE_CONFIG = {
    "page_title": "HR SIMULATE – Decision Lab",
    "page_icon": "🏢",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

CHART_COLORS = [
    "#38BDF8", "#2DD4BF", "#A78BFA", "#FBBF24", "#FB7185", "#34D399",
]

CSS_STYLES = """
<style>
/* Global */
.main .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 1200px; }
h1 { color: #F8FAFC; font-weight: 700; }
h2 { color: #F8FAFC; font-weight: 600; border-bottom: 2px solid #334155; padding-bottom: 0.3rem; }
h3 { color: #F8FAFC; font-weight: 600; }

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #111827 0%, #172033 100%);
    border-radius: 12px; padding: 1.2rem 1rem; text-align: center;
    border-left: 4px solid #38BDF8; box-shadow: 0 4px 15px rgba(2, 6, 23, 0.35);
    margin-bottom: 0.8rem; transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-card .kpi-title {
    font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;
    letter-spacing: 0.5px; margin-bottom: 0.3rem;
}
.kpi-card .kpi-value {
    font-size: 1.8rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.2rem;
}
.kpi-card .kpi-delta { font-size: 0.85rem; }
.kpi-delta.positive { color: #34D399; }
.kpi-delta.negative { color: #FB7185; }
.kpi-delta.neutral  { color: #94A3B8; }

/* Summary Card */
.summary-card {
    background: #111827; border-radius: 10px; padding: 1.2rem;
    border: 1px solid #334155; margin-bottom: 1rem;
}
.summary-card h4 { color: #F8FAFC; margin-bottom: 0.5rem; }

/* Status Badge */
.status-badge {
    display: inline-block; padding: 0.2rem 0.7rem; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.3px;
}
.badge-success { background: #14532D; color: #DCFCE7; }
.badge-warning { background: #78350F; color: #FEF3C7; }
.badge-danger  { background: #7F1D1D; color: #FEE2E2; }
.badge-info    { background: #1E3A8A; color: #DBEAFE; }

/* Section Divider */
.section-divider {
    border: none; height: 2px;
    background: linear-gradient(90deg, #38BDF8, #14B8A6);
    margin: 1.5rem 0;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1220 0%, #111827 100%);
}
section[data-testid="stSidebar"] .stRadio > label {
    color: #F8FAFC; font-weight: 500;
}

/* Table */
.dataframe { font-size: 0.85rem; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0; padding: 8px 20px; font-weight: 500;
}

/* Metric Override */
[data-testid="stMetricValue"] { font-size: 1.6rem; }
[data-testid="stMetricLabel"] { font-size: 0.8rem; text-transform: uppercase; }

/* Expander */
.streamlit-expanderHeader { font-weight: 600; color: #38BDF8; }

/* Progress */
.stProgress > div > div > div { background-color: #38BDF8; }
</style>
"""

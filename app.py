from __future__ import annotations

import calendar
import csv
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st


TEAM_NAME = "Escalation & Digital"
TIMEZONE = ZoneInfo("Asia/Singapore")
DATA_FILE = Path(__file__).with_name("team_positions.csv")
TEAMS = ("Escalation", "Digital")


st.set_page_config(
    page_title="Team Position Tracker",
    page_icon="U0001f9ed",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def shift_month(source: date, offset: int) -> date:
    """Move a date by whole months, keeping the day valid."""
    month_index = source.year * 12 + source.month - 1 + offset
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    day = min(source.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def calculate_tenure(date_hired: date, as_of: date) -> tuple[int, int, int]:
    """Return completed years, months, and days between two dates."""
    years = as_of.year - date_hired.year
    if (as_of.month, as_of.day) < (date_hired.month, date_hired.day):
        years -= 1

    anniversary_year = date_hired.year + years
    anniversary_day = min(
        date_hired.day, calendar.monthrange(anniversary_year, date_hired.month)[1]
    )
    anniversary = date(anniversary_year, date_hired.month, anniversary_day)

    months = (as_of.year - anniversary.year) * 12 + as_of.month - anniversary.month
    month_mark = shift_month(anniversary, months)
    if month_mark > as_of:
        months -= 1
        month_mark = shift_month(anniversary, months)

    days = (as_of - month_mark).days
    return years, months, days


def tenure_text(years: int, months: int, days: int) -> str:
    parts = []
    for value, singular in ((years, "year"), (months, "month"), (days, "day")):
        if value:
            parts.append(f"{value} {singular if value == 1 else singular + 's'}")
    return ", ".join(parts) if parts else "Newly hired today"


def record_exists(record_month: str, full_name: str) -> bool:
    if not DATA_FILE.exists():
        return False
    with DATA_FILE.open("r", newline="", encoding="utf-8") as file:
        return any(
            row.get("month") == record_month and row.get("full_name") == full_name
            for row in csv.DictReader(file)
        )


def save_record(
    record_month: str,
    full_name: str,
    date_hired: date,
    tenure: str,
    bank: str,
    team: str,
) -> None:
    is_new_file = not DATA_FILE.exists()
    with DATA_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new_file:
            writer.writerow(
                [
                    "month",
                    "full_name",
                    "date_hired",
                    "tenure",
                    "bank",
                    "team",
                    "submitted_at",
                ]
            )
        writer.writerow(
            [
                record_month,
                full_name,
                date_hired.isoformat(),
                tenure,
                bank,
                team,
                datetime.now(TIMEZONE).isoformat(timespec="seconds"),
            ]
        )


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@700;800&display=swap');

        :root {
            --ink: #172137;
            --muted: #727b91;
            --purple: #6658d9;
            --blue: #3794d8;
            --mint: #39bca4;
        }

        html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }

        .stApp {
            color: var(--ink);
            background:
                radial-gradient(circle at 8% 10%, rgba(102, 88, 217, .16), transparent 26%),
                radial-gradient(circle at 91% 87%, rgba(57, 188, 164, .16), transparent 27%),
                linear-gradient(145deg, #fafaff, #f2f6fc 53%, #f6fbfa);
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            opacity: .32;
            background-image:
                linear-gradient(rgba(70, 80, 115, .06) 1px, transparent 1px),
                linear-gradient(90deg, rgba(70, 80, 115, .06) 1px, transparent 1px);
            background-size: 44px 44px;
            mask-image: linear-gradient(to bottom, black, transparent 82%);
        }

        header[data-testid="stHeader"] { background: transparent; }
        [data-testid="stMainBlockContainer"] { max-width: 780px; padding-top: 3rem; }

        .orb {
            position: fixed;
            z-index: 0;
            pointer-events: none;
            border-radius: 999px;
        }

        .orb-a {
            width: 190px;
            height: 190px;
            left: -70px;
            top: 15%;
            background: linear-gradient(135deg, rgba(102, 88, 217, .23), rgba(102, 88, 217, .03));
            animation: drift-a 11s ease-in-out infinite;
        }

        .orb-b {
            width: 235px;
            height: 235px;
            right: -90px;
            bottom: 7%;
            background: linear-gradient(135deg, rgba(57, 188, 164, .22), rgba(57, 188, 164, .03));
            animation: drift-b 14s ease-in-out infinite;
        }

        @keyframes drift-a {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(38px, 48px); }
        }

        @keyframes drift-b {
            0%, 100% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(-34px, -45px) scale(1.08); }
        }

        .eyebrow {
            margin-bottom: 1rem;
            color: var(--purple);
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .14em;
            text-align: center;
            text-transform: uppercase;
        }

        .hero-title {
            margin: 0;
            color: var(--ink);
            font-family: "Manrope", sans-serif;
            font-size: clamp(2rem, 7vw, 3.1rem);
            font-weight: 800;
            letter-spacing: -.055em;
            line-height: 1.06;
            text-align: center;
        }

        .hero-copy {
            max-width: 540px;
            margin: .85rem auto 2rem;
            color: var(--muted);
            font-size: .98rem;
            line-height: 1.6;
            text-align: center;
        }

        [data-testid="stForm"] {
            padding: 1.55rem 1.65rem 1.7rem;
            border: 1px solid rgba(255, 255, 255, .92);
            border-radius: 24px;
            background: rgba(255, 255, 255, .88);
            box-shadow: 0 24px 65px rgba(50, 59, 90, .12);
            backdrop-filter: blur(18px);
        }

        [data-testid="stWidgetLabel"] p {
            color: #3e4962;
            font-size: .87rem;
            font-weight: 700;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            min-height: 47px;
            border-color: #dfe3ee;
            border-radius: 12px;
            background: rgba(250, 251, 255, .94);
        }

        input[aria-label="Full name"], input[aria-label="Bank"] {
            text-transform: uppercase;
            letter-spacing: .03em;
        }

        .tenure-card {
            margin: .3rem 0 1rem;
            padding: .95rem 1rem;
            border: 1px solid rgba(102, 88, 217, .13);
            border-radius: 13px;
            background: linear-gradient(110deg, rgba(102, 88, 217, .08), rgba(57, 188, 164, .08));
        }

        .tenure-label {
            color: var(--muted);
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .tenure-value {
            margin-top: .25rem;
            color: var(--ink);
            font-family: "Manrope", sans-serif;
            font-size: 1.05rem;
            font-weight: 800;
        }

        [data-testid="stFormSubmitButton"] button {
            width: 100%;
            min-height: 50px;
            margin-top: .7rem;
            border: 0;
            border-radius: 13px;
            color: white;
            font-weight: 700;
            background: linear-gradient(105deg, var(--purple), var(--blue) 58%, var(--mint));
            box-shadow: 0 12px 25px rgba(102, 88, 217, .24);
            transition: transform .2s ease, box-shadow .2s ease;
        }

        [data-testid="stFormSubmitButton"] button:hover {
            color: white;
            border: 0;
            transform: translateY(-2px);
            box-shadow: 0 16px 30px rgba(102, 88, 217, .31);
        }

        [data-testid="stAlert"] { border-radius: 14px; margin-top: 1rem; }

        .footer-note {
            margin-top: 1.2rem;
            color: #8a92a6;
            font-size: .78rem;
            text-align: center;
        }

        @media (max-width: 640px) {
            [data-testid="stMainBlockContainer"] { padding: 2rem 1rem; }
            [data-testid="stForm"] { padding: 1.25rem 1.05rem 1.4rem; border-radius: 20px; }
        }

        @media (prefers-reduced-motion: reduce) {
            .orb { animation: none !important; }
        }
    </style>

    <div class="orb orb-a"></div>
    <div class="orb orb-b"></div>
    <div class="eyebrow">Escalation &amp; Digital</div>
    <h1 class="hero-title">Team Position<br>Tracker</h1>
    <p class="hero-copy">Keep team assignments, bank alignment, and employee tenure organized in one place.</p>
    """,
    unsafe_allow_html=True,
)


today = datetime.now(TIMEZONE).date()
month_options = [shift_month(today.replace(day=1), offset) for offset in range(-24, 4)]
current_month_index = month_options.index(today.replace(day=1))

with st.form("team_position_form", clear_on_submit=True):
    selected_month = st.selectbox(
        "Month",
        options=month_options,
        index=current_month_index,
        format_func=lambda value: value.strftime("%B %Y"),
    )

    full_name = st.text_input(
        "Full name", placeholder="FIRST NAME LAST NAME", max_chars=100
    )

    date_col, bank_col = st.columns(2, gap="medium")
    with date_col:
        date_hired = st.date_input(
            "Date hired",
            value=today,
            max_value=today,
            format="MM/DD/YYYY",
        )
    with bank_col:
        bank = st.text_input("Bank", placeholder="BANK NAME", max_chars=100)

    years, months, days = calculate_tenure(date_hired, today)
    calculated_tenure = tenure_text(years, months, days)
    st.markdown(
        f"""
        <div class="tenure-card">
            <div class="tenure-label">Automatic tenure as of {today.strftime('%B %d, %Y')}</div>
            <div class="tenure-value">{calculated_tenure}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    team = st.radio("Team", options=TEAMS, horizontal=True)
    submitted = st.form_submit_button("Save team position  →", use_container_width=True)


if submitted:
    clean_name = " ".join(full_name.split()).upper()
    clean_bank = " ".join(bank.split()).upper()
    record_month = selected_month.strftime("%Y-%m")

    if not clean_name:
        st.error("Please enter the employee's full name.", icon="⚠️")
    elif not clean_bank:
        st.error("Please enter the bank name.", icon="⚠️")
    elif date_hired > today:
        st.error("Date hired cannot be in the future.", icon="⚠️")
    elif record_exists(record_month, clean_name):
        st.warning(
            f"{clean_name} already has a record for {selected_month.strftime('%B %Y')}.",
            icon="⚠️",
        )
    else:
        save_record(
            record_month=record_month,
            full_name=clean_name,
            date_hired=date_hired,
            tenure=calculated_tenure,
            bank=clean_bank,
            team=team,
        )
        st.success(
            f"Saved {clean_name} under {team} with {calculated_tenure} of tenure.",
            icon="✅",
        )
        st.balloons()


st.markdown(
    '<p class="footer-note">Internal team position portal · Escalation &amp; Digital</p>',
    unsafe_allow_html=True,
)

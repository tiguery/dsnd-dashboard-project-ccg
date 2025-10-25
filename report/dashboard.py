# report/dashboard.py
from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path

# FastHTML imports
from fasthtml.common import fast_app, Div, H1, H2, P, Form, Label, Input, Button, Table, Tr, Th, Td, Br, Select, Option, Script, Img
import matplotlib.pyplot as plt
import io, base64

# Import package classes
from employee_events import Employee, Team
# Local utils
from .utils import load_model

app, rt = fast_app()
model = load_model()  # pre-load ML model once

def _img_from_plt() -> str:
    """Return a data URI for the current matplotlib figure."""
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"

def _line_chart(dates: List[str], pos: List[int], neg: List[int]) -> str:
    plt.figure()
    plt.plot(dates, pos, label="Positive")
    plt.plot(dates, neg, label="Negative")
    plt.legend()
    plt.xticks(rotation=45, ha="right")
    return _img_from_plt()

def _bar_chart(labels: List[str], values: List[float], title: str = "") -> str:
    plt.figure()
    plt.bar(labels, values)
    plt.title(title)
    return _img_from_plt()

def _predict_risk(example_features: Dict[str, float]) -> float:
    """
    Simple adapter: many baseline Udacity models expect a 2D array.
    We’ll feed [total_positive, total_negative, net] in that order if present.
    Falls back gracefully if the model has a different interface.
    """
    feats = [
        example_features.get("total_positive", 0.0),
        example_features.get("total_negative", 0.0),
        example_features.get("net", 0.0),
    ]
    try:
        # scikit-learn style
        proba = getattr(model, "predict_proba", None)
        if callable(proba):
            prob = proba([feats])[0]
            return float(prob[-1]) if hasattr(prob, "__iter__") else float(prob)
        pred = getattr(model, "predict", None)
        if callable(pred):
            out = pred([feats])[0]
            return float(out)
    except Exception:
        pass
    return 0.0

def _summary_table(headers: List[str], rows: List[List[Any]]):
    return Table(
        Tr(*[Th(h) for h in headers]),
        *[Tr(*[Td(str(c)) for c in r]) for r in rows]
    )

@app.get("/")
def index():
    return Div(
        H1("Employee/Team Performance Dashboard"),
        Form(
            Label("View: "),
            Select(
                Option("Employee", value="employee", selected=True),
                Option("Team", value="team"),
                name="view"
            ),
            Label(Br(), "ID: "),
            Input(type="number", name="entity_id", min="1", required=True),
            Br(),
            Button("Open", type="submit"),
            method="get", action="/route"
        ),
    )

@app.get("/route")
def route(view:str, entity_id:int):
    if view == "team":
        return team(entity_id)
    return employee(entity_id)

@app.get("/employee/{entity_id}")
def employee(entity_id:int):
    svc = Employee()
    prof = svc.profile(entity_id)
    ts = svc.timeseries(entity_id)
    notes = svc.notes(entity_id)

    # Build vectors for charts
    dates = [r["event_date"] for r in ts]
    pos = [int(r["positive_events"] or 0) for r in ts]
    neg = [int(r["negative_events"] or 0) for r in ts]

    total_pos = sum(pos)
    total_neg = sum(neg)
    net = total_pos - total_neg
    risk = _predict_risk({"total_positive": total_pos, "total_negative": total_neg, "net": net})
    risk_pct = f"{round(100*max(0.0, min(1.0, risk)), 1)}%"

    img_ts = _line_chart(dates, pos, neg)
    img_bar = _bar_chart(["Positive", "Negative", "Net"], [total_pos, total_neg, net], "Event Summary")

    return Div(
        H1("Employee Performance"),
        H2(prof.get("employee_name", f"Employee {entity_id}")),
        P(f"Team: {prof.get('team_name','N/A')}"),
        P(f"Recruitment Risk (predicted): {risk_pct}"),
        _summary_table(
            ["Total Positive", "Total Negative", "Net"],
            [[total_pos, total_neg, net]]
        ),
        Br(),
        H2("Time Series"),
        Img(src=img_ts, alt="time series"),
        Br(),
        H2("Event Summary"),
        Img(src=img_bar, alt="bar summary"),
        Br(),
        H2("Recent Notes"),
        _summary_table(["Date","Note"], [[n["note_date"], n["note"]] for n in notes[:10]]),
    )

@app.get("/team/{entity_id}")
def team(entity_id:int):
    svc = Team()
    prof = svc.profile(entity_id)
    ts = svc.timeseries(entity_id)
    roster = svc.roster(entity_id)
    notes = svc.notes(entity_id)

    dates = [r["event_date"] for r in ts]
    pos = [int(r["positive_events"] or 0) for r in ts]
    neg = [int(r["negative_events"] or 0) for r in ts]

    total_pos = sum(pos)
    total_neg = sum(neg)
    net = total_pos - total_neg

    # Average risk across employees (simple demo: average single-employee risk)
    # If you want a true average per-employee, loop per roster id and average predictions.
    risk = _predict_risk({"total_positive": total_pos, "total_negative": total_neg, "net": net})
    risk_pct = f"{round(100*max(0.0, min(1.0, risk)), 1)}%"

    img_ts = _line_chart(dates, pos, neg)
    img_bar = _bar_chart(["Positive", "Negative", "Net"], [total_pos, total_neg, net], "Team Summary")

    return Div(
        H1("Team Performance"),
        H2(prof.get("team_name", f"Team {entity_id}")),
        P(f"Shift: {prof.get('shift', 'N/A')} | Manager: {prof.get('manager_name', 'N/A')}"),
        P(f"Headcount: {prof.get('headcount', 'N/A')} | Avg Recruitment Risk (illustrative): {risk_pct}"),
        _summary_table(
            ["Total Positive", "Total Negative", "Net"],
            [[total_pos, total_neg, net]]
        ),
        Br(),
        H2("Time Series"),
       Img(src=img_ts, alt="time series"),
        Br(),
        H2("Roster"),
        _summary_table(["Employee ID","Employee Name"], [[r["employee_id"], r["employee_name"]] for r in roster]),
        Br(),
        H2("Recent Notes"),
        _summary_table(["Date","Note"], [[n["note_date"], n["note"]] for n in notes[:10]]),
        Br(),
        H2("Event Summary"),
        Img(src=img_bar, alt="bar summary"),
    )

# Run with: python -m report.dashboard
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

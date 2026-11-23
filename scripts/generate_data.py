"""
Generate the (small, deterministic) dataset behind the Pharma Project Finance report.

The numbers are hand-crafted and round so every figure in the report can be
recalculated on paper. One platform, two customers, three projects, 12 months
(Jan-Dec 2026). Actuals run to 31 Oct 2026; Nov-Dec are forecast.

  PRJ-101  Customer 001  Development project       over time (cost-to-cost)   clean, finishes in Aug
  PRJ-102  Customer 002  Clinical batch project    over time (cost-to-cost)   cost overrun (Jun), change
                                                                                order (Oct), late invoice
  PRJ-103  Customer 001  Commercial supply         point in time (batch       advance payment, a failed batch,
                                                   release)                    a batch stuck in QA review

Run:  python scripts/generate_data.py
"""

from __future__ import annotations

import calendar
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

OUT_FILE = Path(__file__).resolve().parents[1] / "data" / "pharma_project_finance.xlsx"
YEAR = 2026
CLOSE_MONTH = 10                                  # October = last closed month
K = 1_000                                         # amounts below are in USD thousands


def me(m: int) -> date:                           # month-end date
    return date(YEAR, m, calendar.monthrange(YEAR, m)[1])


def d(m: int, day: int) -> date:
    return date(YEAR, m, day)


# ------------------------------------------------------------------ dimensions
customers = [
    {"CustomerKey": 1, "Customer": "Customer 001", "CustomerSegment": "Large pharma"},
    {"CustomerKey": 2, "Customer": "Customer 002", "CustomerSegment": "Emerging biotech"},
]
projects = [
    {"ProjectKey": 1, "ProjectID": "PRJ-101", "ProjectName": "PRJ-101 Development project",
     "CustomerKey": 1, "Customer": "Customer 001", "ServiceType": "Process development",
     "RevRecMethod": "Over time", "RevRecBasis": "Cost-to-cost (cost to date / EAC)",
     "Platform": "Platform A", "Site": "Site 01", "StartDate": d(1, 1), "PlannedEndDate": me(8),
     "OriginalContractValue": 1_000 * K, "ProjectStatus": "Completed"},
    {"ProjectKey": 2, "ProjectID": "PRJ-102", "ProjectName": "PRJ-102 Clinical batch project",
     "CustomerKey": 2, "Customer": "Customer 002", "ServiceType": "Clinical manufacturing",
     "RevRecMethod": "Over time", "RevRecBasis": "Cost-to-cost (cost to date / EAC)",
     "Platform": "Platform A", "Site": "Site 01", "StartDate": d(2, 1), "PlannedEndDate": me(12),
     "OriginalContractValue": 2_000 * K, "ProjectStatus": "Active"},
    {"ProjectKey": 3, "ProjectID": "PRJ-103", "ProjectName": "PRJ-103 Commercial supply",
     "CustomerKey": 1, "Customer": "Customer 001", "ServiceType": "Commercial manufacturing",
     "RevRecMethod": "Point in time", "RevRecBasis": "Batch release by QA (control transfers)",
     "Platform": "Platform A", "Site": "Site 01", "StartDate": d(1, 1), "PlannedEndDate": me(12),
     "OriginalContractValue": None, "ProjectStatus": "Active"},
]
CUST = {p["ProjectKey"]: p["CustomerKey"] for p in projects}

# WBS: (key, project, phase, work package, is change order, CO id, CO status)
wbs = [
    (1, 1, "1 Technology transfer", "1.1 Process transfer", "No", "", ""),
    (2, 1, "2 Process development", "2.1 Process optimisation", "No", "", ""),
    (3, 1, "2 Process development", "2.2 Scale-up run", "No", "", ""),
    (4, 1, "3 Reporting & handover", "3.1 Development report", "No", "", ""),
    (5, 2, "1 Technology transfer", "1.1 Process transfer", "No", "", ""),
    (6, 2, "2 Process development", "2.1 Process optimisation", "No", "", ""),
    (7, 2, "2 Process development", "2.2 Engineering run", "No", "", ""),
    (8, 2, "3 GMP manufacturing", "3.1 Clinical GMP batches", "No", "", ""),
    (9, 2, "4 QC & release testing", "4.1 Release testing", "No", "", ""),
    (10, 2, "4 QC & release testing", "4.2 Stability study", "No", "", ""),
    (11, 2, "5 Project management", "5.1 Project management & QA", "No", "", ""),
    (12, 2, "6 Change orders", "6.1 CO-01 Extra stability timepoints", "Yes", "CO-01", "Approved Oct-2026"),
    (13, 3, "1 Commercial batches", "1.1 Batch manufacturing", "No", "", ""),
    (14, 3, "1 Commercial batches", "1.2 QC release testing", "No", "", ""),
    (15, 3, "1 Commercial batches", "1.3 QA batch disposition", "No", "", ""),
]
dim_wbs = [{"WBSKey": k, "ProjectKey": p, "ProjectID": f"PRJ-10{p}", "WBSCode": f"PRJ-10{p}.{wp.split(' ')[0]}",
            "Phase": ph, "WorkPackage": wp, "IsChangeOrder": co, "ChangeOrderID": cid, "ChangeOrderStatus": cst}
           for k, p, ph, wp, co, cid, cst in wbs]
WBS_PROJECT = {k: p for k, p, *_ in wbs}

# ------------------------------------------------------------------ cost plan (budget, time-phased) & actuals
# {wbs key: {month: USD k}}
plan = {
    # PRJ-101: budget 800k (= actuals, a clean project)
    1: {1: 50, 2: 100}, 2: {3: 150, 4: 150, 5: 100}, 3: {5: 50, 6: 100, 7: 50}, 4: {7: 10, 8: 40},
    # PRJ-102: original budget 1,500k
    5: {2: 90, 3: 60}, 6: {3: 80, 4: 140, 5: 80}, 7: {5: 60, 6: 140}, 8: {6: 50, 7: 190, 8: 160, 9: 100},
    9: {8: 30, 9: 40, 10: 60, 11: 20}, 10: {10: 30, 11: 20, 12: 50},
    11: {m: 10 for m in range(2, 12)},
    12: {11: 100, 12: 100},                        # change order CO-01, budget 200k, approved Oct
    # PRJ-103: 11 batches Feb-Dec x 170k (130 manufacturing + 30 QC + 10 QA)
    13: {m: 130 for m in range(2, 13)}, 14: {m: 30 for m in range(2, 13)}, 15: {m: 10 for m in range(2, 13)},
}
actual = {
    1: {1: 50, 2: 100}, 2: {3: 150, 4: 150, 5: 100}, 3: {5: 50, 6: 100, 7: 50}, 4: {7: 10, 8: 40},
    5: {2: 90, 3: 60}, 6: {3: 80, 4: 140, 5: 80},
    7: {5: 60, 6: 190, 7: 50},                     # engineering run overruns: +100k rework
    8: {6: 50, 7: 190, 8: 180, 9: 130, 10: 40},
    9: {8: 30, 9: 40, 10: 70}, 10: {10: 30},
    11: {m: 10 for m in range(2, 11)},
    13: {m: 130 for m in range(2, 11)}, 14: {m: 30 for m in range(2, 11)}, 15: {m: 10 for m in range(2, 11)},
}
cost_plan = [{"PlanDate": me(m), "ProjectKey": WBS_PROJECT[w], "CustomerKey": CUST[WBS_PROJECT[w]], "WBSKey": w,
              "BudgetType": "Change order" if w == 12 else "Original budget",
              "ApprovalDate": me(10) if w == 12 else (d(1, 1) if WBS_PROJECT[w] != 2 else d(2, 1)),
              "PlannedCost": v * K}
             for w, months in plan.items() for m, v in months.items()]
fact_cost = [{"PostingDate": me(m), "ProjectKey": WBS_PROJECT[w], "CustomerKey": CUST[WBS_PROJECT[w]],
              "WBSKey": w, "ActualCost": v * K}
             for w, months in actual.items() for m, v in sorted(months.items())]

# ------------------------------------------------------------------ project-controlling snapshot (price, EAC)
price = {1: {m: 1_000 for m in range(1, 13)},
         2: {m: (2_300 if m >= 10 else 2_000) for m in range(2, 13)}}        # +300k change order in Oct
eac = {1: {m: 800 for m in range(1, 13)},
       2: {m: (1_500 if m <= 5 else 1_800 if m <= 9 else 2_000) for m in range(2, 13)}}
snapshot = [{"SnapshotDate": me(m), "ProjectKey": p, "CustomerKey": CUST[p],
             "TransactionPrice": price[p][m] * K, "EstimateAtCompletion": eac[p][m] * K}
            for p in (1, 2) for m in sorted(price[p]) if m <= CLOSE_MONTH]

# ------------------------------------------------------------------ billing
billing_spec = [
    ("INV-1001", d(1, 15), 1, "Advance payment (30%)", "Advance", 300),
    ("INV-1002", d(1, 12), 3, "Advance payment - capacity reservation", "Advance", 500),
    ("INV-1003", d(2, 10), 2, "Advance payment (20%)", "Advance", 400),
    ("INV-1004", d(4, 20), 1, "Process transfer & optimisation milestone (30%)", "Milestone", 300),
    ("INV-1005", d(4, 22), 2, "Technology transfer complete (20%)", "Milestone", 400),
    ("INV-1006", d(7, 24), 2, "Process development complete (20%)", "Milestone", 400),
    ("INV-1007", d(8, 28), 1, "Final development report (40%)", "Milestone", 400),
    # PRJ-102 'GMP batches complete (20%)' was due in Sep: not invoiced yet (customer PO missing)
]

# ------------------------------------------------------------------ GMP batches
batches = [
    # id, project, type, start, planned release, release date, status, value k, deviations
    ("B-201", 2, "Engineering run", d(6, 20), d(7, 15), d(7, 20), "Released", None, 0),
    ("B-202", 2, "Clinical GMP batch", d(7, 25), d(8, 20), d(8, 25), "Released", None, 0),
    ("B-203", 2, "Clinical GMP batch", d(9, 1), d(9, 25), d(10, 2), "Released", None, 1),
    ("B-301", 3, "Commercial GMP batch", d(2, 2), d(2, 18), d(2, 20), "Released", 250, 0),
    ("B-302", 3, "Commercial GMP batch", d(3, 2), d(3, 18), d(3, 19), "Released", 250, 0),
    ("B-303", 3, "Commercial GMP batch", d(4, 1), d(4, 17), d(4, 21), "Released", 250, 0),
    ("B-304", 3, "Commercial GMP batch", d(5, 4), d(5, 18), None, "Failed", 250, 3),
    ("B-305", 3, "Commercial GMP batch", d(6, 1), d(6, 18), d(6, 19), "Released", 250, 0),
    ("B-306", 3, "Commercial GMP batch", d(7, 1), d(7, 17), d(7, 20), "Released", 250, 0),
    ("B-307", 3, "Commercial GMP batch", d(8, 3), d(8, 18), d(8, 24), "Released", 250, 1),
    ("B-308", 3, "Commercial GMP batch", d(9, 1), d(9, 18), d(9, 18), "Released", 250, 0),
    ("B-309", 3, "Commercial GMP batch", d(10, 1), d(10, 19), None, "Under QA review", 250, 2),
    ("B-310", 3, "Commercial GMP batch", d(11, 2), d(11, 18), None, "Planned", 250, 0),
    ("B-311", 3, "Commercial GMP batch", d(12, 1), d(12, 17), None, "Planned", 250, 0),
    ("B-312", 3, "Commercial GMP batch (remake of B-304)", d(12, 3), d(12, 22), None, "Planned", 250, 0),
]
fact_batch = [{"BatchID": b, "ProjectKey": p, "CustomerKey": CUST[p], "BatchType": t, "ManufactureStartDate": s,
               "PlannedReleaseDate": pr, "ReleaseDate": rd, "BatchStatus": st,
               "BatchValue": (v * K if v else None), "DeviationCount": dev,
               "RightFirstTime": 1 if st == "Released" and dev == 0 else 0}
              for b, p, t, s, pr, rd, st, v, dev in batches]
# PRJ-103 invoices: 250k per released batch less 50k drawn from the advance
inv_no = 1008
for b in sorted([b for b in fact_batch if b["ProjectKey"] == 3 and b["BatchStatus"] == "Released"],
                key=lambda x: x["ReleaseDate"]):
    billing_spec.append((f"INV-{inv_no}", b["ReleaseDate"], 3, f"Batch {b['BatchID']} released (250k less 50k advance)",
                         "Batch release", 200))
    inv_no += 1
fact_billing = sorted([{"InvoiceID": i, "InvoiceDate": dt, "ProjectKey": p, "CustomerKey": CUST[p],
                        "BillingMilestone": lbl, "MilestoneType": t, "InvoiceAmount": a * K}
                       for i, dt, p, lbl, t, a in billing_spec], key=lambda r: r["InvoiceDate"])


# ------------------------------------------------------------------ revenue engine (same logic as the DAX)
def cost_to_date(p: int, m: int) -> float:
    return sum(r["ActualCost"] for r in fact_cost if r["ProjectKey"] == p and r["PostingDate"] <= me(m))


def revenue_to_date(p: int, m: int, price_override: float | None = None) -> float:
    if p in price:
        if m not in eac[p]:
            return 0.0
        pr = price_override if price_override is not None else price[p][m] * K
        return pr * min(1.0, cost_to_date(p, m) / (eac[p][m] * K))
    return sum(b["BatchValue"] for b in fact_batch
               if b["ProjectKey"] == p and b["BatchStatus"] == "Released" and b["ReleaseDate"] <= me(m))


def billed_to_date(p: int, m: int) -> float:
    return sum(r["InvoiceAmount"] for r in fact_billing if r["ProjectKey"] == p and r["InvoiceDate"] <= me(m))


# ------------------------------------------------------------------ general ledger extract (one break in Oct)
# The ERP still holds PRJ-102's old contract value (2.0M) in October: change order CO-01 (+300k) was approved
# but not yet loaded, so the October revenue booking is too low.
ledger = []
for p in (1, 2, 3):
    prev = 0.0
    start = 2 if p == 2 else 1
    for m in range(start, CLOSE_MONTH + 1):
        rtd = revenue_to_date(p, m, price_override=2_000 * K if (p == 2 and m == 10) else None)
        net = rtd - billed_to_date(p, m)
        ledger.append({"PeriodEnd": me(m), "ProjectKey": p, "CustomerKey": CUST[p],
                       "BookedRevenue": round(rtd - prev, 2),
                       "GLContractAsset": round(max(net, 0), 2), "GLContractLiability": round(max(-net, 0), 2)})
        prev = rtd

# ------------------------------------------------------------------ budget (target) and forecast
rev_plan = []
budget_cost = {1: 800, 2: 1_500}
for p in (1, 2):
    cum, prev = 0.0, 0.0
    for m in range(1, 13):
        cum += sum(plan[w].get(m, 0) for w in plan if WBS_PROJECT[w] == p and w != 12)
        r = (1_000 if p == 1 else 2_000) * min(1, cum / budget_cost[p])      # original price x planned % complete
        if round(r - prev, 2):
            rev_plan.append({"PeriodEnd": me(m), "ProjectKey": p, "CustomerKey": CUST[p], "PlanType": "Budget",
                             "PlanRevenue": round((r - prev) * K, 2)})
        prev = r
for m in range(2, 13):                                         # PRJ-103: one 250k batch per month Feb-Dec
    rev_plan.append({"PeriodEnd": me(m), "ProjectKey": 3, "CustomerKey": 1, "PlanType": "Budget", "PlanRevenue": 250 * K})
# Forecast for the open months (Nov-Dec)
# PRJ-102: remaining cost 400k (Nov 250k, Dec 150k), price 2.3M, EAC 2.0M
rev_plan += [
    {"PeriodEnd": me(11), "ProjectKey": 2, "CustomerKey": 2, "PlanType": "Forecast", "PlanRevenue": 287.5 * K},
    {"PeriodEnd": me(12), "ProjectKey": 2, "CustomerKey": 2, "PlanType": "Forecast", "PlanRevenue": 172.5 * K},
    {"PeriodEnd": me(11), "ProjectKey": 3, "CustomerKey": 1, "PlanType": "Forecast", "PlanRevenue": 500 * K},   # B-309 + B-310
    {"PeriodEnd": me(12), "ProjectKey": 3, "CustomerKey": 1, "PlanType": "Forecast", "PlanRevenue": 500 * K},   # B-311 + B-312
]

# ------------------------------------------------------------------ risks & opportunities
ro = [
    ("R-01", "Risk", "GMP / quality", "Batch B-309 deviation investigation pushes its release into next year", 3, 11, 250, 0.40, "PM 01"),
    ("R-02", "Risk", "GMP / quality", "Remake batch B-312 slips into next year", 3, 12, 250, 0.50, "PM 01"),
    ("R-03", "Risk", "Schedule", "PRJ-102 final stability testing slips into next year", 2, 12, 172.5, 0.30, "PM 02"),
    ("O-01", "Opportunity", "Capacity", "Customer 001 orders an extra commercial batch in December", 3, 12, 250, 0.30, "PM 01"),
    ("O-02", "Opportunity", "Scope change", "Second change order on PRJ-102 (process characterisation)", 2, 12, 150, 0.40, "PM 02"),
]
fact_ro = [{"ItemID": i, "ItemType": t, "Category": c, "Description": desc, "ProjectKey": p, "CustomerKey": CUST[p],
            "ExpectedDate": me(m), "RevenueImpact": v * K, "Probability": pr, "Owner": o, "Status": "Open"}
           for i, t, c, desc, p, m, v, pr, o in ro]

TABLES = [
    ("DimCustomer", customers, "Customers (anonymised)."),
    ("DimProject", projects, "Projects = contracts / performance obligations, with the revenue-recognition method."),
    ("DimWBS", dim_wbs, "Work breakdown structure: project > phase > work package (incl. change order)."),
    ("FactCost", fact_cost, "Actual cost by month-end and WBS element."),
    ("FactCostPlan", cost_plan, "Time-phased cost budget by month and WBS element (BAC and planned value)."),
    ("FactContractSnapshot", snapshot, "Month-end controlling snapshot: transaction price and estimate at completion (EAC)."),
    ("FactBilling", fact_billing, "Customer invoices."),
    ("FactBatch", fact_batch, "GMP batches and their QA status; release drives point-in-time revenue."),
    ("FactLedger", ledger, "General-ledger extract: booked revenue and contract asset / liability balances."),
    ("FactRevenuePlan", rev_plan, "Revenue budget (target) and forecast for Nov-Dec."),
    ("FactRiskOpp", fact_ro, "Risks and opportunities register for the FY outlook."),
]


# ------------------------------------------------------------------ write workbook
def to_cell(v):
    if isinstance(v, date) and not isinstance(v, datetime):
        return datetime(v.year, v.month, v.day)
    return v


def write_workbook() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "README"
    navy = "1F3A5F"
    ws["A1"] = "Pharma Project Finance - synthetic dataset"
    ws["A1"].font = Font(bold=True, size=14, color=navy)
    notes = [
        "All data is synthetic, generated by scripts/generate_data.py. Numbers are round on purpose so they can be checked by hand.",
        "One platform, two customers, three projects. Actuals Jan-Oct 2026, forecast Nov-Dec 2026.",
        "Each sheet holds one Excel table (same name as the sheet) that Power Query loads by name.",
        "Sheet 'RevRec_Example' recalculates revenue, billing and the WIP / deferred balance with Excel formulas.",
    ]
    for i, t in enumerate(notes, start=3):
        ws.cell(row=i, column=1, value=t)
    r0 = 9
    for c, h in enumerate(("Table", "Rows", "Description"), start=1):
        ws.cell(row=r0, column=c, value=h).font = Font(bold=True)
    for i, (name, rows, desc) in enumerate(TABLES, start=1):
        ws.cell(row=r0 + i, column=1, value=name)
        ws.cell(row=r0 + i, column=2, value=len(rows))
        ws.cell(row=r0 + i, column=3, value=desc)
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["C"].width = 100

    money = {"ActualCost", "PlannedCost", "TransactionPrice", "EstimateAtCompletion", "InvoiceAmount", "BatchValue",
             "BookedRevenue", "GLContractAsset", "GLContractLiability", "PlanRevenue", "RevenueImpact",
             "OriginalContractValue"}
    for name, rows, _ in TABLES:
        sh = wb.create_sheet(name)
        cols = list(rows[0].keys())
        sh.append(cols)
        for r in rows:
            sh.append([to_cell(r[c]) for c in cols])
        tbl = Table(displayName=name, ref=f"A1:{get_column_letter(len(cols))}{len(rows) + 1}")
        tbl.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        sh.add_table(tbl)
        for ci, c in enumerate(cols, start=1):
            L = get_column_letter(ci)
            sh.column_dimensions[L].width = max(12, min(55, len(c) + 4))
            fmt = "yyyy-mm-dd" if ("Date" in c or c == "PeriodEnd") else "#,##0" if c in money else "0%" if c == "Probability" else None
            if fmt:
                for cell in sh[L][1:]:
                    cell.number_format = fmt
        sh.freeze_panes = "A2"

    # ---- worked example with live formulas
    ex = wb.create_sheet("RevRec_Example")
    ex["A1"] = "Revenue recognition & WIP / deferred - step by step (formulas read the tables)"
    ex["A1"].font = Font(bold=True, size=14, color=navy)
    ex["A2"], ex["B2"] = "Project key (1 or 2)", 1
    ex["B2"].fill = PatternFill("solid", fgColor="FFF4CC")
    ex["C2"] = "<- 1 = PRJ-101 (clean), 2 = PRJ-102 (overrun + change order)"
    heads = ["Month end", "Cost in month", "Cost to date", "EAC", "Transaction price", "% complete",
             "Revenue to date", "Revenue in month", "Billed to date", "Net position", "Balance type"]
    for ci, h in enumerate(heads, start=1):
        c = ex.cell(row=4, column=ci, value=h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=navy)
        c.alignment = Alignment(wrap_text=True)
        ex.column_dimensions[get_column_letter(ci)].width = 16
    for m in range(1, CLOSE_MONTH + 1):
        r = 4 + m
        ex.cell(row=r, column=1, value=to_cell(me(m))).number_format = "mmm-yy"
        ex.cell(row=r, column=2, value=f"=SUMIFS(FactCost[ActualCost],FactCost[ProjectKey],$B$2,FactCost[PostingDate],A{r})")
        ex.cell(row=r, column=3, value=f"=SUM($B$5:B{r})")
        ex.cell(row=r, column=4, value=f"=SUMIFS(FactContractSnapshot[EstimateAtCompletion],FactContractSnapshot[ProjectKey],$B$2,FactContractSnapshot[SnapshotDate],A{r})")
        ex.cell(row=r, column=5, value=f"=SUMIFS(FactContractSnapshot[TransactionPrice],FactContractSnapshot[ProjectKey],$B$2,FactContractSnapshot[SnapshotDate],A{r})")
        ex.cell(row=r, column=6, value=f"=IF(D{r}>0,MIN(1,C{r}/D{r}),0)")
        ex.cell(row=r, column=7, value=f"=E{r}*F{r}")
        ex.cell(row=r, column=8, value=f"=G{r}-N(G{r - 1})" if m > 1 else f"=G{r}")
        ex.cell(row=r, column=9, value=f"=SUMIFS(FactBilling[InvoiceAmount],FactBilling[ProjectKey],$B$2,FactBilling[InvoiceDate],\"<=\"&A{r})")
        ex.cell(row=r, column=10, value=f"=G{r}-I{r}")
        ex.cell(row=r, column=11, value=f"=IF(ROUND(J{r},0)>0,\"Contract asset (WIP)\",IF(ROUND(J{r},0)<0,\"Contract liability (deferred)\",\"Settled\"))")
        for ci in (2, 3, 4, 5, 7, 8, 9, 10):
            ex.cell(row=r, column=ci).number_format = "#,##0;(#,##0);-"
        ex.cell(row=r, column=6).number_format = "0.0%"
    wb.save(OUT_FILE)


if __name__ == "__main__":
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    write_workbook()
    print(f"Wrote {OUT_FILE}")
    for name, rows, _ in TABLES:
        print(f"  {name:<22}{len(rows):>4} rows")
    print("\nMonth-end check (USD k):  project | month | revenue to date | billed to date | net")
    for p in (1, 2, 3):
        for m in range(1, CLOSE_MONTH + 1):
            rtd, btd = revenue_to_date(p, m) / K, billed_to_date(p, m) / K
            if rtd or btd:
                print(f"  PRJ-10{p} {m:>2}  {rtd:>10,.1f} {btd:>10,.1f} {rtd - btd:>10,.1f}")

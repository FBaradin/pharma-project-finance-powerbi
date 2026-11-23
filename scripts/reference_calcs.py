"""
Recompute the report's headline numbers in pandas, straight from the Excel file.

Gives an independent check of the DAX: every value printed here should match
what the Power BI report shows at the 31-Oct-2026 close.
Run:  python scripts/reference_calcs.py
"""

from pathlib import Path

import pandas as pd

XLSX = Path(__file__).resolve().parents[1] / "data" / "pharma_project_finance.xlsx"
T = {n: pd.read_excel(XLSX, sheet_name=n) for n in
     ["DimProject", "FactCost", "FactCostPlan", "FactContractSnapshot", "FactBilling", "FactBatch",
      "FactLedger", "FactRevenuePlan", "FactRiskOpp"]}
proj, cost, plan, snap, bill, batch, gl, rp, ro = T.values()
close = gl.PeriodEnd.max()
ids = proj.set_index("ProjectKey").ProjectID


def rtd(p, asof):
    if proj.set_index("ProjectKey").RevRecMethod[p] == "Over time":
        s = snap[(snap.ProjectKey == p) & (snap.SnapshotDate == asof)]
        if s.empty:
            return 0.0
        ctd = cost[(cost.ProjectKey == p) & (cost.PostingDate <= asof)].ActualCost.sum()
        return float(s.TransactionPrice.iloc[0] * min(1, ctd / s.EstimateAtCompletion.iloc[0]))
    b = batch[(batch.ProjectKey == p) & (batch.BatchStatus == "Released") & (batch.ReleaseDate <= asof)]
    return float(b.BatchValue.sum())


def btd(p, asof):
    return float(bill[(bill.ProjectKey == p) & (bill.InvoiceDate <= asof)].InvoiceAmount.sum())


def k(x):
    return f"{x / 1000:>10,.1f}k"


print(f"Close date: {close.date()}\n")
print("Project   Rev to date   Billed   Net (+WIP/-deferred)   GL net   Difference")
for p in ids.index:
    r, b = rtd(p, close), btd(p, close)
    g = gl[(gl.ProjectKey == p) & (gl.PeriodEnd == close)]
    gnet = float((g.GLContractAsset - g.GLContractLiability).sum())
    print(f"{ids[p]}  {k(r)} {k(b)} {k(r - b)} {k(gnet)} {k(r - b - gnet)}")

# Earned value for PRJ-102
p = 2
s = snap[(snap.ProjectKey == p) & (snap.SnapshotDate == close)].iloc[0]
ctd = cost[(cost.ProjectKey == p)].ActualCost.sum()
bac = plan[(plan.ProjectKey == p) & (plan.ApprovalDate <= close)].PlannedCost.sum()
pv = plan[(plan.ProjectKey == p) & (plan.ApprovalDate <= close) & (plan.PlanDate <= close)].PlannedCost.sum()
ev = bac * min(1, ctd / s.EstimateAtCompletion)
print(f"\nPRJ-102  BAC {k(bac)}  EAC {k(s.EstimateAtCompletion)}  PV {k(pv)}  EV {k(ev)}  AC {k(ctd)}"
      f"  CPI {ev / ctd:.2f}  SPI {ev / pv:.2f}  VAC {k(bac - s.EstimateAtCompletion)}")

actual = sum(rtd(p, close) for p in ids.index)
fcst = rp[rp.PlanType == "Forecast"].PlanRevenue.sum()
budget = rp[rp.PlanType == "Budget"].PlanRevenue.sum()
risks, opps = ro[ro.ItemType == "Risk"], ro[ro.ItemType == "Opportunity"]
base = actual + fcst
print(f"\nFY budget {k(budget)} | actual Jan-Oct {k(actual)} | forecast Nov-Dec {k(fcst)}")
print(f"Scenarios: downside {k(base - risks.RevenueImpact.sum())}  base {k(base)}  "
      f"risk-weighted {k(base - (risks.RevenueImpact * risks.Probability).sum() + (opps.RevenueImpact * opps.Probability).sum())}"
      f"  upside {k(base + opps.RevenueImpact.sum())}")
done = batch[batch.BatchStatus.isin(["Released", "Failed"])]
print(f"\nBatches released {int((done.BatchStatus == 'Released').sum())}, failed {int((done.BatchStatus == 'Failed').sum())}, "
      f"success rate {(done.BatchStatus == 'Released').mean():.1%}, awaiting QA "
      f"{k(batch[batch.BatchStatus == 'Under QA review'].BatchValue.sum())}")

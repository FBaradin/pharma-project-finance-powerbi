# 5-minute demo script

**Opening (15 s).** "This is a small project-finance report for a contract manufacturer: three projects, one page per concept. The data is synthetic, and the logic follows IFRS 15 and month-end close practice. It's saved as a Power BI Project, so the model and every DAX measure are in Git."

**1 · Revenue recognition (60 s).** Start on PRJ-101: revenue = price × cost to date ÷ EAC, row by row in the step table. Switch to PRJ-102 and point at June: the cost was high but revenue was low, because the EAC rose from 1.5M to 1.8M (cumulative catch-up). In October the price goes up with an approved change order.

**2 · WIP & deferred (60 s).** "Earned minus billed, per project." The chart shows PRJ-103's advance as deferred revenue that shrinks with each released batch, and PRJ-102's WIP that grows because a milestone invoice was not sent (flagged after 3 months). Then the recon table: PRJ-102 is 240k off the GL because the change order wasn't loaded in the ERP.

**3 · WBS & project control (45 s).** The S-curve of PV, EV and AC. PRJ-102 has CPI 0.85 and VAC −300k. Expand the WBS to show the engineering-run overrun, and the change order on its own line so scope changes stay visible.

**4 · Outlook (45 s).** Base 6.05M vs a 5.75M target. Choose Downside (5.38M) to show the two GMP batch risks taking us below target. Set the what-if to −20 to show how much the year depends on the last two months.

**5 · GMP (30 s).** "No QA release, no revenue." Show B-309 under review (250k waiting, also risk R-01) and the failed B-304 (250k lost, remake planned).

**Close (15 s).** "Under the hood: a star schema with 8 facts and 4 dimensions, 63 documented measures, implicit measures off, an inactive relationship for planned vs actual release, and a Python check that recomputes the numbers independently of Power BI."

# Study guide

Read one section, open the matching report page, and check that the numbers agree. Every figure below comes from the dataset in this repository. All amounts are in USD, and "k" means thousand.

**Cast:** PRJ-101 (development, over time), PRJ-102 (clinical, over time, the "problem" project) and PRJ-103 (commercial batches, point in time). The year is 2026 and the books are closed to 31 October.

---

## 1. Revenue recognition — *page 1*

**Idea.** Revenue is earned when we deliver what we promised. It does not depend on when we invoice or get paid. The rules come from **IFRS 15** (ASC 606 in the US), which applies five steps: identify the contract, identify the promises in it (performance obligations), set the price, split the price across the promises, then recognise revenue as each promise is fulfilled.

There are two ways to recognise it:

- **Over time.** The customer benefits as we work (development and clinical projects). Progress is measured with **cost-to-cost**: `% complete = cost to date ÷ EAC`.
- **Point in time.** Revenue is earned at one moment, when control passes. For commercial batches that moment is **QA release**.

### PRJ-101: the textbook case
Price 1,000k, estimated total cost (EAC) 800k.

| Month | Cost in month | Cost to date | % complete | Revenue to date | Revenue in month |
|---|---|---|---|---|---|
| Jan | 50 | 50 | 6.25% | 62.5 | 62.5 |
| Feb | 100 | 150 | 18.75% | 187.5 | 125 |
| Mar | 150 | 300 | 37.5% | 375 | 187.5 |
| Apr | 150 | 450 | 56.25% | 562.5 | 187.5 |
| May | 150 | 600 | 75% | 750 | 187.5 |
| Jun | 100 | 700 | 87.5% | 875 | 125 |
| Jul | 60 | 760 | 95% | 950 | 75 |
| Aug | 40 | 800 | 100% | 1,000 | 50 |

Because the EAC never changes, revenue is always cost × 1.25.

### PRJ-102: when the estimate changes
Price 2,000k and EAC 1,500k until May. In June the engineering run needs rework and the **EAC rises to 1,800k**.

- End of May: cost to date 550 → 550 ÷ 1,500 = 36.7% → revenue to date **733.3k**.
- End of June: cost to date 800 → 800 ÷ **1,800** = 44.4% → revenue to date **888.9k**.
- June revenue = 888.9 − 733.3 = **155.6k**, although June cost was 250k.

This is the **cumulative catch-up**: the higher EAC lowers % complete for the whole project, and the correction lands in the month the estimate changes.

In October the customer approves **change order CO-01**: +300k price and +200k cost. Price becomes 2,300k and EAC 2,000k. With cost to date of 1,600k, % complete is 80% and revenue to date is **1,840k**.

### PRJ-103: point in time
Each released batch adds 250k on its release date. Seven batches were released by October, so revenue is **1,750k**. B-304 failed and earns nothing. B-309 is still under QA review, so its revenue waits.

**Check yourself**
1. If PRJ-101's EAC had risen to 1,000k in May (cost to date still 600k), what would revenue to date be?
2. A customer pays 100% up front for a project that has not started. How much revenue is recognised?
3. Why can a month show high cost but low revenue?

<details><summary>Answers</summary>

1. 600 ÷ 1,000 = 60% → 600k, which is 150k lower than the 750k reported.
2. Zero. The cash is a contract liability (deferred revenue) until the work is done.
3. Because the EAC went up, so % complete fell (cumulative catch-up). PRJ-102 in June is an example.
</details>

---

## 2. WIP and deferred balances — *page 2*

**Idea.** Compare **earned** (revenue to date) with **billed** (invoices to date), contract by contract.

- Earned > billed → **contract asset**, also called WIP or unbilled revenue. We need to send an invoice.
- Billed > earned → **contract liability**, also called deferred revenue. We still owe the work.

Never net one contract against another. Two projects of +100 and −100 are a 100 asset **and** a 100 liability, not zero.

### PRJ-101: flips back and forth
| Month | Earned to date | Billed to date | Earned − billed | What it is |
|---|---|---|---|---|
| Jan | 62.5 | 300 (30% advance) | −237.5 | deferred |
| Mar | 375 | 300 | +75 | WIP |
| Apr | 562.5 | 600 (milestone) | −37.5 | deferred |
| Jul | 950 | 600 | +350 | WIP |
| Aug | 1,000 | 1,000 (final invoice) | 0 | settled |

### PRJ-103: an advance that is used up
The customer paid a **500k advance** in January, which is deferred. Each released batch is invoiced at 200k (250k minus 50k taken from the advance). The deferred balance falls by 50k per release: 500 → 450 → … → **150k** in October.

### PRJ-102: WIP that keeps growing
The 20% "GMP batches complete" invoice (400k) was due in September. It was not sent because the customer's purchase order was missing. By October the project has earned 1,840k and billed 1,200k, so **WIP is 640k**. The last invoice was in July, three months earlier, so the report flags it. Growing WIP means either late billing or overstated progress, and both need follow-up.

### Month-end reconciliation
The model's position must equal the general ledger (GL). In October, PRJ-102 shows **640k in the model vs 400k in the GL, a 240k difference**. The cause: CO-01 was approved, but the contract value in the ERP was not updated. Revenue was booked at the old 2,000k price (80% × 2,000 = 1,600k instead of 1,840k).

**Check yourself**
1. Earned 300k, billed 500k: what is the balance called, and how big is it?
2. Why test each project separately?
3. What two explanations would you look for when WIP grows every month?

<details><summary>Answers</summary>

1. A contract liability (deferred revenue) of 200k.
2. Netting hides both balances, and errors that offset each other (for example an invoice posted to the wrong project) disappear in the total.
3. Billing is late (missing PO, disputed milestone), or % complete is overstated (EAC too low).
</details>

---

## 3. WBS and project control — *page 3*

**Idea.** A **WBS** (work breakdown structure) splits a project into phases and work packages, each with a budget. Project control compares the plan with what actually happened.

PRJ-102 WBS (budget, USD k): 1 Technology transfer 150 · 2 Process development 500 · 3 GMP manufacturing 500 · 4 QC & release testing 250 · 5 Project management 100 · **6 Change order CO-01 200** (approved October). BAC = 1,500 + 200 = **1,700k**.

**Earned value** uses three numbers at a date:

| | Meaning | PRJ-102 at 31 Oct |
|---|---|---|
| **PV** (planned value) | budget of the work *scheduled* by now | 1,400k |
| **EV** (earned value) | budget of the work *done* = BAC × % complete | 1,700 × 80% = **1,360k** |
| **AC** (actual cost) | what it really cost | 1,600k |

- **CPI = EV ÷ AC = 0.85.** Each dollar spent delivered 85 cents of planned work, so the project is over budget.
- **SPI = EV ÷ PV = 0.97.** Slightly behind schedule.
- **VAC = BAC − EAC = 1,700 − 2,000 = −300k.** The forecast overrun at completion, which equals the engineering-run rework (+100k) plus the extra GMP and testing effort (+200k).

The change order has its **own WBS line and budget**. Extra scope is priced and tracked separately, so it never hides the overrun.

PRJ-101 for comparison: CPI 1.00 and VAC 0.

**Check yourself**
1. EV 60k, AC 50k: over or under budget?
2. Why does PRJ-103 show no CPI?
3. Budget 100k, CPI 0.875. What is a simple estimate at completion?

<details><summary>Answers</summary>

1. CPI = 1.2, so under budget.
2. Its revenue is recognised per batch, not by cost-to-cost, so there is no EAC-based % complete and no EV.
3. 100 ÷ 0.875 ≈ 114.3k.
</details>

---

## 4. Outlook scenarios — *page 4*

**Idea.** A full-year forecast is a **range built from stated assumptions**, compared with the **target** (budget).

| | USD k |
|---|---|
| Budget (target) | 5,750 |
| Actual Jan–Oct | 4,590 (1,000 + 1,840 + 1,750) |
| Forecast Nov–Dec | 1,460 |
| **Base outlook** | **6,050** (+300 vs budget, mainly the change order) |

Risks & opportunities register (impact × probability):

| ID | Item | Impact | Prob. | Weighted |
|---|---|---|---|---|
| R-01 | B-309 release slips to next year | −250 | 40% | −100 |
| R-02 | Remake batch B-312 slips | −250 | 50% | −125 |
| R-03 | PRJ-102 final testing slips | −172.5 | 30% | −51.75 |
| O-01 | Extra commercial batch in December | +250 | 30% | +75 |
| O-02 | Second change order on PRJ-102 | +150 | 40% | +60 |

- **Downside** = 6,050 − 672.5 = **5,377.5k**, below target.
- **Risk-weighted** = 6,050 − 276.75 + 135 = **5,908.25k**.
- **Upside** = 6,050 + 400 = **6,450k**.

The message for a business review: "Base is above target, but the two GMP batch risks alone could take us below it."

**Check yourself**
1. Why show a range instead of one number?
2. A risk of 400k at 25% probability adds what to the risk-weighted view?

<details><summary>Answers</summary>

1. It makes the assumptions and the uncertainty visible, so leaders can act on the risks.
2. −100k.
</details>

---

## 5. Biopharma contract manufacturing and GMP — *page 5*

**Idea.** A contract development and manufacturing organisation (CDMO) develops and manufactures medicines for other companies. Projects move from **technology transfer** to **process development**, then to **clinical GMP batches** and finally to **commercial supply**. **GMP** (Good Manufacturing Practice) is the quality rulebook: every step is documented, every **deviation** is investigated, and only **QA** can **release** a batch.

Why finance cares:
- **No release, no point-in-time revenue.** B-309 (250k) was due 19 Oct and is still under QA review.
- **A failed batch earns nothing, and its cost is absorbed.** B-304 failed in May with 3 deviations, and a remake (B-312) is planned for December.
- **Quality KPIs lead revenue.** Batch success = 10 released ÷ 11 decided = **90.9%**. Right-first-time counts only batches released with zero deviations.

**Check yourself**
1. Why is B-309 a risk in the outlook (page 4)?
2. Do PRJ-102's clinical batches create revenue on release?

<details><summary>Answers</summary>

1. If the deviation investigation runs into January, its 250k moves to next year.
2. No. PRJ-102 is recognised over time (cost-to-cost). Its batches are tracked for quality only.
</details>

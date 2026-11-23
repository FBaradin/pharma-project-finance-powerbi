# DAX measure catalogue

_Generated from the TMDL source by `scripts/document_measures.py`: 63 measures._

| Folder | Measures |
|---|---|
| 0 Helpers | [Reporting Close Date](#reporting-close-date), [As-of Date](#as-of-date), [Report Subtitle](#report-subtitle) |
| 1 Revenue Recognition | [Actual Cost](#actual-cost), [Cost to Date](#cost-to-date), [Transaction Price](#transaction-price), [Estimate at Completion (EAC)](#estimate-at-completion-eac), [Revenue to Date (Over Time)](#revenue-to-date-over-time), [Revenue to Date (Point in Time)](#revenue-to-date-point-in-time), [Revenue to Date](#revenue-to-date), [Revenue to Date (Opening)](#revenue-to-date-opening), [Revenue Recognised](#revenue-recognised), [% Complete](#-complete), [Gross Margin](#gross-margin), [Gross Margin %](#gross-margin-) |
| 2 WIP & Deferred | [Invoiced Amount](#invoiced-amount), [Billed to Date](#billed-to-date), [Net Contract Position](#net-contract-position), [Contract Assets (WIP)](#contract-assets-wip), [Contract Liabilities (Deferred)](#contract-liabilities-deferred), [Balance Type](#balance-type), [Months Since Last Invoice](#months-since-last-invoice), [WIP Ageing Flag](#wip-ageing-flag), [GL Net Contract Balance](#gl-net-contract-balance), [Difference vs GL](#difference-vs-gl), [Recon Status](#recon-status), [Projects to Investigate](#projects-to-investigate) |
| 3 WBS & Project Control | [Budget at Completion (BAC)](#budget-at-completion-bac), [Planned Value (PV)](#planned-value-pv), [Actual Cost (AC)](#actual-cost-ac), [Earned Value (EV)](#earned-value-ev), [CPI](#cpi), [SPI](#spi), [Variance at Completion (VAC)](#variance-at-completion-vac), [Budget Remaining](#budget-remaining), [Cost Variance to Plan](#cost-variance-to-plan) |
| 4 Outlook Scenarios | [Revenue Budget](#revenue-budget), [Revenue Forecast](#revenue-forecast), [Revenue Actual + Forecast](#revenue-actual--forecast), [FY Budget](#fy-budget), [FY Actual to Date](#fy-actual-to-date), [FY Remaining Forecast](#fy-remaining-forecast), [FY Base Outlook](#fy-base-outlook), [FY Risks](#fy-risks), [FY Opportunities](#fy-opportunities), [FY Risks (Weighted)](#fy-risks-weighted), [FY Opportunities (Weighted)](#fy-opportunities-weighted), [Scenario Outlook](#scenario-outlook), [Gap to Budget](#gap-to-budget), [R&O Impact](#ro-impact), [R&O Probability](#ro-probability), [R&O Weighted Impact](#ro-weighted-impact) |
| 5 GMP Batches | [Batches](#batches), [Batches Released](#batches-released), [Batches Failed](#batches-failed), [Batch Success Rate](#batch-success-rate), [Right First Time %](#right-first-time-), [Revenue Awaiting QA Release](#revenue-awaiting-qa-release), [Revenue Lost (Failed Batches)](#revenue-lost-failed-batches), [Batch Value](#batch-value), [Batch Revenue Recognised](#batch-revenue-recognised), [Deviations](#deviations) |
| 7 What-if parameters | [Forecast Adjustment Value](#forecast-adjustment-value) |

## 0 Helpers

### Reporting Close Date

Last closed month-end = latest period in the general-ledger extract. Everything after it is forecast.

```dax
Reporting Close Date =
CALCULATE ( MAX ( FactLedger[PeriodEnd] ), REMOVEFILTERS () )
```

Format: `dd mmm yyyy`

### As-of Date

The date every "to date" (balance) measure is evaluated at: end of the period in context, capped at the close date.

```dax
As-of Date =
VAR _periodEnd = MAX ( DimDate[Date] )
VAR _close = [Reporting Close Date]
RETURN
    IF ( NOT ISBLANK ( _periodEnd ), MIN ( _periodEnd, _close ) )
```

Format: `dd mmm yyyy`

### Report Subtitle

Header text, e.g. "Actuals to 31 Oct 2026 · USD · synthetic data".

```dax
Report Subtitle =
"Actuals to " & FORMAT ( [Reporting Close Date], "dd mmm yyyy" ) & "  ·  USD  ·  synthetic data"
```


## 1 Revenue Recognition

### Actual Cost

Actual cost posted in the period in context.

```dax
Actual Cost =
SUM ( FactCost[ActualCost] )
```

Format: `\$#,0`

### Cost to Date

Inception-to-date actual cost at the as-of date.

```dax
Cost to Date =
VAR _asOf = [As-of Date]
RETURN
    IF (
        NOT ISBLANK ( _asOf ),
        CALCULATE ( [Actual Cost], REMOVEFILTERS ( DimDate ), DimDate[Date] <= _asOf )
    )
```

Format: `\$#,0`

### Transaction Price

Contract value (original price + approved change orders) in the as-of month's controlling snapshot.

```dax
Transaction Price =
VAR _asOf = [As-of Date]
RETURN
    IF (
        NOT ISBLANK ( _asOf ),
        CALCULATE (
            SUM ( FactContractSnapshot[TransactionPrice] ),
            REMOVEFILTERS ( DimDate ),
            DimDate[Date] = EOMONTH ( _asOf, 0 )
        )
    )
```

Format: `\$#,0`

### Estimate at Completion (EAC)

Estimate at completion (EAC): the latest forecast of the project's total cost, from the as-of month's snapshot.

```dax
Estimate at Completion (EAC) =
VAR _asOf = [As-of Date]
RETURN
    IF (
        NOT ISBLANK ( _asOf ),
        CALCULATE (
            SUM ( FactContractSnapshot[EstimateAtCompletion] ),
            REMOVEFILTERS ( DimDate ),
            DimDate[Date] = EOMONTH ( _asOf, 0 )
        )
    )
```

Format: `\$#,0`

### Revenue to Date (Over Time)

Over-time revenue to date, cost-to-cost method, project by project: transaction price x MIN ( 1, cost to date / EAC ).

```dax
Revenue to Date (Over Time) =
VAR _asOf = [As-of Date]
RETURN
    IF (
        NOT ISBLANK ( _asOf ),
        CALCULATE (
            SUMX (
                VALUES ( DimProject[ProjectKey] ),
                VAR _price = [Transaction Price]
                VAR _eac = [Estimate at Completion (EAC)]
                VAR _costToDate = [Cost to Date]
                RETURN
                    IF ( _eac > 0, _price * MIN ( 1, DIVIDE ( _costToDate, _eac ) ) )
            ),
            DimProject[RevRecMethod] = "Over time",
            REMOVEFILTERS ( DimWBS )
        )
    )
```

Format: `\$#,0`

### Revenue to Date (Point in Time)

Point-in-time revenue to date: value of commercial batches released by QA up to the as-of date.

```dax
Revenue to Date (Point in Time) =
VAR _asOf = [As-of Date]
RETURN
    IF (
        NOT ISBLANK ( _asOf ),
        CALCULATE (
            SUM ( FactBatch[BatchValue] ),
            FactBatch[BatchStatus] = "Released",
            DimProject[RevRecMethod] = "Point in time",
            REMOVEFILTERS ( DimDate ),
            DimDate[Date] <= _asOf
        )
    )
```

Format: `\$#,0`

### Revenue to Date

Total revenue earned since the start of the contract, at the as-of date.

```dax
Revenue to Date =
[Revenue to Date (Over Time)] + [Revenue to Date (Point in Time)]
```

Format: `\$#,0`

### Revenue to Date (Opening)

Revenue to date on the day before the period in context starts.

```dax
Revenue to Date (Opening) =
VAR _openingDate = MIN ( DimDate[Date] ) - 1
RETURN
    CALCULATE ( [Revenue to Date], REMOVEFILTERS ( DimDate ), DimDate[Date] = _openingDate )
```

Format: `\$#,0`

### Revenue Recognised

Revenue recognised in the period = revenue to date at the end - revenue to date at the start. An EAC change therefore hits the month it happens in (cumulative catch-up).

```dax
Revenue Recognised =
[Revenue to Date] - [Revenue to Date (Opening)]
```

Format: `\$#,0`

### % Complete

Cost-to-cost % complete of over-time projects (weighted by contract value when several are selected).

```dax
% Complete =
DIVIDE ( [Revenue to Date (Over Time)], [Transaction Price] )
```

Format: `0.0%`

### Gross Margin

Revenue recognised minus actual cost in the period.

```dax
Gross Margin =
[Revenue Recognised] - [Actual Cost]
```

Format: `\$#,0`

### Gross Margin %

```dax
Gross Margin % =
DIVIDE ( [Gross Margin], [Revenue Recognised] )
```

Format: `0.0%`


## 2 WIP & Deferred

### Invoiced Amount

Invoices issued in the period in context.

```dax
Invoiced Amount =
SUM ( FactBilling[InvoiceAmount] )
```

Format: `\$#,0`

### Billed to Date

Inception-to-date invoicing at the as-of date.

```dax
Billed to Date =
VAR _asOf = [As-of Date]
RETURN
    IF (
        NOT ISBLANK ( _asOf ),
        CALCULATE ( [Invoiced Amount], REMOVEFILTERS ( DimDate ), DimDate[Date] <= _asOf )
    )
```

Format: `\$#,0`

### Net Contract Position

Earned minus billed. Positive = contract asset (WIP, unbilled). Negative = contract liability (deferred revenue).

```dax
Net Contract Position =
[Revenue to Date] - [Billed to Date]
```

Format: `\$#,0;-\$#,0;\$0`

### Contract Assets (WIP)

Contract assets (WIP): sum of the projects whose position is POSITIVE. Never netted across contracts.

```dax
Contract Assets (WIP) =
SUMX (
    VALUES ( DimProject[ProjectKey] ),
    VAR _net = [Net Contract Position]
    RETURN
        IF ( _net > 0, _net )
) + 0
```

Format: `\$#,0`

### Contract Liabilities (Deferred)

Contract liabilities (deferred revenue): sum of the projects whose position is NEGATIVE, shown as a positive amount.

```dax
Contract Liabilities (Deferred) =
SUMX (
    VALUES ( DimProject[ProjectKey] ),
    VAR _net = [Net Contract Position]
    RETURN
        IF ( _net < 0, - _net )
) + 0
```

Format: `\$#,0`

### Balance Type

Plain-language label for the position in context.

```dax
Balance Type =
VAR _net = ROUND ( [Net Contract Position], 0 )
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( _net ), BLANK (),
        _net > 0, "Contract asset (WIP)",
        _net < 0, "Contract liability (deferred)",
        "Settled"
    )
```

### Months Since Last Invoice

Whole months between the last invoice and the as-of date.

```dax
Months Since Last Invoice =
VAR _asOf = [As-of Date]
VAR _lastInvoice =
    CALCULATE ( MAX ( FactBilling[InvoiceDate] ), REMOVEFILTERS ( DimDate ), DimDate[Date] <= _asOf )
RETURN
    IF ( NOT ISBLANK ( _lastInvoice ), DATEDIFF ( _lastInvoice, _asOf, MONTH ) )
```

Format: `0`

### WIP Ageing Flag

Warns when unbilled revenue has been building for 3+ months (late billing or over-stated progress).

```dax
WIP Ageing Flag =
IF (
    [Net Contract Position] > 0 && [Months Since Last Invoice] >= 3,
    "⚠ Unbilled 3+ months",
    "OK"
)
```

### GL Net Contract Balance

Contract asset minus contract liability booked in the general ledger at the as-of month-end.

```dax
GL Net Contract Balance =
VAR _asOf = [As-of Date]
RETURN
    IF (
        NOT ISBLANK ( _asOf ),
        CALCULATE (
            SUM ( FactLedger[GLContractAsset] ) - SUM ( FactLedger[GLContractLiability] ),
            REMOVEFILTERS ( DimDate ),
            DimDate[Date] = EOMONTH ( _asOf, 0 )
        )
    )
```

Format: `\$#,0;-\$#,0;\$0`

### Difference vs GL

Model position minus GL balance. Should be zero.

```dax
Difference vs GL =
[Net Contract Position] - [GL Net Contract Balance]
```

Format: `\$#,0;-\$#,0;\$0`

### Recon Status

"✔ Matches GL" or "⚠ Investigate" (difference above 1 USD).

```dax
Recon Status =
IF (
    NOT ISBLANK ( [GL Net Contract Balance] ),
    IF ( ABS ( [Difference vs GL] ) <= 1, "✔ Matches GL", "⚠ Investigate" )
)
```

### Projects to Investigate

Number of projects whose model position differs from the GL. Tested per project because offsetting errors cancel in totals.

```dax
Projects to Investigate =
COUNTROWS ( FILTER ( VALUES ( DimProject[ProjectKey] ), ABS ( [Difference vs GL] ) > 1 ) ) + 0
```

Format: `0`


## 3 WBS & Project Control

### Budget at Completion (BAC)

Budget at completion (BAC): time-phased budget in total, incl. change orders approved by the as-of date.

```dax
Budget at Completion (BAC) =
VAR _asOf = [As-of Date]
RETURN
    CALCULATE (
        SUM ( FactCostPlan[PlannedCost] ),
        REMOVEFILTERS ( DimDate ),
        FactCostPlan[ApprovalDate] <= _asOf
    )
```

Format: `\$#,0`

### Planned Value (PV)

Planned value (PV): budgeted cost of the work scheduled up to the as-of date.

```dax
Planned Value (PV) =
VAR _asOf = [As-of Date]
RETURN
    IF (
        NOT ISBLANK ( _asOf ),
        CALCULATE (
            SUM ( FactCostPlan[PlannedCost] ),
            REMOVEFILTERS ( DimDate ),
            DimDate[Date] <= _asOf,
            FactCostPlan[ApprovalDate] <= _asOf
        )
    )
```

Format: `\$#,0`

### Actual Cost (AC)

Actual cost (AC) to date, the earned-value name for Cost to Date.

```dax
Actual Cost (AC) =
[Cost to Date]
```

Format: `\$#,0`

### Earned Value (EV)

Earned value (EV): budget of the work actually done = BAC x % complete (cost-to-cost), per over-time project.

```dax
Earned Value (EV) =
CALCULATE (
    SUMX (
        VALUES ( DimProject[ProjectKey] ),
        VAR _eac = [Estimate at Completion (EAC)]
        RETURN
            IF ( _eac > 0, [Budget at Completion (BAC)] * MIN ( 1, DIVIDE ( [Cost to Date], _eac ) ) )
    ),
    DimProject[RevRecMethod] = "Over time",
    REMOVEFILTERS ( DimWBS )
)
```

Format: `\$#,0`

### CPI

Cost performance index = EV / AC. Below 1 = each dollar spent delivers less than a dollar of planned work (over budget).

```dax
CPI =
DIVIDE (
    [Earned Value (EV)],
    CALCULATE ( [Cost to Date], DimProject[RevRecMethod] = "Over time", REMOVEFILTERS ( DimWBS ) )
)
```

Format: `0.00`

### SPI

Schedule performance index = EV / PV. Below 1 = behind schedule.

```dax
SPI =
DIVIDE (
    [Earned Value (EV)],
    CALCULATE ( [Planned Value (PV)], DimProject[RevRecMethod] = "Over time", REMOVEFILTERS ( DimWBS ) )
)
```

Format: `0.00`

### Variance at Completion (VAC)

Forecast over/underrun at completion: BAC - EAC (negative = overrun).

```dax
Variance at Completion (VAC) =
VAR _eac = [Estimate at Completion (EAC)]
RETURN
    IF ( NOT ISBLANK ( _eac ), CALCULATE ( [Budget at Completion (BAC)], REMOVEFILTERS ( DimWBS ) ) - _eac )
```

Format: `\$#,0;-\$#,0;\$0`

### Budget Remaining

Budget not yet spent: BAC - actual cost to date.

```dax
Budget Remaining =
[Budget at Completion (BAC)] - [Cost to Date]
```

Format: `\$#,0;-\$#,0;\$0`

### Cost Variance to Plan

Planned to date minus actual to date (negative = spending more than planned so far).

```dax
Cost Variance to Plan =
[Planned Value (PV)] - [Cost to Date]
```

Format: `\$#,0;-\$#,0;\$0`


## 4 Outlook Scenarios

### Revenue Budget

```dax
Revenue Budget =
CALCULATE ( SUM ( FactRevenuePlan[PlanRevenue] ), FactRevenuePlan[PlanType] = "Budget" )
```

Format: `\$#,0`

### Revenue Forecast

Forecast for the open months, flexed by the Forecast Adjustment what-if parameter.

```dax
Revenue Forecast =
CALCULATE ( SUM ( FactRevenuePlan[PlanRevenue] ), FactRevenuePlan[PlanType] = "Forecast" )
    * ( 1 + [Forecast Adjustment Value] )
```

Format: `\$#,0`

### Revenue Actual + Forecast

Actual revenue for closed months + forecast for open months.

```dax
Revenue Actual + Forecast =
[Revenue Recognised] + [Revenue Forecast]
```

Format: `\$#,0`

### FY Budget

Full-year revenue target of the reporting year.

```dax
FY Budget =
VAR _fy = YEAR ( [Reporting Close Date] )
RETURN
    CALCULATE ( [Revenue Budget], REMOVEFILTERS ( DimDate ), DimDate[Year] = _fy )
```

Format: `\$#,0`

### FY Actual to Date

Revenue actually recognised from 1 January to the close date.

```dax
FY Actual to Date =
VAR _fy = YEAR ( [Reporting Close Date] )
RETURN
    CALCULATE ( [Revenue Recognised], REMOVEFILTERS ( DimDate ), DimDate[Year] = _fy )
```

Format: `\$#,0`

### FY Remaining Forecast

Forecast revenue for the remaining (open) months of the year.

```dax
FY Remaining Forecast =
VAR _fy = YEAR ( [Reporting Close Date] )
RETURN
    CALCULATE ( [Revenue Forecast], REMOVEFILTERS ( DimDate ), DimDate[Year] = _fy )
```

Format: `\$#,0`

### FY Base Outlook

Base outlook = actual to date + remaining forecast.

```dax
FY Base Outlook =
[FY Actual to Date] + [FY Remaining Forecast]
```

Format: `\$#,0`

### FY Risks

```dax
FY Risks =
CALCULATE ( SUM ( FactRiskOpp[RevenueImpact] ), FactRiskOpp[ItemType] = "Risk", REMOVEFILTERS ( DimDate ) )
```

Format: `\$#,0`

### FY Opportunities

```dax
FY Opportunities =
CALCULATE ( SUM ( FactRiskOpp[RevenueImpact] ), FactRiskOpp[ItemType] = "Opportunity", REMOVEFILTERS ( DimDate ) )
```

Format: `\$#,0`

### FY Risks (Weighted)

Expected value of risks: impact x probability, item by item.

```dax
FY Risks (Weighted) =
CALCULATE (
    SUMX ( FactRiskOpp, FactRiskOpp[RevenueImpact] * FactRiskOpp[Probability] ),
    FactRiskOpp[ItemType] = "Risk",
    REMOVEFILTERS ( DimDate )
)
```

Format: `\$#,0`

### FY Opportunities (Weighted)

```dax
FY Opportunities (Weighted) =
CALCULATE (
    SUMX ( FactRiskOpp, FactRiskOpp[RevenueImpact] * FactRiskOpp[Probability] ),
    FactRiskOpp[ItemType] = "Opportunity",
    REMOVEFILTERS ( DimDate )
)
```

Format: `\$#,0`

### Scenario Outlook

Full-year revenue for the scenario in context (slicer or chart axis). Defaults to Base.

```dax
Scenario Outlook =
VAR _base = [FY Base Outlook]
RETURN
    SWITCH (
        SELECTEDVALUE ( DimScenario[Scenario], "Base" ),
        "Downside", _base - [FY Risks],
        "Risk-weighted", _base - [FY Risks (Weighted)] + [FY Opportunities (Weighted)],
        "Base", _base,
        "Upside", _base + [FY Opportunities]
    )
```

Format: `\$#,0`

### Gap to Budget

Scenario outlook minus full-year budget (negative = below target).

```dax
Gap to Budget =
[Scenario Outlook] - [FY Budget]
```

Format: `+\$#,0;-\$#,0;\$0`

### R&O Impact

```dax
R&O Impact =
SUM ( FactRiskOpp[RevenueImpact] )
```

Format: `\$#,0`

### R&O Probability

```dax
R&O Probability =
AVERAGE ( FactRiskOpp[Probability] )
```

Format: `0%`

### R&O Weighted Impact

Impact x probability, signed: opportunities +, risks -.

```dax
R&O Weighted Impact =
SUMX (
    FactRiskOpp,
    FactRiskOpp[RevenueImpact] * FactRiskOpp[Probability]
        * IF ( FactRiskOpp[ItemType] = "Risk", -1, 1 )
)
```

Format: `+\$#,0;-\$#,0;\$0`


## 5 GMP Batches

### Batches

Number of batches, dated by PLANNED release (inactive relationship activated with USERELATIONSHIP).

```dax
Batches =
CALCULATE ( COUNTROWS ( FactBatch ), USERELATIONSHIP ( FactBatch[PlannedReleaseDate], DimDate[Date] ) )
```

Format: `0`

### Batches Released

```dax
Batches Released =
CALCULATE ( [Batches], FactBatch[BatchStatus] = "Released" ) + 0
```

Format: `0`

### Batches Failed

```dax
Batches Failed =
CALCULATE ( [Batches], FactBatch[BatchStatus] = "Failed" ) + 0
```

Format: `0`

### Batch Success Rate

Released / (released + failed): only batches with a final QA decision count.

```dax
Batch Success Rate =
DIVIDE ( [Batches Released], [Batches Released] + [Batches Failed] )
```

Format: `0.0%`

### Right First Time %

Released with zero deviations / (released + failed).

```dax
Right First Time % =
DIVIDE (
    CALCULATE ( SUM ( FactBatch[RightFirstTime] ), USERELATIONSHIP ( FactBatch[PlannedReleaseDate], DimDate[Date] ) ),
    [Batches Released] + [Batches Failed]
)
```

Format: `0.0%`

### Revenue Awaiting QA Release

Commercial revenue waiting for QA release: no release, no revenue.

```dax
Revenue Awaiting QA Release =
CALCULATE ( SUM ( FactBatch[BatchValue] ), FactBatch[BatchStatus] = "Under QA review", REMOVEFILTERS ( DimDate ) ) + 0
```

Format: `\$#,0`

### Revenue Lost (Failed Batches)

Value of failed batches: no revenue, and their cost is absorbed.

```dax
Revenue Lost (Failed Batches) =
CALCULATE ( SUM ( FactBatch[BatchValue] ), FactBatch[BatchStatus] = "Failed", REMOVEFILTERS ( DimDate ) ) + 0
```

Format: `\$#,0`

### Batch Value

Batch value (commercial batches only).

```dax
Batch Value =
CALCULATE ( SUM ( FactBatch[BatchValue] ), USERELATIONSHIP ( FactBatch[PlannedReleaseDate], DimDate[Date] ) )
```

Format: `\$#,0`

### Batch Revenue Recognised

Revenue recognised for the batch: its value if QA released it, otherwise zero.

```dax
Batch Revenue Recognised =
CALCULATE (
    SUM ( FactBatch[BatchValue] ),
    FactBatch[BatchStatus] = "Released",
    USERELATIONSHIP ( FactBatch[PlannedReleaseDate], DimDate[Date] )
)
```

Format: `\$#,0`

### Deviations

```dax
Deviations =
CALCULATE ( SUM ( FactBatch[DeviationCount] ), USERELATIONSHIP ( FactBatch[PlannedReleaseDate], DimDate[Date] ) )
```

Format: `0`


## 7 What-if parameters

### Forecast Adjustment Value

Selected forecast adjustment as a fraction (0 when nothing or several values are selected).

```dax
Forecast Adjustment Value =
SELECTEDVALUE ( 'Forecast Adjustment'[Forecast Adjustment %], 0 ) / 100
```

Format: `+0%;-0%;0%`

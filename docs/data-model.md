# Data model

A **star schema**: each fact table records one kind of business event, and the dimensions describe the who / what / when around it. Source: one Excel workbook with one Excel table per model table. Power Query loads each table by name and sets explicit column types. The workbook folder is set in the `DataFolder` parameter.

## Dimensions

| Table | One row per | Notes |
|---|---|---|
| `DimDate` | day of 2026 | Built in DAX (`CALENDAR` over the data's date range) and marked as the date table. `Period Type` = *Actual* up to the close date, *Forecast* after it. |
| `DimProject` | project (= contract = performance obligation) | `RevRecMethod` decides the revenue rule: *Over time* or *Point in time*. |
| `DimWBS` | WBS element | Phase → work package. The change order is its own element (`IsChangeOrder = Yes`). |
| `DimCustomer` | customer | |

## Facts

| Table | One row per | Used for | Additive? |
|---|---|---|---|
| `FactCost` | month × WBS element | Actual cost, cost to date | yes |
| `FactCostPlan` | month × WBS element | BAC (total budget), planned value (to date) | yes; change-order budget counts from its approval date |
| `FactContractSnapshot` | month-end × over-time project | Transaction price, EAC | **no**, read one month (snapshot) |
| `FactBilling` | invoice | Invoiced, billed to date | yes |
| `FactBatch` | GMP batch | Point-in-time revenue, quality KPIs | yes; two date roles |
| `FactLedger` | month-end × project | Booked revenue; GL contract asset / liability | revenue yes; balances are snapshots |
| `FactRevenuePlan` | month × project × plan type | Budget (target), forecast | yes |
| `FactRiskOpp` | register item | Scenario range | yes |

Helper tables: `DimScenario` (disconnected, drives the scenario slicer), `Forecast Adjustment` (what-if parameter), and `_Measures` (home of all measures).

## Design choices (and why)

1. **One fact table per event type.** Each grain is different (monthly cost, invoices, batches, snapshots). Putting them in one table would mix grains and break the totals.
2. **Single-direction one-to-many relationships only.** Filters flow from dimensions to facts, so they are predictable.
3. **`DimWBS` is not related to `DimProject`.** A second path from `FactCost` to `DimProject` would make the model ambiguous, so `DimWBS` carries `ProjectID` for its hierarchy instead.
4. **Two dates on batches.** `ReleaseDate` is active because revenue is earned on release. `PlannedReleaseDate` is inactive and switched on with `USERELATIONSHIP` for quality KPIs, so a failed batch (no release date) still counts in the month it was due.
5. **Revenue is calculated per project.** IFRS 15 measures progress per performance obligation, so revenue measures remove WBS filters. WBS is for cost control.
6. **Contract assets and liabilities are tested per project.** Netting them would hide both balances.
7. **One as-of date drives every "to date" measure,** so the same measure works for a month, a quarter or the year and never invents actuals after the close.
8. **Implicit measures are disabled.** Every number on the page comes from a named, documented measure.
9. **Saved as a Power BI Project (TMDL + PBIR).** The model and report are plain text and can be reviewed in Git.

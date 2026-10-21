---
title: One month-end, start to finish
member: Nick Walker
github: nick2468
version: 0.89.1
date: 2026-10-21
media:
  - file: 01-workspace.png
    alt: The workspace. The Modules tree lists the bakery's objects by type, and the aggregation's result shows September sales by shop and category.
  - file: 02-workflow.png
    alt: The Month-end close Workflow on its canvas. It builds the aggregation first, then the report.
  - file: 03-data-model.png
    alt: The Sales with products data model in view. Each sale is joined to its product's name, category and price, 720 rows for September.
  - file: 04-schedule-next-runs.png
    alt: The Schedule's trigger. It runs at 6 am on the first of each month, Brisbane time, and lists its next five runs.
  - file: 05-run-record.png
    alt: The log of one run started from the Scheduler. Each step starts and ends, and the Workflow finishes in SUCCESS.
  - file: 06-report.png
    alt: The Month-end sales report after its run. It wrote 8 rows to a CSV file, ready to download or print.
---
Harbour Street Bakery is a made-up business with two shops. Its September close runs end
to end in DataCrafter: two data sources, a data model that joins them, an aggregation, a
report, and a Workflow that runs the aggregation and then the report. The Scheduler runs
the Workflow at 6 am on the first of each month. Every name in these pictures is made up.

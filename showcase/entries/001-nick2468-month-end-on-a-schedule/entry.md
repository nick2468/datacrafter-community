---
title: Month-end pack on a schedule
member: Nick Walker
github: nick2468
version: 0.89.1
date: 2026-10-21
media:
  - file: 01-workflow.png
    alt: The Workflow editor showing the two chained steps, the aggregation and then the report
  - file: 02-run-record.png
    alt: The log of one run, each step starting and finishing in SUCCESS
---
A Workflow chains the steps of a month-end sales pack for a made-up two-shop bakery: it
sums September's sales by shop and category, then builds the month-end report from that
summary. The Scheduler runs it early on the first day of each month, so the pack is
waiting when the team arrives. The run log shows each step as it starts and finishes, so
a failed step is easy to find.

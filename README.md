# Disaster Relief Resource & Camp Management System

DBMS Project-Based Learning project: a normalized (3NF) relational database in SQLite with a Python application layer.

## Features
- 14 tables: Disaster, Location, Camp, Warehouse, Family, Person, Volunteer, ReliefItem, Stock, Donation, Need, Distribution, Assignment, Referral
- Constraints (PK, FK, UNIQUE, CHECK, DEFAULT) and 3 triggers that block duplicate entitlement, over-allocation, item mismatch and insufficient stock
- Python functions for registration, needs, donations, distributions (parameterised queries, transactions)
- 6 reports: camp occupancy, unmet needs, stock alerts, audit trail, volunteer workload, families without aid

## Files
| File | Purpose |
|---|---|
| schema.sql | DDL: tables, constraints, triggers, indexes |
| data.sql | Sample (illustrative) data |
| relief_app.py | Python application and reports |
| run_tests.py | Runs 13 test cases and writes results.json |
| relief.db | Ready-made SQLite database (optional) |

## Run
Requires Python 3.8+ (standard library only).

```
# optional: rebuild the database from scratch
python3 -c "import sqlite3,os; os.path.exists('relief.db') and os.remove('relief.db'); c=sqlite3.connect('relief.db'); c.executescript(open('schema.sql').read()); c.executescript(open('data.sql').read()); c.commit()"

python3 relief_app.py                 # all reports
python3 relief_app.py audit_trail     # one report (camp_occupancy, unmet_needs, stock_alerts, audit_trail, volunteer_load, no_aid)
python3 run_tests.py                  # execute the test cases
```

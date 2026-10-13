"""Disaster Relief Resource & Camp Management System - Python + SQLite application layer."""
import sqlite3, sys, os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relief.db")

def connect(path=DB):
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")
    return con

def run(con, sql, params=()):
    """Parameterised write inside a transaction; returns (ok, message)."""
    try:
        with con:                      # commits on success, rolls back on error
            cur = con.execute(sql, params)
        return True, f"OK ({cur.rowcount} row(s) affected)"
    except sqlite3.IntegrityError as e:
        return False, f"REJECTED: {e}"

def query(con, sql, params=()):
    cur = con.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return cols, cur.fetchall()

def table(cols, rows):
    rows = [[str(v) for v in r] for r in rows]
    w = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]
    line = "+" + "+".join("-" * (x + 2) for x in w) + "+"
    fmt = lambda r: "| " + " | ".join(v.ljust(w[i]) for i, v in enumerate(r)) + " |"
    return "\n".join([line, fmt(cols), line] + [fmt(r) for r in rows] + [line])

# ---- CRUD / transactions ---------------------------------------------------
def add_family(con, head, contact, camp_id):
    return run(con, "INSERT INTO Family (HeadOfFamily, ContactInfo, CampID) VALUES (?,?,?)", (head, contact, camp_id))

def add_person(con, family_id, name, age, gender, cond="None"):
    return run(con, "INSERT INTO Person (FamilyID, FullName, Age, Gender, MedicalCondition) VALUES (?,?,?,?,?)",
               (family_id, name, age, gender, cond))

def add_need(con, family_id, item_id, qty):
    return run(con, "INSERT INTO Need (FamilyID, ItemID, Quantity) VALUES (?,?,?)", (family_id, item_id, qty))

def update_contact(con, family_id, contact):
    return run(con, "UPDATE Family SET ContactInfo = ? WHERE FamilyID = ?", (contact, family_id))

def delete_camp(con, camp_id):
    return run(con, "DELETE FROM Camp WHERE CampID = ?", (camp_id,))

def record_donation(con, donor, item_id, wh_id, qty):
    return run(con, "INSERT INTO Donation (DonorName, ItemID, WarehouseID, Quantity) VALUES (?,?,?,?)",
               (donor, item_id, wh_id, qty))

def distribute(con, need_id, stock_id, volunteer_id, qty):
    return run(con, "INSERT INTO Distribution (NeedID, StockID, VolunteerID, Quantity) VALUES (?,?,?,?)",
               (need_id, stock_id, volunteer_id, qty))

# ---- Reports ---------------------------------------------------------------
REPORTS = {
 "camp_occupancy": ("Camp occupancy (JOIN + GROUP BY)",
  """SELECT c.CampName, c.Capacity, COUNT(p.PersonID) AS Sheltered,
            ROUND(100.0*COUNT(p.PersonID)/c.Capacity,1) AS PctFull
     FROM Camp c LEFT JOIN Family f ON f.CampID=c.CampID LEFT JOIN Person p ON p.FamilyID=f.FamilyID
     GROUP BY c.CampID ORDER BY c.CampID"""),
 "unmet_needs": ("Unmet needs by camp (multi-table JOIN)",
  """SELECT c.CampName, f.HeadOfFamily AS Family, i.ItemName AS Item,
            n.Quantity - COALESCE(SUM(d.Quantity),0) AS Remaining, n.Status
     FROM Need n JOIN Family f ON f.FamilyID=n.FamilyID JOIN Camp c ON c.CampID=f.CampID
          JOIN ReliefItem i ON i.ItemID=n.ItemID LEFT JOIN Distribution d ON d.NeedID=n.NeedID
     WHERE n.Status <> 'Fulfilled' GROUP BY n.NeedID ORDER BY c.CampID, f.FamilyID"""),
 "stock_alerts": ("Total stock per item with low-stock flag (aggregate + CASE)",
  """SELECT i.ItemName, i.Unit, SUM(s.Quantity) AS TotalQty,
            CASE WHEN SUM(s.Quantity) <= 30 THEN 'LOW' ELSE 'OK' END AS Level
     FROM Stock s JOIN ReliefItem i ON i.ItemID=s.ItemID GROUP BY i.ItemID ORDER BY TotalQty"""),
 "audit_trail": ("Distribution audit trail (traceability)",
  """SELECT d.DistributionID AS ID, d.DistDate AS Date, f.HeadOfFamily AS Family, i.ItemName AS Item,
            d.Quantity AS Qty, w.WarehouseName AS FromWarehouse, v.FullName AS Volunteer
     FROM Distribution d JOIN Need n ON n.NeedID=d.NeedID JOIN Family f ON f.FamilyID=n.FamilyID
          JOIN ReliefItem i ON i.ItemID=n.ItemID JOIN Stock s ON s.StockID=d.StockID
          JOIN Warehouse w ON w.WarehouseID=s.WarehouseID JOIN Volunteer v ON v.VolunteerID=d.VolunteerID
     ORDER BY d.DistributionID"""),
 "volunteer_load": ("Volunteer workload (subquery)",
  """SELECT v.FullName, v.Skill,
            (SELECT COUNT(*) FROM Distribution d WHERE d.VolunteerID=v.VolunteerID) AS Distributions,
            (SELECT GROUP_CONCAT(c.CampName) FROM Assignment a JOIN Camp c ON c.CampID=a.CampID
              WHERE a.VolunteerID=v.VolunteerID AND a.EndDate IS NULL) AS ActiveCamp
     FROM Volunteer v ORDER BY Distributions DESC"""),
 "no_aid": ("Families that have received no aid (NOT EXISTS)",
  """SELECT f.FamilyID, f.HeadOfFamily, c.CampName FROM Family f JOIN Camp c ON c.CampID=f.CampID
     WHERE NOT EXISTS (SELECT 1 FROM Need n JOIN Distribution d ON d.NeedID=n.NeedID WHERE n.FamilyID=f.FamilyID)"""),
}

def report(con, key):
    title, sql = REPORTS[key]
    cols, rows = query(con, sql)
    return f"{title}\n{table(cols, rows)}"

if __name__ == "__main__":
    con = connect()
    keys = sys.argv[1:] or list(REPORTS)
    for k in keys:
        print(report(con, k)); print()

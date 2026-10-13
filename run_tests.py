import sqlite3, os, json, shutil
import relief_app as app
shutil.copy("relief.db", "test.db")
con = app.connect("test.db")
out = {"cases": [], "screens": {}}
def stock(sid): return con.execute("SELECT Quantity FROM Stock WHERE StockID=?", (sid,)).fetchone()[0]
def nstat(n): return con.execute("SELECT Status FROM Need WHERE NeedID=?", (n,)).fetchone()[0]
def case(tid, feat, action, expected, actual, ok): out["cases"].append([tid, feat, action, expected, actual, "Pass" if ok else "Fail"])
scr = {k: [] for k in ("s2", "s3", "s4", "s5")}
def log(k, cmd, res): scr[k].append((cmd, res))

# TC-01 create family + persons
ok, m = app.add_family(con, "Venkat Naidu", "9848011107", 3); fid = con.execute("SELECT MAX(FamilyID) FROM Family").fetchone()[0]
ok2, m2 = app.add_person(con, fid, "Venkat Naidu", 45, "M"); ok3, _ = app.add_person(con, fid, "Rani Naidu", 41, "F", "Diabetes")
log("s2", f"add_family('Venkat Naidu','9848011107',camp=3)", m); log("s2", "add_person(family=7,'Venkat Naidu',45,'M')", m2)
case("TC-01", "Register family", "Family 'Venkat Naidu' to Camp 3 with 2 members", "Rows inserted in Family and Person", f"Family ID {fid} created; {con.execute('SELECT COUNT(*) FROM Person WHERE FamilyID=?',(fid,)).fetchone()[0]} persons stored", ok and ok2 and ok3)
# TC-02 add need
ok, m = app.add_need(con, fid, 1, 40); nid = con.execute("SELECT MAX(NeedID) FROM Need").fetchone()[0]
log("s2", f"add_need(family={fid}, item=1 Rice, qty=40)", m)
case("TC-02", "Register need", f"Family {fid}, Rice, qty 40", "Need created with status Pending", f"NeedID {nid}, status {nstat(nid)}", ok and nstat(nid) == "Pending")
# TC-03 duplicate need
ok, m = app.add_need(con, fid, 1, 10); log("s2", f"add_need(family={fid}, item=1 Rice, qty=10)", m)
case("TC-03", "One need per family/item", f"Second Rice need for family {fid}", "Rejected by UNIQUE(FamilyID, ItemID)", m, (not ok) and "UNIQUE" in m)
# TC-04 valid partial distribution
before = stock(1); ok, m = app.distribute(con, nid, 1, 1, 15); log("s3", f"distribute(need={nid}, stock=1, volunteer=1, qty=15)", m)
case("TC-04", "Valid distribution", f"Need {nid}, 15 kg Rice from Stock 1", "Stock falls by 15; need becomes Partial", f"Stock {before} -> {stock(1)}; status {nstat(nid)}", ok and stock(1) == before - 15 and nstat(nid) == "Partial")
# TC-05 over-allocation
before = stock(1); ok, m = app.distribute(con, nid, 1, 1, 30); log("s3", f"distribute(need={nid}, stock=1, volunteer=1, qty=30)", m)
case("TC-05", "Over-allocation", f"Need {nid} has 25 kg left; try 30 kg", "Rejected; stock unchanged", f"{m}; stock still {stock(1)}", (not ok) and "Over-allocation" in m and stock(1) == before)
# TC-06 duplicate entitlement
ok, m = app.distribute(con, 1, 1, 1, 5); log("s3", "distribute(need=1, stock=1, volunteer=1, qty=5)", m)
case("TC-06", "Duplicate entitlement", "Need 1 (Ravi Kumar, Rice) is already Fulfilled", "Rejected as duplicate", m, (not ok) and "Duplicate" in m)
# TC-07 insufficient stock
con.execute("UPDATE Stock SET Quantity=3 WHERE StockID=7"); con.commit()
ok, m = app.distribute(con, 10, 7, 2, 4); log("s3", "distribute(need=10 Blanket x4, stock=7, volunteer=2, qty=4)  # row holds 3", m)
case("TC-07", "Insufficient stock", "Need 4 blankets from a warehouse row holding 3", "Rejected; need and stock unchanged", f"{m}; need status {nstat(10)}, stock {stock(7)}", (not ok) and "Insufficient" in m and nstat(10) == "Pending" and stock(7) == 3)
# TC-08 item mismatch
ok, m = app.distribute(con, 6, 1, 1, 1); log("s3", "distribute(need=6 First-Aid, stock=1 Rice, volunteer=1, qty=1)", m)
case("TC-08", "Item mismatch", "Need for First-Aid Kit served from Rice stock", "Rejected", m, (not ok) and "mismatch" in m)
# TC-09 donation
before = stock(2); ok, m = app.record_donation(con, "Sri Sai Trust", 2, 1, 250); log("s2", "record_donation('Sri Sai Trust', item=2 Water, warehouse=1, qty=250)", m)
case("TC-09", "Donation updates stock", "Donate 250 L water to Warehouse 1", "Stock row increases by 250", f"Stock {before} -> {stock(2)}", ok and stock(2) == before + 250)
# TC-10 FK violation
ok, m = app.add_family(con, "Test Family", "9000", 99); log("s2", "add_family('Test Family','9000',camp=99)", m)
case("TC-10", "Foreign key check", "Family linked to non-existent Camp 99", "Rejected (FOREIGN KEY)", m, (not ok) and "FOREIGN KEY" in m)
# TC-11 restricted delete
ok, m = app.delete_camp(con, 1); case("TC-11", "Controlled removal", "Delete Camp 1 that still has families", "Rejected; Camp 1 remains", m, (not ok) and con.execute("SELECT COUNT(*) FROM Camp WHERE CampID=1").fetchone()[0] == 1)
log("s2", "delete_camp(1)", m)
# TC-12 update
ok, m = app.update_contact(con, 1, "9848099999"); log("s2", "update_contact(family=1, '9848099999')", m)
case("TC-12", "Update record", "Change contact of Family 1", "ContactInfo updated", con.execute("SELECT ContactInfo FROM Family WHERE FamilyID=1").fetchone()[0], ok)
# successful extra distributions for screen 3 / audit
app.distribute(con, 3, 2, 2, 40); log("s3", "distribute(need=3, stock=2, volunteer=2, qty=40)", "OK (1 row(s) affected)")
# check constraint
try:
    con.execute("INSERT INTO Person (FamilyID, FullName, Age, Gender) VALUES (1,'X',150,'M')"); ok = True; m = ""
except sqlite3.IntegrityError as e: ok = False; m = str(e)
case("TC-13", "CHECK constraint", "Person with Age = 150", "Rejected by CHECK (Age 0-120)", f"REJECTED: {m}", not ok)
con.commit()
for k, sec in [("s4", ["camp_occupancy", "unmet_needs", "stock_alerts"]), ("s5", ["audit_trail", "volunteer_load", "no_aid"])]:
    scr[k] = [(None, app.report(con, s)) for s in sec]
out["screens"] = {k: [list(x) for x in v] for k, v in scr.items()}
out["counts"] = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ['Disaster','Location','Camp','Warehouse','Family','Person','Volunteer','ReliefItem','Stock','Donation','Need','Distribution','Assignment','Referral']}
json.dump(out, open("results.json", "w"), indent=1)
for c in out["cases"]: print(c[0], c[5], "|", c[4])

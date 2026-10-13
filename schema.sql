-- Disaster Relief Resource & Camp Management System : schema (SQLite 3)
PRAGMA foreign_keys = ON;

CREATE TABLE Disaster (
    DisasterID   INTEGER PRIMARY KEY AUTOINCREMENT,
    DisasterName TEXT NOT NULL UNIQUE,
    DisasterType TEXT NOT NULL CHECK (DisasterType IN ('Flood','Cyclone','Earthquake','Drought','Fire')),
    StartDate    DATE NOT NULL,
    Severity     TEXT NOT NULL CHECK (Severity IN ('Low','Medium','High','Critical')),
    Status       TEXT NOT NULL DEFAULT 'Active' CHECK (Status IN ('Active','Closed'))
);
CREATE TABLE Location (
    LocationID INTEGER PRIMARY KEY AUTOINCREMENT,
    Village    TEXT NOT NULL,
    District   TEXT NOT NULL,
    State      TEXT NOT NULL DEFAULT 'Telangana',
    DisasterID INTEGER NOT NULL REFERENCES Disaster(DisasterID) ON DELETE RESTRICT,
    UNIQUE (Village, District, DisasterID)
);
CREATE TABLE Camp (
    CampID     INTEGER PRIMARY KEY AUTOINCREMENT,
    CampName   TEXT NOT NULL UNIQUE,
    LocationID INTEGER NOT NULL REFERENCES Location(LocationID) ON DELETE RESTRICT,
    Capacity   INTEGER NOT NULL CHECK (Capacity > 0),
    Status     TEXT NOT NULL DEFAULT 'Open' CHECK (Status IN ('Open','Full','Closed'))
);
CREATE TABLE Warehouse (
    WarehouseID   INTEGER PRIMARY KEY AUTOINCREMENT,
    WarehouseName TEXT NOT NULL UNIQUE,
    LocationID    INTEGER NOT NULL REFERENCES Location(LocationID) ON DELETE RESTRICT,
    ManagerName   TEXT NOT NULL
);
CREATE TABLE Family (
    FamilyID     INTEGER PRIMARY KEY AUTOINCREMENT,
    HeadOfFamily TEXT NOT NULL,
    ContactInfo  TEXT,
    CampID       INTEGER NOT NULL REFERENCES Camp(CampID) ON DELETE RESTRICT,
    RegisteredOn DATE NOT NULL DEFAULT CURRENT_DATE
);
CREATE TABLE Person (
    PersonID         INTEGER PRIMARY KEY AUTOINCREMENT,
    FamilyID         INTEGER NOT NULL REFERENCES Family(FamilyID) ON DELETE CASCADE,
    FullName         TEXT NOT NULL,
    Age              INTEGER NOT NULL CHECK (Age BETWEEN 0 AND 120),
    Gender           TEXT NOT NULL CHECK (Gender IN ('F','M','O')),
    MedicalCondition TEXT DEFAULT 'None'
);
CREATE TABLE Volunteer (
    VolunteerID INTEGER PRIMARY KEY AUTOINCREMENT,
    FullName    TEXT NOT NULL,
    Phone       TEXT NOT NULL UNIQUE,
    Skill       TEXT NOT NULL,
    Status      TEXT NOT NULL DEFAULT 'Available' CHECK (Status IN ('Available','Assigned','Inactive'))
);
CREATE TABLE ReliefItem (
    ItemID   INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemName TEXT NOT NULL UNIQUE,
    Category TEXT NOT NULL CHECK (Category IN ('Food','Water','Shelter','Clothing','Medical')),
    Unit     TEXT NOT NULL
);
CREATE TABLE Stock (
    StockID     INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemID      INTEGER NOT NULL REFERENCES ReliefItem(ItemID) ON DELETE RESTRICT,
    WarehouseID INTEGER NOT NULL REFERENCES Warehouse(WarehouseID) ON DELETE RESTRICT,
    Quantity    INTEGER NOT NULL DEFAULT 0 CHECK (Quantity >= 0),
    LastUpdated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (ItemID, WarehouseID)
);
CREATE TABLE Donation (
    DonationID   INTEGER PRIMARY KEY AUTOINCREMENT,
    DonorName    TEXT NOT NULL,
    ItemID       INTEGER NOT NULL REFERENCES ReliefItem(ItemID) ON DELETE RESTRICT,
    WarehouseID  INTEGER NOT NULL REFERENCES Warehouse(WarehouseID) ON DELETE RESTRICT,
    Quantity     INTEGER NOT NULL CHECK (Quantity > 0),
    DonationDate DATE NOT NULL DEFAULT CURRENT_DATE
);
CREATE TABLE Need (
    NeedID   INTEGER PRIMARY KEY AUTOINCREMENT,
    FamilyID INTEGER NOT NULL REFERENCES Family(FamilyID) ON DELETE CASCADE,
    ItemID   INTEGER NOT NULL REFERENCES ReliefItem(ItemID) ON DELETE RESTRICT,
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    Status   TEXT NOT NULL DEFAULT 'Pending' CHECK (Status IN ('Pending','Partial','Fulfilled')),
    UNIQUE (FamilyID, ItemID)
);
CREATE TABLE Distribution (
    DistributionID INTEGER PRIMARY KEY AUTOINCREMENT,
    NeedID         INTEGER NOT NULL REFERENCES Need(NeedID) ON DELETE RESTRICT,
    StockID        INTEGER NOT NULL REFERENCES Stock(StockID) ON DELETE RESTRICT,
    VolunteerID    INTEGER NOT NULL REFERENCES Volunteer(VolunteerID) ON DELETE RESTRICT,
    Quantity       INTEGER NOT NULL CHECK (Quantity > 0),
    DistDate       DATE NOT NULL DEFAULT CURRENT_DATE
);
CREATE TABLE Assignment (
    AssignmentID INTEGER PRIMARY KEY AUTOINCREMENT,
    VolunteerID  INTEGER NOT NULL REFERENCES Volunteer(VolunteerID) ON DELETE RESTRICT,
    CampID       INTEGER NOT NULL REFERENCES Camp(CampID) ON DELETE RESTRICT,
    Role         TEXT NOT NULL,
    StartDate    DATE NOT NULL,
    EndDate      DATE,
    CHECK (EndDate IS NULL OR EndDate >= StartDate)
);
CREATE TABLE Referral (
    ReferralID   INTEGER PRIMARY KEY AUTOINCREMENT,
    PersonID     INTEGER NOT NULL REFERENCES Person(PersonID) ON DELETE CASCADE,
    CampID       INTEGER NOT NULL REFERENCES Camp(CampID) ON DELETE RESTRICT,
    Facility     TEXT NOT NULL,
    Reason       TEXT NOT NULL,
    ReferralDate DATE NOT NULL DEFAULT CURRENT_DATE,
    Status       TEXT NOT NULL DEFAULT 'Open' CHECK (Status IN ('Open','Attended','Closed'))
);

-- Business-rule triggers --------------------------------------------------
CREATE TRIGGER trg_dist_validate BEFORE INSERT ON Distribution
BEGIN
    SELECT CASE WHEN (SELECT ItemID FROM Need WHERE NeedID = NEW.NeedID)
                  <> (SELECT ItemID FROM Stock WHERE StockID = NEW.StockID)
           THEN RAISE(ABORT, 'Item mismatch: stock item differs from the needed item') END;
    SELECT CASE WHEN (SELECT Status FROM Need WHERE NeedID = NEW.NeedID) = 'Fulfilled'
           THEN RAISE(ABORT, 'Duplicate entitlement: need already fulfilled') END;
    SELECT CASE WHEN NEW.Quantity > (SELECT n.Quantity - COALESCE((SELECT SUM(d.Quantity) FROM Distribution d
                                     WHERE d.NeedID = n.NeedID), 0) FROM Need n WHERE n.NeedID = NEW.NeedID)
           THEN RAISE(ABORT, 'Over-allocation: quantity exceeds remaining need') END;
    SELECT CASE WHEN NEW.Quantity > (SELECT Quantity FROM Stock WHERE StockID = NEW.StockID)
           THEN RAISE(ABORT, 'Insufficient stock in selected warehouse') END;
END;

CREATE TRIGGER trg_dist_apply AFTER INSERT ON Distribution
BEGIN
    UPDATE Stock SET Quantity = Quantity - NEW.Quantity, LastUpdated = CURRENT_TIMESTAMP
     WHERE StockID = NEW.StockID;
    UPDATE Need SET Status = CASE
        WHEN (SELECT SUM(Quantity) FROM Distribution WHERE NeedID = NEW.NeedID) >= Quantity THEN 'Fulfilled'
        ELSE 'Partial' END
     WHERE NeedID = NEW.NeedID;
END;

CREATE TRIGGER trg_donation_stock AFTER INSERT ON Donation
BEGIN
    INSERT INTO Stock (ItemID, WarehouseID, Quantity) VALUES (NEW.ItemID, NEW.WarehouseID, NEW.Quantity)
    ON CONFLICT (ItemID, WarehouseID)
    DO UPDATE SET Quantity = Quantity + NEW.Quantity, LastUpdated = CURRENT_TIMESTAMP;
END;

CREATE INDEX idx_family_camp ON Family(CampID);
CREATE INDEX idx_need_family ON Need(FamilyID);
CREATE INDEX idx_dist_need   ON Distribution(NeedID);

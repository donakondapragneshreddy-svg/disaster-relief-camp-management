-- Representative sample data (illustrative)
INSERT INTO Disaster (DisasterName, DisasterType, StartDate, Severity) VALUES
 ('Manjeera Basin Floods 2026','Flood','2026-09-28','Critical'),
 ('Gajwel Cyclone Spell 2026','Cyclone','2026-10-02','High');
INSERT INTO Location (Village, District, DisasterID) VALUES
 ('Siddipet','Siddipet',1),
 ('Husnabad','Siddipet',1),
 ('Gajwel','Siddipet',2),
 ('Karimnagar','Karimnagar',1);
INSERT INTO Camp (CampName, LocationID, Capacity) VALUES
 ('Siddipet Relief Camp A',1,300),('Husnabad Camp B',2,180),('Gajwel Camp C',3,220);
INSERT INTO Warehouse (WarehouseName, LocationID, ManagerName) VALUES
 ('Siddipet Central Warehouse',1,'K. Srinivas'),('Karimnagar Depot',4,'M. Fatima');
INSERT INTO ReliefItem (ItemName, Category, Unit) VALUES
 ('Rice','Food','kg'),('Drinking Water','Water','litre'),('Blanket','Clothing','piece'),
 ('Tarpaulin Tent','Shelter','piece'),('First-Aid Kit','Medical','kit'),('Cooking Oil','Food','litre');
INSERT INTO Family (HeadOfFamily, ContactInfo, CampID, RegisteredOn) VALUES
 ('Ravi Kumar','9848011101',1,'2026-09-29'),('Lakshmi Devi','9848011102',1,'2026-09-29'),
 ('Anwar Khan','9848011103',2,'2026-09-30'),('Sunita Reddy','9848011104',2,'2026-09-30'),
 ('Mahesh Goud','9848011105',3,'2026-10-03'),('Padma Rao','9848011106',3,'2026-10-03');
INSERT INTO Person (FamilyID, FullName, Age, Gender, MedicalCondition) VALUES
 (1,'Ravi Kumar',42,'M','None'),(1,'Sridevi Kumar',38,'F','None'),(1,'Arjun Kumar',14,'M','None'),(1,'Meena Kumar',9,'F','Asthma'),(1,'Kamala Bai',68,'F','Diabetes'),
 (2,'Lakshmi Devi',55,'F','Hypertension'),(2,'Vamsi Devi',27,'M','None'),(2,'Harini Devi',4,'F','None'),(2,'Kiran Devi',30,'F','None'),
 (3,'Anwar Khan',47,'M','None'),(3,'Shabana Khan',44,'F','None'),(3,'Imran Khan',20,'M','None'),(3,'Zoya Khan',16,'F','None'),(3,'Aliya Khan',8,'F','None'),(3,'Salma Bi',72,'F','Arthritis'),
 (4,'Sunita Reddy',35,'F','None'),(4,'Teja Reddy',11,'M','None'),(4,'Nandini Reddy',2,'F','None'),
 (5,'Mahesh Goud',50,'M','None'),(5,'Yadamma Goud',46,'F','None'),(5,'Bhaskar Goud',22,'M','None'),(5,'Ramya Goud',19,'F','None'),(5,'Chandu Goud',12,'M','None'),(5,'Pooja Goud',6,'F','None'),(5,'Narsamma',75,'F','Heart condition'),
 (6,'Padma Rao',63,'F','Diabetes'),(6,'Sai Rao',31,'M','None');
INSERT INTO Volunteer (FullName, Phone, Skill, Status) VALUES
 ('Anitha Rao','9000000001','Logistics','Assigned'),('Imran Shaikh','9000000002','Driver','Assigned'),
 ('Suresh Babu','9000000003','Medical Aid','Assigned'),('Divya Nair','9000000004','Registration','Assigned'),
 ('Karthik Yadav','9000000005','Cooking','Available');
INSERT INTO Assignment (VolunteerID, CampID, Role, StartDate, EndDate) VALUES
 (1,1,'Stores in-charge','2026-09-29',NULL),(2,1,'Transport','2026-09-29',NULL),
 (3,2,'First-aid desk','2026-09-30',NULL),(4,2,'Registration desk','2026-09-30','2026-10-10'),
 (4,3,'Registration desk','2026-10-11',NULL),(1,3,'Stores in-charge','2026-10-03','2026-10-08');
-- Opening stock (before donations)
INSERT INTO Stock (ItemID, WarehouseID, Quantity) VALUES
 (1,1,400),(2,1,900),(3,1,40),(4,2,12),(5,2,8),(1,2,150),(3,2,9),(6,1,60);
INSERT INTO Donation (DonorName, ItemID, WarehouseID, Quantity, DonationDate) VALUES
 ('Rotary Club Siddipet',1,1,100,'2026-10-05'),('Telangana Red Cross',5,2,20,'2026-10-06'),
 ('Hyderabad Textile Assn.',3,1,60,'2026-10-07'),('Anonymous',2,1,300,'2026-10-08'),('Lions Club Karimnagar',4,2,10,'2026-10-09');
INSERT INTO Need (FamilyID, ItemID, Quantity) VALUES
 (1,1,50),(1,3,5),(2,2,80),(3,4,1),(3,1,60),(4,5,1),(5,2,100),(5,3,7),(6,1,20),(2,3,4),(4,6,5),(6,5,1);
-- Distributions (validated and applied by triggers)
INSERT INTO Distribution (NeedID, StockID, VolunteerID, Quantity, DistDate) VALUES
 (1,1,1,50,'2026-10-09'),(2,3,1,2,'2026-10-10'),(5,6,2,20,'2026-10-10'),(7,2,2,100,'2026-10-11'),(9,1,1,20,'2026-10-11');
INSERT INTO Referral (PersonID, CampID, Facility, Reason, ReferralDate) VALUES
 (4,1,'Area Hospital Siddipet','Asthma attack after flooding','2026-10-04'),
 (15,2,'PHC Husnabad','Joint pain, mobility support','2026-10-05'),
 (25,3,'District Hospital Gajwel','Cardiac check-up','2026-10-06');

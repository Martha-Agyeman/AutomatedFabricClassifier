
CREATE DATABASE garment_sustainability;
USE garment_sustainability;


CREATE TABLE FABRIC (
    fabric_id VARCHAR(50) PRIMARY KEY,
    composition VARCHAR(255) NOT NULL,
    recyclability_index FLOAT NOT NULL
);


CREATE TABLE SCAN (
    scan_id VARCHAR(50) PRIMARY KEY,
    scan_time TIMESTAMP NOT NULL,
    condition_score FLOAT NOT NULL,
    fabric_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (fabric_id) REFERENCES FABRIC(fabric_id)
);

CREATE TABLE GARMENT (
    garment_id VARCHAR(50) PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    scan_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (scan_id) REFERENCES SCAN(scan_id)
);

CREATE TABLE RECOMMENDATION (
    rec_id VARCHAR(50) PRIMARY KEY,
    fabric_id VARCHAR(50) NOT NULL,
    instructions TEXT NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    FOREIGN KEY (fabric_id) REFERENCES FABRIC(fabric_id)
);
CREATE TABLE BLOCKCHAIN_AUDIT (
    block_id VARCHAR(100) PRIMARY KEY,
    transaction_hash VARCHAR(100) NOT NULL,
    scan_id VARCHAR(50) NOT NULL,
    garment_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    data_hash VARCHAR(100) NOT NULL,
    FOREIGN KEY (scan_id) REFERENCES SCAN(scan_id),
    FOREIGN KEY (garment_id) REFERENCES GARMENT(garment_id)
);


INSERT INTO BLOCKCHAIN_AUDIT (block_id, transaction_hash, scan_id, garment_id, timestamp, data_hash) VALUES
('BLK20250425001', '0x1234abcd...', 'SCN20250425001', 'GMT001', '2025-04-25 09:16:05', 'a1b2c3d4...'),
('BLK20250425002', '0x5678efgh...', 'SCN20250425002', 'GMT002', '2025-04-25 10:23:12', 'e5f6g7h8...'),
('BLK20250425003', '0x9012ijkl...', 'SCN20250425003', 'GMT003', '2025-04-25 11:06:30', 'i9j0k1l2...');


INSERT INTO FABRIC (fabric_id, composition, recyclability_index) VALUES
('FAB001', '100% Organic Cotton', 0.85),
('FAB002', '70% Polyester, 30% Recycled PET', 0.65),
('FAB003', '100% Merino Wool', 0.75),
('FAB004', '50% Linen, 50% Hemp', 0.90),
('FAB005', '65% Viscose, 35% Nylon', 0.55);


INSERT INTO SCAN (scan_id, scan_time, condition_score, fabric_id) VALUES
('SCN20250425001', '2025-04-25 09:15:32', 8.7, 'FAB001'),
('SCN20250425002', '2025-04-25 10:22:45', 6.5, 'FAB002'),
('SCN20250425003', '2025-04-25 11:05:18', 7.2, 'FAB003'),
('SCN20250425004', '2025-04-25 13:42:56', 9.1, 'FAB004'),
('SCN20250425005', '2025-04-25 15:30:10', 5.8, 'FAB005'),
('SCN20250425006', '2025-04-25 16:45:22', 7.9, 'FAB001');

INSERT INTO GARMENT (garment_id, type, scan_id) VALUES
('GMT001', 'T-Shirt', 'SCN20250425001'),
('GMT002', 'Dress Shirt', 'SCN20250425002'),
('GMT003', 'Sweater', 'SCN20250425003'),
('GMT004', 'Pants', 'SCN20250425004'),
('GMT005', 'Blouse', 'SCN20250425005'),
('GMT006', 'Skirt', 'SCN20250425006');


INSERT INTO RECOMMENDATION (rec_id, fabric_id, instructions, difficulty) VALUES
('REC001', 'FAB001', 'Compost after removing non-organic labels and stitching', 'Easy'),
('REC002', 'FAB002', 'Mechanical recycling - shred and melt to create new polyester fibers', 'Medium'),
('REC003', 'FAB003', 'Repair and reuse - wool is highly durable and can be felted for new products', 'Hard'),
('REC004', 'FAB004', 'Chemical recycling - break down into cellulose fibers for new textiles', 'Medium'),
('REC005', 'FAB005', 'Downcycling into insulation material or industrial rags', 'Easy'),
('REC006', 'FAB001', 'Upcycle into cleaning cloths or craft materials', 'Easy');
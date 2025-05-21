# Fabric Detection System - User Manual

## Table of Contents
1. [System Overview](#system-overview)
2. [Using the Interface](#using-the-interface)
3. [Blockchain Verification](#blockchain-verification)
4. [Maintenance](#maintenance)
5. [FAQs](#faqs)

---

## System Overview
The system provides:
- **Automatic fabric detection** via camera
- **Clothing classification** using ML
- **Blockchain-recorded** scans
- **Sustainability recommendations**


---

## Using the Interface
### 1. Home Screen
- Live camera feed
- Status indicators for:
  - Blockchain connection
  - Arduino connection
  - Camera status

### 2. Detection Process
1. Place garment under camera
2. System auto-detects via Arduino trigger
3. Results appear in real-time:
   - Fabric type (e.g., "Cotton - 95% confidence")
   - Garment type (e.g., "T-shirt - 89% confidence")
   - Care instructions
   - Blockchain TX hash

### 3. Saving Results
- All scans are automatically:
  - Saved to database
  - Recorded on blockchain
- Access past scans via database ID or TX hash

---

## Blockchain Verification
To verify a scan:
1. Open Ganache UI
2. Go to "Transactions" tab
3. Search by transaction hash (shown in results)
4. View details:
   - Block number
   - Timestamp
   - Input data (decoded)

Example verification workflow:
    User->>System: Triggers scan
    System->>Blockchain: Creates TX
    Blockchain-->>System: Returns TX hash
    System->>User: Displays results
    User->>Ganache: Verifies TX
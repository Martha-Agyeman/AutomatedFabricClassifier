# Fabric Detection System - Complete Setup Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)  
3. [Database Configuration](#database-configuration)  
4. [Blockchain Setup](#blockchain-setup)  
5. [Hardware Setup](#hardware-setup)  
6. [Software Configuration](#software-configuration)  
7. [Running the System](#running-the-system)  
8. [Verification](#verification)  
9. [Troubleshooting](#troubleshooting)  

---

## System Requirements

### Hardware
- ESP32, Ultrasonic Sensor, Breadboard and wires, Arduino IDE with USB cable  
- 1080p webcam (Logitech C920 recommended)  
- Computer with available USB 3.0 ports  

### Software Dependencies
| Component       | Version  | Installation Link                     |
|----------------|----------|---------------------------------------|
| Python         | 3.8+     | [python.org](https://www.python.org/downloads/) |
| MySQL          | 8.0+     | [mysql.com](https://dev.mysql.com/downloads/) |
| Node.js        | 16+      | [nodejs.org](https://nodejs.org/)     |
| Ganache        | 2.7+     | [trufflesuite.com](https://trufflesuite.com/ganache/) |

---

## Installation

Commands run in Terminal

### 1. Clone the repository:
   git clone https://github.com/yourusername/fabric-detection-system.git
   cd fabric-detection-system

### 2. Set up Python environment:

   python -m venv venv

   For windows:
   source venv/bin/activate  
   pip install -r code/src/requirements.txt

### 3. Install Node.js dependencies:
   npm install -g truffle
   npm install @truffle/hdwallet-provider web3

---

## Database Configuration

### 1. Create MySQL database:
   ```sql
   CREATE DATABASE garment_sustainability;
   CREATE USER 'fabric_user'@'localhost' IDENTIFIED BY 'yourpassword';
   GRANT ALL PRIVILEGES ON garment_sustainability.* TO 'fabric_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
   

### 2. Import the schema**:
   mysql -u fabric_user -p garment_sustainability < resources/database_schema.sql
   

### 3. Configure connection** in `db_integration.py`:
   ```python
   conn = mysql.connector.connect(
       host='localhost',
       user='fabric_user',
       password='yourpassword',
       database='garment_sustainability'
   )
   ```

---

## Blockchain Setup

### 1. Launch Ganache:
   - Download from [trufflesuite.com/ganache](https://trufflesuite.com/ganache/)
   - Create workspace with default settings:
     - RPC Server: `http://127.0.0.1:7545`
     - Chain ID: `1337`

### 2. Deploy smart contracts:
   ```bash
   cd code/src/contracts
   truffle compile
   truffle migrate --network ganache
   ```

### 3. Update `.env`:
   ```ini
   GANACHE_RPC=http://127.0.0.1:7545
   CONTRACT_ADDRESS=0x123...abc # From deployment output
   PRIVATE_KEY=0xdf...12 # From Ganache accounts tab
   ```

---

## Hardware Setup

### Arduino Configuration

#### 1. Upload trigger sketch:
   ```arduino
   void setup() {
     Serial.begin(9600);
     pinMode(2, INPUT_PULLUP);
   }
   
   void loop() {
     if(digitalRead(2) == LOW) {
       Serial.println("TAKE_PICTURE");
       delay(1000);
     }
   }
   ```

#### 2. Identify port:
   - Windows: `COM3` (Check Device Manager)
   - Mac/Linux: `/dev/cu.usbmodem*` or `/dev/ttyUSB*`

#### 3. Update `app.py`:
   ```python
   ARDUINO_PORT = '/dev/cu.usbmodem14101' # Your actual port
   BAUD_RATE = 9600
   ```

### Camera Setup
#### 1. Test camera indices:
   ```python
   import cv2
   for i in range(3):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f"Camera index {i} works")
           cap.release()
   ```

#### 2. Configure in `app.py`:
   ```python
   CAMERA_INDEX = 0 # Use working index
   ```

---

## Software Configuration

### 1. Roboflow API:
   ```python
   API_KEY = "your_roboflow_api_key"
   MODEL_ID = "your_model_id/version"
   ```

### 2. Blockchain integration:
   - Copy ABI from `build/contracts/GarmentContract.json`
   - Paste into `blockchain_integration.py`

---

## Running the System

### 1. Start services:
   ```bash
   ganache &  # Start blockchain
   python code/src/app.py  # Start Flask server
   ```

### 2. Access interface:
   ```
   http://localhost:5001
   ```

---

## Verification

### System checks:
- Web interface shows green status indicators  
- Ganache displays active transactions  
- Arduino serial monitor logs "TAKE_PICTURE"  

### Test workflow:
1. Place fabric under camera  
2. Trigger Arduino  
3. Verify:
   - Database entry created  
   - Blockchain transaction appears  
   - Web UI updates  

---

## Troubleshooting

### Common Solutions
| Issue | Fix |
|-------|-----|
| Camera not detected | Try different USB port/index |
| Arduino connection failed | Verify port/baud rate |
| Blockchain errors | Check Ganache is running |
| Database failures | Verify MySQL service |

### Command Diagnostics
```bash
# Test MySQL connection
mysql -u fabric_user -p -e "SHOW DATABASES;"

# Check camera
v4l2-ctl --list-devices # Linux
ffmpeg -list_devices true -f dshow -i dummy # Windows
```

For additional support: marthagyeman14@gmail.com  
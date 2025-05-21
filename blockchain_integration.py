from web3 import Web3
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime

# Ganache connection setup
GANACHE_URL = "HTTP://127.0.0.1:7545" 
import json

with open('contract_abi.json') as f:
    CONTRACT_ABI = json.load(f)



CONTRACT_ADDRESS = "0xD50fFa21e120693748575Af354d378f7ecb657c4"  

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'garment_sustainability'
}

class BlockchainIntegrator:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
        self.contract = self.w3.eth.contract(
            address=CONTRACT_ADDRESS,
            abi=CONTRACT_ABI
        )
        self.account = self.w3.eth.accounts[0]  

    def get_scans_from_db(self, limit=10):
        """Retrieve recent scans from MySQL database"""
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT s.scan_id, s.scan_time, s.condition_score, 
                   f.common_name as fabric_type, g.type as garment_type,
                   r.instructions as recommendation
            FROM SCAN s
            JOIN FABRIC f ON s.fabric_id = f.fabric_id
            JOIN GARMENT g ON s.scan_id = g.scan_id
            LEFT JOIN RECOMMENDATION r ON f.fabric_id = r.fabric_id 
                                     AND (g.type = r.garment_type OR r.garment_type IS NULL)
            ORDER BY s.scan_time DESC
            LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
            
        except Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def prepare_blockchain_data(self, db_records):
        """Format database records for blockchain storage"""
        formatted = []
        for record in db_records:
            formatted.append({
                'scanId': record['scan_id'],
                'timestamp': int(record['scan_time'].timestamp()),
                'fabricType': record['fabric_type'],
                'garmentType': record['garment_type'],
                'conditionScore': float(record['condition_score']),
                'recommendation': record['recommendation'] or "No recommendation"
            })
        return formatted

    def upload_to_blockchain(self, data):
        """Store data on Ganache blockchain"""
        condition_score_int = int(float(data['conditionScore']) * 10000)
        try:
            tx_hash = self.contract.functions.storeScanData(
                data['scanId'],
                data['timestamp'],
                data['fabricType'],
                data['garmentType'],
                condition_score_int,
                data['recommendation']
            ).transact({
                'from': self.account,
                'gas': 1000000
            })
            return tx_hash.hex()
        except Exception as e:
            print(f"Blockchain error: {e}")
            return None

    def process_recent_scans(self):
        """Main method to fetch and upload scans"""
        db_records = self.get_scans_from_db()
        if not db_records:
            print("No scans found in database")
            return
            
        print(f"Found {len(db_records)} scans to process")
        
        for record in db_records:
            formatted = self.prepare_blockchain_data([record])[0]
            tx_hash = self.upload_to_blockchain(formatted)
            
            if tx_hash:
                print(f"Uploaded scan {record['scan_id']} in tx: {tx_hash}")
            else:
                print(f"Failed to upload scan {record['scan_id']}")

if __name__ == "__main__":
    integrator = BlockchainIntegrator()
    integrator.process_recent_scans()
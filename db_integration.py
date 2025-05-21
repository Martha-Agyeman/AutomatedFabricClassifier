import mysql.connector
from mysql.connector import Error
from datetime import datetime
import uuid

class GarmentDB:
    def __init__(self):
        self.connection = self._connect()
        
    def _connect(self):
        """Establish database connection"""
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',  
                password='',
                database='garment_sustainability'
            )
            print("Connected to Garment Sustainability database")
            return conn
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def save_detection(self, detection_data):
        """Save detection results to the garment sustainability database"""
        if not self.connection or not self.connection.is_connected():
            self.connection = self._connect()
            if not self.connection:
                return None
                
        try:
            cursor = self.connection.cursor()
            
            
            scan_id = f"SCN{datetime.now().strftime('%Y%m%d%H%M%S')}"
            garment_id = f"GMT{uuid.uuid4().hex[:6].upper()}"
            fabric_id = self._get_fabric_id(detection_data['fabric']['type'])
            
            
            scan_query = """
            INSERT INTO SCAN (
                scan_id, 
                scan_time, 
                condition_score, 
                fabric_id,
                image_path,
                confidence_score
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            fabric_conf = float(detection_data['fabric']['confidence'].strip('%')) / 100
            scan_values = (
                scan_id,
                datetime.now(),
                8.0,  # Default condition score
                fabric_id,
                detection_data['snapshot'],
                fabric_conf
            )
            cursor.execute(scan_query, scan_values)
            
            
            garment_query = """
            INSERT INTO GARMENT (
                garment_id,
                type,
                scan_id,
                confidence_score
            ) VALUES (%s, %s, %s, %s)
            """
            
            clothing_conf = float(detection_data['clothing']['confidence'].strip('%')) / 100
            garment_values = (
                garment_id,
                detection_data['clothing']['type'],
                scan_id,
                clothing_conf
            )
            cursor.execute(garment_query, garment_values)
            
            
            rec_query = """
            SELECT rec_id FROM RECOMMENDATION 
            WHERE fabric_id = %s AND (garment_type = %s OR garment_type IS NULL)
            LIMIT 1
            """
            cursor.execute(rec_query, (fabric_id, detection_data['clothing']['type']))
            rec = cursor.fetchone()
            
            if not rec:
                
                rec_id = f"REC{uuid.uuid4().hex[:6].upper()}"
                insert_rec = """
                INSERT INTO RECOMMENDATION (
                    rec_id,
                    fabric_id,
                    instructions,
                    difficulty,
                    garment_type
                ) VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_rec, (
                    rec_id,
                    fabric_id,
                    detection_data['care'],
                    'Medium',  # Default difficulty
                    detection_data['clothing']['type']
                ))
            
            
            block_id = f"BLK{datetime.now().strftime('%Y%m%d%H%M%S')}"
            blockchain_query = """
            INSERT INTO BLOCKCHAIN_AUDIT (
                block_id,
                transaction_hash,
                scan_id,
                garment_id,
                timestamp,
                data_hash
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(blockchain_query, (
                block_id,
                f"0x{uuid.uuid4().hex}",
                scan_id,
                garment_id,
                datetime.now(),
                f"hash{uuid.uuid4().hex[:10]}"
            ))
            
            self.connection.commit()
            print(f"Saved detection to database - Scan ID: {scan_id}, Garment ID: {garment_id}")
            return scan_id
            
        except Error as e:
            print(f"Database error: {e}")
            self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
    def _get_fabric_id(self, fabric_name):
        """Get fabric ID by common name, create if doesn't exist"""
        if not self.connection or not self.connection.is_connected():
            self.connection = self._connect()
            
        try:
            cursor = self.connection.cursor()
            
            # Try to find existing fabric
            query = "SELECT fabric_id FROM FABRIC WHERE common_name = %s LIMIT 1"
            cursor.execute(query, (fabric_name,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
                
            # Create new fabric if not found
            new_id = f"FAB{uuid.uuid4().hex[:6].upper()}"
            insert_query = """
            INSERT INTO FABRIC (
                fabric_id,
                composition,
                recyclability_index,
                common_name
            ) VALUES (%s, %s, %s, %s)
            """
            
         
            composition = f"100% {fabric_name}"
            recyclability = 0.7  # Default average recyclability
            
            cursor.execute(insert_query, (
                new_id,
                composition,
                recyclability,
                fabric_name
            ))
            
            self.connection.commit()
            return new_id
            
        except Error as e:
            print(f"Error getting fabric ID: {e}")
            return 'FAB000'  # Default unknown fabric ID
        finally:
            if cursor:
                cursor.close()


    def get_recommendations(self, fabric_name, garment_type):
        if not self.connection or not self.connection.is_connected():
            self.connection = self._connect()
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # First get fabric ID from common name
            fabric_query = "SELECT fabric_id FROM FABRIC WHERE common_name = %s LIMIT 1"
            cursor.execute(fabric_query, (fabric_name.lower(),))
            fabric = cursor.fetchone()
            
            if not fabric:
                return []
                
            # Get recommendations matching fabric and garment type
            rec_query = """
            SELECT * FROM RECOMMENDATION 
            WHERE fabric_id = %s 
            AND (garment_type = %s OR garment_type IS NULL)
            ORDER BY CASE WHEN garment_type IS NOT NULL THEN 0 ELSE 1 END
            """
            cursor.execute(rec_query, (fabric['fabric_id'], garment_type))
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error getting recommendations: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    db = GarmentDB()
    
    test_detection = {
        'fabric': {'type': 'cotton', 'confidence': '95.25%'},
        'clothing': {'type': 'T-shirt', 'confidence': '98.75%'},
        'care': 'Machine wash cold, tumble dry low',
        'snapshot': 'snapshots/snapshot_test.jpg'
    }
    
    scan_id = db.save_detection(test_detection)
    print(f"Saved with scan ID: {scan_id}")
    
    db.close()
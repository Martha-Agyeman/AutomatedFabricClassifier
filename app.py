from flask import Flask, render_template, Response
from flask import jsonify
import serial
import serial.tools.list_ports
from inference_sdk import InferenceHTTPClient
import cv2
import threading
import time
from werkzeug.serving import make_server
import os
from flask_socketio import SocketIO, emit
import tensorflow as tf
import numpy as np
from db_integration import GarmentDB


app = Flask(__name__)
socketio = SocketIO(app)

garment_db = GarmentDB() 
# Configuration
ARDUINO_PORT = '/dev/cu.usbserial-0001'  
BAUD_RATE = 9600
MODEL_ID = "fabricclassv2-0au2r/1"  
API_KEY = "D2EOvGCx0S0cIoLvoyCH"  
CAMERA_INDEX = 0  


# local clothing model
clothing_model = tf.keras.models.load_model('fashion_mnist_clothing_type_model.h5')
clothing_class_names = ['T-shirt', 'Trouser', 'Pullover', 'Dress', 'Coat', 
                       'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

# Initialize clients
client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=API_KEY
)

# Global variables for results
current_prediction = {
    'fabric': {
        'type': None,
        'confidence': None
    },
    'clothing': {
        'type': None,
        'confidence': None
    },
    'care': None,
    'snapshot': None,
    'error': None
}

class Camera:
    def __init__(self, index=0):
        print(f"Initializing camera with index {index}")
        self.camera = cv2.VideoCapture(index)
        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera")
        
       
        width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Camera initialized at {width}x{height} resolution")
        
      
        print("Warming up camera...")
        for i in range(5):
            ret, frame = self.camera.read()
            print(f"Warmup frame {i+1}: {'Success' if ret else 'Failed'}")
            if not ret:
                print("Warning: Failed to capture warmup frame")
            time.sleep(0.1)
        print("Camera ready")

    def capture_image(self, save_dir="static/images"):
        try:
            os.makedirs(save_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.jpg"
            filepath = os.path.join(save_dir, filename)
            
            ret, frame = self.camera.read()
            if ret:
                cv2.imwrite(filepath, frame)  # Save to disk
                _, buffer = cv2.imencode('.jpg', frame)
                print(f"Saved: {filepath}")
                return buffer.tobytes(), filename  
        except Exception as e:
            print(f"Save error: {e}")
        return None, None

    def get_frame(self):
        ret, frame = self.camera.read()
        if ret:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                return buffer.tobytes()
        return None

class ArduinoController:
    def __init__(self, port, baud_rate):
        self.port = port
        self.baud_rate = baud_rate
        self.arduino = None
        self.connect()
        self.last_trigger_time = 0
        self.trigger_cooldown = 10  # 10 second cooldown between triggers

    def connect(self):
        try:
            print(f"Attempting to connect to Arduino on {self.port}")
            self.arduino = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1,
                write_timeout=1
            )
            time.sleep(2)  
            self.arduino.reset_input_buffer()
            print("Arduino connected successfully")
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")
            self.arduino = None

    def check_for_trigger(self):
        if not self.arduino:
            print("Arduino not connected, attempting reconnect...")
            self.connect()
            return False
            
        try:
            current_time = time.time()
            if current_time - self.last_trigger_time < self.trigger_cooldown:
                print(f"Trigger cooldown: {self.trigger_cooldown - (current_time - self.last_trigger_time):.1f}s remaining")
                return False
                
           
            while self.arduino.in_waiting:
               
                raw_data = self.arduino.readline()
                
               
                try:
                    line = raw_data.decode('utf-8').strip()
                except UnicodeDecodeError:
                    line = raw_data.hex()  
                    print(f"Received non-UTF8 data: {line}")
                    continue
                    
                #print(f"Received from Arduino: {repr(line)}")  # Debug print
                
                if line == "TAKE_PICTURE":
                    print("Valid trigger received!")
                    self.last_trigger_time = current_time
                    return True
                    
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            self.arduino = None  
        except Exception as e:
            print(f"Unexpected error reading from Arduino: {e}")
            
        return False

camera = Camera(CAMERA_INDEX)
arduino = ArduinoController(ARDUINO_PORT, BAUD_RATE)

def preprocess_for_clothing_model(frame):
    """Prepare frame for Fashion MNIST model"""
    # Convert to grayscale and resize to 28x28
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)
    # Normalize and reshape for model input
    processed = resized.astype('float32') / 255.0
    return processed.reshape(1, 28, 28, 1)

def detect_clothing_type(frame):
    """Run local clothing classification"""
    processed = preprocess_for_clothing_model(frame)
    predictions = clothing_model.predict(processed)
    predicted_class = np.argmax(predictions[0])
    confidence = np.max(predictions[0])
    return clothing_class_names[predicted_class], float(confidence)

def detection_loop():
    global current_prediction
    
    print("Starting detection loop...")
    while True:
        try:
            if arduino.check_for_trigger():
                print("\n" + "="*50)
                print("Trigger detected! Starting capture sequence...")
                
                # Reset prediction at start
                current_prediction = {
                    'fabric': {'type': None, 'confidence': None},
                    'clothing': {'type': None, 'confidence': None},
                    'care': None,
                    'snapshot': None,
                    'error': None,
                    'db_status': None
                }
                
                #  Capture frame
                ret, frame = camera.camera.read()
                if not ret:
                    current_prediction['error'] = "Failed to capture frame"
                    socketio.emit('prediction_error', current_prediction)
                    continue
                
                #  Save snapshot
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                snapshot_dir = "static/snapshots"
                os.makedirs(snapshot_dir, exist_ok=True)
                snapshot_filename = f"snapshot_{timestamp}.jpg"
                snapshot_path = os.path.join(snapshot_dir, snapshot_filename)
                cv2.imwrite(snapshot_path, frame)
                current_prediction['snapshot'] = f"snapshots/{snapshot_filename}"
                
                #  Run both predictions
                try:
                    # Fabric prediction
                    fabric_results = client.infer(frame, model_id=MODEL_ID)
                    if fabric_results and fabric_results.get('predictions'):
                        fabric_pred = fabric_results['predictions'][0]
                        current_prediction['fabric'] = {
                            'type': fabric_pred['class'],
                            'confidence': f"{fabric_pred['confidence']*100:.2f}%"
                        }
                    
                    # Clothing prediction
                    clothing_type, clothing_conf = detect_clothing_type(frame)
                    current_prediction['clothing'] = {
                        'type': clothing_type,
                        'confidence': f"{clothing_conf*100:.2f}%"
                    }
                    
                    # Care instructions
                    if current_prediction['fabric']['type']:
                        current_prediction['care'] = get_care_instructions(
                            current_prediction['fabric']['type'],
                            current_prediction['clothing']['type']
                        )
                    
                    # Save to database if valid
                    if (current_prediction['fabric']['type'] and 
                        current_prediction['clothing']['type'] and
                        current_prediction['fabric'].get('confidence') and
                        current_prediction['clothing'].get('confidence')):
                        
                        scan_id = garment_db.save_detection(current_prediction)
                        if scan_id:
                            current_prediction['db_status'] = f"Saved to database (Scan ID: {scan_id})"
                            print(f"Saved to garment database with scan ID: {scan_id}")
                        else:
                            current_prediction['db_status'] = "Database save failed"
                            print("Warning: Failed to save to garment database")
                    
                    socketio.emit('update_prediction', current_prediction)

                    if scan_id:

                        from blockchain_integration import BlockchainIntegrator
                        blockchain = BlockchainIntegrator()
                        tx_hash = blockchain.upload_to_blockchain({
                            'scanId': scan_id,
                            'timestamp': int(time.time()),
                            'fabricType': current_prediction['fabric']['type'],
                            'garmentType': current_prediction['clothing']['type'],
                            'conditionScore': float(current_prediction['fabric']['confidence'].strip('%'))/100,
                            'recommendation': current_prediction['care']
                        })
                        if tx_hash:
                            current_prediction['blockchain_status'] = f"Uploaded to blockchain (TX: {tx_hash})"
                        else:
                            current_prediction['blockchain_status'] = "Blockchain upload failed"
                    
                except Exception as e:
                    current_prediction['error'] = str(e)
                    socketio.emit('prediction_error', current_prediction)
                
                print("="*50 + "\n")
                
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Detection loop error: {str(e)}")
            time.sleep(1)


def get_care_instructions(fabric_type, clothing_type):
    care_rules = {
        'cotton': {
            'T-shirt': 'Machine wash cold, tumble dry low',
            'Dress': 'Hand wash cold, lay flat to dry',
            'Shirt': 'Machine wash warm, iron medium heat'
        },
        'silk': {
            'Dress': 'Dry clean only',
            'Blouse': 'Hand wash cold with mild detergent'
        },
        'wool': {
            'Coat': 'Professional dry cleaning recommended',
            'Pullover': 'Hand wash cold, lay flat to dry'
        }
    }
    return care_rules.get(fabric_type.lower(), {}).get(
        clothing_type,
        'Check garment care label'
    )

# Start detection thread
detection_thread = threading.Thread(target=detection_loop)
detection_thread.daemon = True
detection_thread.start()

@app.route('/')
def index():
    return render_template('index.html', prediction=current_prediction)

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            frame = camera.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            time.sleep(0.05)
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_recommendations/<fabric_type>/<garment_type>')
def get_recommendations(fabric_type, garment_type):
    db = GarmentDB()
    try:
        recommendations = db.get_recommendations(fabric_type, garment_type)
        return jsonify(recommendations)
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return jsonify([])
    finally:
        db.close()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
    


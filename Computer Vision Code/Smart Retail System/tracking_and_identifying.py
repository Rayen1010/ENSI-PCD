import cv2
from decimal import Decimal, InvalidOperation
import numpy as np
import mediapipe as mp
from ultralytics import YOLO
from datetime import datetime
from bson.decimal128 import Decimal128
from collections import deque
import os
import time
import requests  # For making HTTP requests
import json      # For JSON handling

class ObjectTracker:

    def __init__(self):
        # Initialize directories
        self.create_directories()
        
        # Initialize models
        self.initialize_models()
        
        # Video setup
        self.setup_video_io()
        
        # Tracking variables
        self.initialize_tracking_variables()
        
    def send_customer_count_to_api(self, customer_id):
        """Send customer count to API endpoint"""
        api_url = "http://localhost:3000/api/pcd0/admin/affect-id"
        headers = {'Content-Type': 'application/json'}
        payload = {'customer_Id': customer_id}
        
        try:
            response = requests.post(
                api_url,
                data=json.dumps(payload),
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"Successfully sent customer count: {customer_id}")
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Failed to send to API: {str(e)}")

    @classmethod
    def send_customer_box_to_api(cls, data):
        """Send customer purchase data to API endpoint"""
        api_url = "http://localhost:3000/api/pcd0/admin/retrieve"
        headers = {'Content-Type': 'application/json'}

        # Helper function to convert Decimal128 and datetime objects
        def convert_for_json(obj):
            if isinstance(obj, Decimal128):
                return float(str(obj))  # Convert to float for JSON
            elif isinstance(obj, datetime):
                return obj.isoformat()  # Convert datetime to ISO string
            return obj

        # Prepare payload with proper serialization
        payload = {
            'customer_Id': data['customer_Id'],
            'box': [
                {
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'unit_price': convert_for_json(item['unit_price']),
                    'total_price': convert_for_json(item['total_price'])
                } 
                for item in data['box']
            ],
            'entry_date': convert_for_json(data['entry_date']),
            'processing_date': data['processing_date'],  # Assuming this is already a string
            'total_amount': convert_for_json(data['total_amount'])
        }

        try:
            response = requests.post(
                api_url,
                data=json.dumps(payload, default=convert_for_json),
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully Updated: {data['customer_Id']}")
                return True
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"🚨 Failed to send to API: {str(e)}")
            return False      

    def create_directories(self):
        """Create required directories if they don't exist"""
        os.makedirs('analyze_frames', exist_ok=True)
        os.makedirs('Output Videos', exist_ok=True)
        
    def initialize_models(self):
        """Initialize MediaPipe and YOLO models"""
        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # YOLO Model
        self.model = YOLO(r"Models\yolo11m.pt")
        
    def setup_video_io(self):
        """Set up video input and output"""
        # Input video
        self.video_path = r"Test Videos\besttest.mp4"
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            raise IOError(f"Cannot open video file: {self.video_path}")
            
        # Get video properties
        self.frame_width = int(self.cap.get(3))
        self.frame_height = int(self.cap.get(4))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Output video
        self.output_path = r"Output Videos\Tracking and Identifying3.mp4"
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(
            self.output_path, 
            self.fourcc, 
            self.fps, 
            (self.frame_width, self.frame_height))
            
        if not self.out.isOpened():
            raise IOError("Could not initialize video writer")
            
    def initialize_tracking_variables(self):
        """Initialize all tracking-related variables"""
        # Object tracking
        self.object_ids = {}
        self.table_bbox = None
        self.current_red_objects = set()
        
        # Hand tracking
        self.hand_ids = {}
        self.hand_position_history = deque(maxlen=10)
        
        # People counting
        self.person_ids_crossed = set()
        self.entry_counter = 0
        self.entrance_line_x = int(self.frame_width * 0.53)
        
        # Frame processing
        self.frame_skip = 3
        self.frame_count = 0
        self.capture_interval = 3  # seconds
        self.last_capture_time = time.time()
        self.frame_number = 0
        
    def is_on_table(self, object_bbox):
        """Check if an object is on the table"""
        if self.table_bbox is None:
            return False
            
        x1, y1, x2, y2 = object_bbox
        tx1, ty1, tx2, ty2 = self.table_bbox
        return y2 > ty1
        
    def update_hand_tracking(self, hand_id, new_position):
        """Update hand position with smoothing"""
        if hand_id not in self.hand_ids:
            self.hand_ids[hand_id] = deque(maxlen=10)
            
        self.hand_ids[hand_id].append(new_position)
        avg_position = np.mean(self.hand_ids[hand_id], axis=0)
        return tuple(map(int, avg_position))
        
    def is_crossing_entrance_line(self, center_x, track_id):
        """Check if a person is crossing the entrance line"""
        if track_id not in self.person_ids_crossed:
            if center_x > self.entrance_line_x:
                self.person_ids_crossed.add(track_id)
                return True
        return False
        
    def process_frame(self, frame):
        """Process a single frame"""
        # Convert to grayscale for optical flow (if needed)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Run YOLO tracking
        results = self.model.track(
            source=frame,
            classes=list(range(80)),
            tracker="botsort.yaml",
            persist=True
        )
        
        if results and results[0].boxes:
            self.process_detections(frame, results[0].boxes.data.cpu().numpy())
        
        # Display customer count in top-left corner (added this)
        cv2.putText(frame, f"Total Customers: {self.entry_counter}", 
                (20, 40),  # Position (x,y) - top-left corner
                cv2.FONT_HERSHEY_SIMPLEX, 
                1.0,  # Font scale (larger than before)
                (0, 255, 255),  # Yellow color
                2)  # Thickness
        
        return frame
        
    def process_detections(self, frame, detections):
        """Process all detections in a frame"""
        for det in detections:
            x1, y1, x2, y2, conf, class_id, track_id = det
            track_id = int(track_id)
            
            # Get object name based on class ID
            object_name = self.get_object_name(track_id)
            
            # Process person detection
            if track_id == 0:
                self.process_person(frame, x1, y1, x2, y2, track_id, object_name)
            # Process table detection
            elif track_id == 60:
                self.process_table(frame, x1, y1, x2, y2, object_name)
            # Process other objects
            else:
                self.process_object(frame, x1, y1, x2, y2, track_id, object_name)
                
    def get_object_name(self, track_id):
        """Get the name of an object based on its track ID"""
        object_names = {
            0:"Customer",
            60: "Table",
            24: "Bag",
            26: "Bag",
            44: "Spoon",
            38: "Tennis Racket",
            39: "Bottle of Water",
            41: "Cup"
        }
        return object_names.get(track_id)
        
    def process_person(self, frame, x1, y1, x2, y2, track_id, object_name):
        """Process a person detection"""
        # Check for entrance crossing
        center_x = int((x1 + x2) / 2)
        if self.is_crossing_entrance_line(center_x, track_id):
            self.entry_counter += 1
            print(f"People entered: {self.entry_counter}")
            # Send to API (added this)
            self.send_customer_count_to_api(self.entry_counter)
            
        # Hand detection
        self.detect_hands(frame)
        
        # Draw person bounding box
        color = (0, 255, 0)  # Green for person
        self.draw_bounding_box(frame, x1, y1, x2, y2, color, f"Customer {self.entry_counter}")
        
    def process_table(self, frame, x1, y1, x2, y2, object_name):
        """Process a table detection"""
        self.table_bbox = (x1, y1, x2, y2)
        color = (255, 0, 0)  # Blue for table
        self.draw_bounding_box(frame, x1, y1, x2, y2, color, object_name)
        
    def process_object(self, frame, x1, y1, x2, y2, track_id, object_name):
        """Process other object detections"""
        if self.table_bbox and not self.is_on_table([x1, y1, x2, y2]):
            color = (0, 0, 255)  # Red for objects not on table
            self.current_red_objects.add(track_id)
        else:
            color = (0, 255, 0)  # Green for objects on table
            
        self.draw_bounding_box(frame, x1, y1, x2, y2, color, object_name)
        
    def detect_hands(self, frame):
        """Detect and draw hand landmarks"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_hands = self.hands.process(rgb_frame)
        
        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                hand_id = len(self.hand_ids)
                hand_positions = [
                    (landmark.x * self.frame_width, landmark.y * self.frame_height) 
                    for landmark in hand_landmarks.landmark
                ]
                smoothed_hand_position = self.update_hand_tracking(hand_id, hand_positions[0])
                cv2.circle(frame, smoothed_hand_position, 5, (0, 0, 255), -1)
                
    def draw_bounding_box(self, frame, x1, y1, x2, y2, color, label):
        """Draw bounding box and label on frame"""
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(frame, label, (int(x1), int(y2) + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                   
    def save_frame_periodically(self, frame):
        """Save frame every specified interval"""
        current_time = time.time()
        if current_time - self.last_capture_time >= self.capture_interval:
            frame_filename = f"analyze_frames/frame_{self.frame_number:04d}.jpg"
            cv2.imwrite(frame_filename, frame)
            print(f"Saved frame to {frame_filename}")
            self.frame_number += 1
            self.last_capture_time = current_time
            
    def run(self):
        """Main processing loop"""
        print(f"Starting video processing: {self.video_path}")
        print(f"Frame dimensions: {self.frame_width}x{self.frame_height}")
        print(f"FPS: {self.fps}, Total frames: {self.total_frames}")
        
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
                
            self.frame_count += 1
            if self.frame_count % self.frame_skip != 0:
                continue
                
            # Process frame
            processed_frame = self.process_frame(frame)
            
            # Write to output video
            self.out.write(processed_frame)
            
            # Display
            cv2.imshow('Tracking Frame', processed_frame)
            
            # Save frame periodically
            self.save_frame_periodically(processed_frame)
            
            # Check for quit command
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        # Cleanup
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        print("Processing completed successfully")
        
        # Verify output file
        if os.path.exists(self.output_path):
            file_size = os.path.getsize(self.output_path)
            print(f"Output video created: {self.output_path} ({file_size} bytes)")
        else:
            print("Warning: Output video was not created")

if __name__ == "__main__":
    try:
        tracker = ObjectTracker()
        tracker.run()
    except Exception as e:
        print(f"Error: {str(e)}")
import cv2
import numpy as np
import os
import time
import requests
from dotenv import load_dotenv
from ultralytics import YOLO

class FireSmokeDetector:
    def __init__(self):
        # Load configuration
        load_dotenv()
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
        self.TELEGRAM_API_URL = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        # Initialize model
        self.model = YOLO(r"Models\best.pt")
        self.class_names = self.model.model.names
        
        # Video setup
        self.cap = cv2.VideoCapture(r'Test Videos\vid.mp4')
        self.frame_size = (1020, 500)
        self.writer = cv2.VideoWriter(
            r'Output Videos\Detection_output.mp4',
            cv2.VideoWriter_fourcc(*'mp4v'),
            self.cap.get(cv2.CAP_PROP_FPS),
            self.frame_size
        )
        
        # Alert system (fire only)
        self.last_alert_time = 0
        self.alert_cooldown = 10  # seconds
        self.frames_dir = 'alert_frames'
        os.makedirs(self.frames_dir, exist_ok=True)

    def draw_detections_with_masks(self, frame, results):
        """Draw bounding boxes with mask overlays"""
        fire_detected = False
        smoke_detected = False
        
        if results[0].boxes is not None and results[0].masks is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            masks = results[0].masks.xy
            
            overlay = frame.copy()
            
            for box, class_id, mask in zip(boxes, class_ids, masks):
                x1, y1, x2, y2 = map(int, box)
                class_name = self.class_names[class_id].lower()
                
                if 'fire' in class_name:
                    color = (0, 0, 255)  # Red for fire
                    label = "FIRE"
                    fire_detected = True
                elif 'smoke' in class_name:
                    color = (255, 0, 0)  # Blue for smoke
                    label = "SMOKE"
                    smoke_detected = True
                else:
                    continue
                
                # Draw mask (blue for smoke, red for fire)
                mask_points = np.array(mask, dtype=np.int32).reshape((-1, 1, 2))
                cv2.fillPoly(overlay, [mask_points], color)
                
                # Draw bounding box and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
            # Apply overlay with transparency
            frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
        
        return frame, fire_detected, smoke_detected

    def send_fire_alert(self, frame):
        """Send alert ONLY for fire detections"""
        current_time = time.time()
        if current_time - self.last_alert_time >= self.alert_cooldown:
            frame_path = os.path.join(self.frames_dir, f"fire_{int(current_time)}.jpg")
            cv2.imwrite(frame_path, frame)
            
            try:
                with open(frame_path, 'rb') as photo:
                    requests.post(
                        self.TELEGRAM_API_URL,
                        files={'photo': photo},
                        data={
                            'chat_id': self.TELEGRAM_CHAT_ID,
                            'caption': '🔥 FIRE DETECTED!',
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                print("✅ Fire alert sent to Telegram")
                self.last_alert_time = current_time
            except Exception as e:
                print(f"⚠️ Failed to send alert: {str(e)}")

    def process_frame(self, frame):
        """Process each frame for detections"""
        frame = cv2.resize(frame, self.frame_size)
        results = self.model.track(frame, persist=True)
        return self.draw_detections_with_masks(frame, results)

    def run(self):
        """Main detection loop"""
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                processed_frame, fire, smoke = self.process_frame(frame)
                
                # Send alert ONLY for fire (not smoke)
                if fire:
                    self.send_fire_alert(processed_frame)
                
                # Output video (contains both fire and smoke detections)
                self.writer.write(processed_frame)
                cv2.imshow("Fire & Smoke Detection", processed_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            self.cap.release()
            self.writer.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = FireSmokeDetector()
    detector.run()
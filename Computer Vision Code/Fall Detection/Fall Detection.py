import cv2
import cvzone
import math
import os
import time
import requests
from ultralytics import YOLO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Correct access method
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

# Validate token exists
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN not found in .env file")

# Initialize YOLO model
model = YOLO(r'Models\yolo12m.pt')

# Video setup
cap = cv2.VideoCapture(r'Test Videos\fall test 1.mp4')
fps = int(cap.get(cv2.CAP_PROP_FPS))
out = cv2.VideoWriter(r'Output Videos\Fall Output 1.mp4', 
                    cv2.VideoWriter_fourcc(*'mp4v'), fps, (980, 740))

# Load class names
with open('coco.txt', 'r') as f:
    classnames = f.read().splitlines()

# Fall frames directory
fall_frames_dir = 'fall_frames'
os.makedirs(fall_frames_dir, exist_ok=True)

def send_telegram_alert(image_path):
    """Send image with alert to your Telegram"""
    try:
        with open(image_path, 'rb') as photo:
            response = requests.post(
                TELEGRAM_API_URL,
                data={
                    'chat_id': TELEGRAM_CHAT_ID,
                    'caption': '🚨 FALL DETECTED! (Test Alert)'
                },
                files={'photo': photo}
            )
        if response.status_code == 200:
            print("✅ Telegram alert sent to your account!")
        else:
            print(f"❌ Telegram failed: {response.text}")
    except Exception as e:
        print(f"⚠️ Telegram error: {str(e)}")

# Alert control
last_alert_time = 0
alert_cooldown = 10  # seconds between alerts

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.resize(frame, (980, 740))
    current_time = time.time()
    fall_detected = False

    # Detect falls
    results = model(frame)
    for info in results:
        for box in info.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = math.ceil(box.conf[0] * 100)
            cls = classnames[int(box.cls[0])]

            if conf > 10 and cls == 'person':
                height, width = y2-y1, x2-x1
                if height - width < 0:  # Fall condition
                    fall_detected = True
                    cvzone.cornerRect(frame, [x1, y1, width, height], l=30, rt=6)
                    cvzone.putTextRect(frame, 'Person Fell', [x1+8, y1-12], 
                                     thickness=2, scale=2, colorR=(0,0,255))

    # Handle alerts
    if fall_detected and (current_time - last_alert_time >= alert_cooldown):
        frame_path = os.path.join(fall_frames_dir, f"fall_{int(time.time())}.jpg")
        if cv2.imwrite(frame_path, frame):
            print(f"📸 Saved: {frame_path}")
            send_telegram_alert(frame_path)
            last_alert_time = current_time

    # Display
    out.write(frame)
    cv2.imshow('Fall Detection', frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
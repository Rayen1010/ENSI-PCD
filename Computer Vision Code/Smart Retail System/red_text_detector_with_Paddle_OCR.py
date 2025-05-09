from paddleocr import PaddleOCR
import os
import cv2
import numpy as np

class RedTextDetector:
    def __init__(self, frames_folder="analyze_frames"):
        self.frames_folder = frames_folder
        # Initialize PaddleOCR
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')  # English language

    def _detect_red_regions(self, image):
        """
        Detect red-colored regions in the image.

        Args:
            image (numpy.ndarray): Input image.

        Returns:
            List of tuples: [(x, y, w, h), ...] representing bounding boxes of red regions.
        """
        try:
            # Convert the image to HSV color space
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Define range for red color in HSV
            lower_red1 = np.array([0, 70, 50])   # Lower bound for red (hue ~0-10)
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 70, 50]) # Upper bound for red (hue ~170-180)
            upper_red2 = np.array([180, 255, 255])

            # Create masks for red regions
            mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
            red_mask = mask1 | mask2

            # Find contours of red regions
            contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Extract bounding boxes of red regions
            red_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 10 and h > 10:  # Ignore very small regions
                    red_regions.append((x, y, w, h))

            return red_regions
        except Exception as e:
            print(f"⚠️ Error detecting red regions: {str(e)}")
            return []

    def find_first_frame_with_red_text(self):
        """
        Find the first frame (counting from the last) that contains red text.

        Returns:
            Tuple: (frame_file, red_texts) where:
                - frame_file: Name of the frame file.
                - red_texts: List of strings containing the detected red text.
        """
        try:
            # Load all frame files and sort them
            frame_files = sorted(os.listdir(self.frames_folder))
            total_frames = len(frame_files)

            # Select only the last 20 frames (or fewer if total_frames < 20)
            last_20_frames = frame_files[-20:] if total_frames >= 20 else frame_files

            # Process each frame in reverse order
            for frame_file in reversed(last_20_frames):
                frame_path = os.path.join(self.frames_folder, frame_file)
                frame = cv2.imread(frame_path)
                if frame is None:
                    print(f"⚠️ Failed to load frame: {frame_file}")
                    continue

                print(f"Processing frame: {frame_file}")
                red_regions = self._detect_red_regions(frame)

                # Check if red regions are found
                if red_regions:
                    print(f"\n✅ Found red text in frame: {frame_file}")
                    print(f"Red regions (bounding boxes): {red_regions}")

                    # Perform OCR on the red regions using PaddleOCR
                    red_texts = []
                    for i, (x, y, w, h) in enumerate(red_regions):
                        roi = frame[y:y+h, x:x+w]
                        result = self.ocr.ocr(roi, cls=True)  # Perform OCR on the ROI

                        # Check if OCR result is valid
                        if result and result[0]:
                            text = " ".join([line[1][0] for line in result[0]])  # Extract recognized text
                            print(f"Red text detected in region {i+1}: {text}")
                            red_texts.append(text)
                        else:
                            print(f"No text detected in region {i+1}.")

                    # If any red text was detected, return the frame and the texts
                    if red_texts:
                        print(f"Returning first frame with red text: {frame_file}")
                        return frame_file, red_texts

            # If no red text is found
            print("\n❌ No frames with red text found.")
            return None, []

        except Exception as e:
            print(f"❌ Fatal error during frame processing: {str(e)}")
            return None, []

if __name__ == "__main__":
    try:
        detector = RedTextDetector(frames_folder="analyze_frames")
        frame_file, red_texts = detector.find_first_frame_with_red_text()

        if frame_file:
            print(f"First frame with red text: {frame_file}")
            print(f"Detected red texts: {red_texts}")
        else:
            print("No red text detected in any frame.")

    except Exception as e:
        print(f"❌ System initialization failed: {str(e)}")
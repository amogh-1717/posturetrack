import cv2
import mediapipe as mp
import numpy as np
import websockets
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostureAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            smooth_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points (point2 is the vertex)"""
        p1 = np.array([point1.x, point1.y, point1.z])
        p2 = np.array([point2.x, point2.y, point2.z])
        p3 = np.array([point3.x, point3.y, point3.z])
        
        v1 = p1 - p2
        v2 = p3 - p2
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        angle = np.degrees(np.arccos(cos_angle))
        return angle
    
    def calculate_line_angle(self, point1, point2):
        """Calculate angle of a line relative to vertical"""
        dx = point2.x - point1.x
        dy = point2.y - point1.y
        angle = abs(np.degrees(np.arctan2(dx, dy)))
        return angle
    
    def analyze_posture(self, landmarks) -> tuple:
        """
        Medical-grade posture analysis
        Returns: (status, wrist_angle, neck_angle, spine_angle)
        """
        if not landmarks:
            return ('bad', 0, 0, 0)
        
        try:
            # Get landmarks
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value]
            right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value]
            left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
            right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
            
            # Try multiple finger points for better detection
            left_index = landmarks[self.mp_pose.PoseLandmark.LEFT_INDEX.value]
            right_index = landmarks[self.mp_pose.PoseLandmark.RIGHT_INDEX.value]
            left_pinky = landmarks[self.mp_pose.PoseLandmark.LEFT_PINKY.value]
            right_pinky = landmarks[self.mp_pose.PoseLandmark.RIGHT_PINKY.value]
            
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
            
            # Calculate midpoints
            class Point:
                def __init__(self, x, y, z):
                    self.x, self.y, self.z = x, y, z
            
            shoulder_midpoint = Point(
                (left_shoulder.x + right_shoulder.x) / 2,
                (left_shoulder.y + right_shoulder.y) / 2,
                (left_shoulder.z + right_shoulder.z) / 2
            )
            
            hip_midpoint = Point(
                (left_hip.x + right_hip.x) / 2,
                (left_hip.y + right_hip.y) / 2,
                (left_hip.z + right_hip.z) / 2
            )
            
            # Calculate BETTER wrist angles using average of index and pinky
            # This gives more accurate wrist flexion measurement
            left_finger_mid = Point(
                (left_index.x + left_pinky.x) / 2,
                (left_index.y + left_pinky.y) / 2,
                (left_index.z + left_pinky.z) / 2
            )
            
            right_finger_mid = Point(
                (right_index.x + right_pinky.x) / 2,
                (right_index.y + right_pinky.y) / 2,
                (right_index.z + right_pinky.z) / 2
            )
            
            # Calculate wrist angles with better finger point
            left_wrist_angle = self.calculate_angle(left_elbow, left_wrist, left_finger_mid)
            right_wrist_angle = self.calculate_angle(right_elbow, right_wrist, right_finger_mid)
            wrist_angle = min(left_wrist_angle, right_wrist_angle)
            
            neck_angle = self.calculate_line_angle(nose, shoulder_midpoint)
            spine_angle = self.calculate_line_angle(shoulder_midpoint, hip_midpoint)
            
            # Classify posture
            wrist_status = self.classify_wrist_posture(wrist_angle)
            neck_status = self.classify_neck_posture(neck_angle)
            spine_status = self.classify_spine_posture(spine_angle)
            
            # Overall status
            if wrist_status == 'bad' or neck_status == 'bad' or spine_status == 'bad':
                overall_status = 'bad'
            elif wrist_status == 'ok' or neck_status == 'ok' or spine_status == 'ok':
                overall_status = 'ok'
            else:
                overall_status = 'good'
            
            return (overall_status, wrist_angle, neck_angle, spine_angle)
                
        except Exception as e:
            logger.error(f"Posture analysis error: {e}")
            return ('bad', 0, 0, 0)
    
    def classify_wrist_posture(self, angle):
        """
        Wrist angle classification - STRICTER MEDICAL STANDARDS
        Good: 140°-180° (straight wrist, ideal)
        OK: 110°-140° (mild flexion, acceptable short-term)
        Bad: <110° (excessive flexion, injury risk)
        """
        if angle >= 140:  # Stricter threshold
            return 'good'
        elif angle >= 110:  # More realistic OK range
            return 'ok'
        else:
            return 'bad'
    
    def classify_neck_posture(self, angle):
        """Neck alignment - VERY LENIENT"""
        if angle <= 35:
            return 'good'
        elif angle <= 50:
            return 'ok'
        else:
            return 'bad'
    
    def classify_spine_posture(self, angle):
        """Spine alignment - EXTREMELY LENIENT"""
        if 5 <= angle <= 80:
            return 'good'
        elif angle < 90:
            return 'ok'
        else:
            return 'bad'
    
    def draw_posture_landmarks(self, image, landmarks):
        """
        Draw ONLY essential landmarks for surgical training ergonomics
        Clean, professional visualization - no clutter
        """
        if not landmarks:
            return
        
        height, width, _ = image.shape
        
        def get_point(landmark):
            return (int(landmark.x * width), int(landmark.y * height))
        
        # Get ONLY essential landmarks for our 3 metrics
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value]
        right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
        right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
        left_index = landmarks[self.mp_pose.PoseLandmark.LEFT_INDEX.value]
        right_index = landmarks[self.mp_pose.PoseLandmark.RIGHT_INDEX.value]
        left_pinky = landmarks[self.mp_pose.PoseLandmark.LEFT_PINKY.value]
        right_pinky = landmarks[self.mp_pose.PoseLandmark.RIGHT_PINKY.value]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
        
        # Calculate essential midpoints
        nose_point = get_point(nose)
        shoulder_mid = (int((left_shoulder.x + right_shoulder.x) / 2 * width),
                       int((left_shoulder.y + right_shoulder.y) / 2 * height))
        hip_mid = (int((left_hip.x + right_hip.x) / 2 * width),
                   int((left_hip.y + right_hip.y) / 2 * height))
        
        # Finger midpoints for wrist angle
        left_finger_mid = (int((left_index.x + left_pinky.x) / 2 * width),
                          int((left_index.y + left_pinky.y) / 2 * height))
        right_finger_mid = (int((right_index.x + right_pinky.x) / 2 * width),
                           int((right_index.y + right_pinky.y) / 2 * height))
        
        # === DRAW ALIGNMENT LINES (Posture metrics) ===
        
        # 1. NECK ALIGNMENT (Head to Shoulder) - Bright Cyan
        cv2.line(image, nose_point, shoulder_mid, (255, 255, 0), 3)
        
        # 2. SPINE ALIGNMENT (Shoulder to Hip) - Bright Magenta  
        cv2.line(image, shoulder_mid, hip_mid, (255, 0, 255), 3)
        
        # 3. WRIST ANGLES - Thinner, cleaner lines
        # Left arm - Yellow
        cv2.line(image, get_point(left_elbow), get_point(left_wrist), (0, 255, 255), 2)
        cv2.line(image, get_point(left_wrist), left_finger_mid, (0, 255, 255), 2)
        
        # Right arm - Cyan
        cv2.line(image, get_point(right_elbow), get_point(right_wrist), (255, 200, 0), 2)
        cv2.line(image, get_point(right_wrist), right_finger_mid, (255, 200, 0), 2)
        
        # === DRAW ESSENTIAL LANDMARKS ONLY ===
        # Small, professional dots - not overwhelming
        
        # Head (neck alignment reference) - Cyan
        cv2.circle(image, nose_point, 5, (255, 255, 0), -1)
        
        # Shoulders (critical reference points) - Green
        cv2.circle(image, get_point(left_shoulder), 6, (0, 255, 0), -1)
        cv2.circle(image, get_point(right_shoulder), 6, (0, 255, 0), -1)
        cv2.circle(image, shoulder_mid, 6, (0, 255, 0), -1)
        
        # Elbows (wrist angle reference) - Blue
        cv2.circle(image, get_point(left_elbow), 5, (255, 100, 0), -1)
        cv2.circle(image, get_point(right_elbow), 5, (255, 100, 0), -1)
        
        # Wrists (wrist angle vertex) - Orange
        cv2.circle(image, get_point(left_wrist), 6, (0, 165, 255), -1)
        cv2.circle(image, get_point(right_wrist), 6, (0, 165, 255), -1)
        
        # Fingers (wrist angle endpoint) - Red with thin white border for visibility
        cv2.circle(image, left_finger_mid, 8, (255, 255, 255), 1)   # White outline
        cv2.circle(image, left_finger_mid, 6, (0, 0, 255), -1)      # Red center
        cv2.circle(image, right_finger_mid, 8, (255, 255, 255), 1)
        cv2.circle(image, right_finger_mid, 6, (0, 0, 255), -1)
        
        # Hips (spine alignment reference) - Magenta
        cv2.circle(image, get_point(left_hip), 6, (255, 0, 255), -1)
        cv2.circle(image, get_point(right_hip), 6, (255, 0, 255), -1)
        cv2.circle(image, hip_mid, 6, (255, 0, 255), -1)

class PostureClient:
    def __init__(self, backend_url="ws://localhost:8000/ws/posture"):
        self.backend_url = backend_url
        self.analyzer = PostureAnalyzer()
        self.websocket = None
        self.cap = None
        
    async def connect_to_backend(self):
        """Connect to backend WebSocket"""
        try:
            self.websocket = await websockets.connect(self.backend_url)
            logger.info(f"Connected to backend at {self.backend_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to backend: {e}")
            return False
    
    async def send_posture_data(self, status: str):
        """Send posture data to backend"""
        if not self.websocket:
            return False
        
        try:
            data = {
                "status": status,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            await self.websocket.send(json.dumps(data))
            
            response = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
            logger.info(f"Backend response: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to send data to backend: {e}")
            return False
    
    async def start_camera_capture(self):
        """Start camera capture and posture analysis"""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            logger.error("Failed to open camera")
            return
        
        logger.info("Camera started. Press 'q' to quit.")
        last_status = None
        frame_count = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.error("Failed to capture frame")
                    break
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.analyzer.pose.process(rgb_frame)
                
                # Analyze posture - FIX: Extract values from tuple
                posture_result = ('bad', 0, 0, 0)
                wrist_angle = 0
                neck_angle = 0
                spine_angle = 0
                
                if results.pose_landmarks:
                    posture_result = self.analyzer.analyze_posture(results.pose_landmarks.landmark)
                    current_status = posture_result[0]  # Extract just the status string
                    wrist_angle = posture_result[1]
                    neck_angle = posture_result[2]
                    spine_angle = posture_result[3]
                    
                    # Draw custom landmarks
                    self.analyzer.draw_posture_landmarks(frame, results.pose_landmarks.landmark)
                else:
                    current_status = 'bad'
                
                # Display status with colors
                if current_status == 'good':
                    status_color = (0, 255, 0)
                    status_bg = (0, 100, 0)
                elif current_status == 'ok':
                    status_color = (0, 255, 255)
                    status_bg = (0, 100, 100)
                else:
                    status_color = (0, 0, 255)
                    status_bg = (0, 0, 100)
                
                # Main status display
                cv2.rectangle(frame, (5, 5), (400, 50), status_bg, -1)
                cv2.putText(frame, f"POSTURE: {current_status.upper()}", 
                           (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.2, status_color, 3)
                
                # Angle measurements
                y_offset = 70
                
                # Wrist
                wrist_color = (0, 255, 0) if wrist_angle >= 140 else (0, 255, 255) if wrist_angle >= 110 else (0, 0, 255)
                cv2.putText(frame, f"Wrist: {wrist_angle:.1f}°", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, wrist_color, 2)
                cv2.putText(frame, f"(Good: 140-180)", 
                           (250, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                
                # Head
                neck_color = (0, 255, 0) if neck_angle <= 35 else (0, 255, 255) if neck_angle <= 50 else (0, 0, 255)
                cv2.putText(frame, f"Head: {neck_angle:.1f}°", 
                           (10, y_offset + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, neck_color, 2)
                cv2.putText(frame, f"(Good: 0-35)", 
                           (250, y_offset + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                
                # Spine
                spine_color = (0, 255, 0) if 5 <= spine_angle <= 80 else (0, 255, 255) if spine_angle < 90 else (0, 0, 255)
                cv2.putText(frame, f"Spine: {spine_angle:.1f}°", 
                           (10, y_offset + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, spine_color, 2)
                cv2.putText(frame, f"(Good: 5-80)", 
                           (250, y_offset + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                
                # Landmarks detected indicator
                cv2.putText(frame, f"Landmarks: {'DETECTED' if results.pose_landmarks else 'NOT FOUND'}", 
                           (10, y_offset + 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                           (0, 255, 0) if results.pose_landmarks else (0, 0, 255), 2)
                
                # Instructions
                instruction_y = frame.shape[0] - 120
                cv2.rectangle(frame, (5, instruction_y), (650, frame.shape[0] - 5), (40, 40, 40), -1)
                
                cv2.putText(frame, "CAMERA SETUP TIPS:", 
                           (15, instruction_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(frame, "1. Sit 3-4 feet from camera", 
                           (15, instruction_y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(frame, "2. Turn chair 45° LEFT (camera sees your right side)", 
                           (15, instruction_y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(frame, "3. Show HIP to HEAD in frame", 
                           (15, instruction_y + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(frame, "4. RED dots (with white border) = Finger tips!", 
                           (15, instruction_y + 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                cv2.putText(frame, "Posture lines: YELLOW=Head->Shoulder | MAGENTA=Shoulder->Hip", 
                           (10, instruction_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(frame, "Wrist angles: CYAN=Left arm | YELLOW=Right arm -> Finger midpoint", 
                           (10, instruction_y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                # Send data every 30 frames or when status changes
                frame_count += 1
                if (frame_count % 30 == 0 or current_status != last_status) and self.websocket:
                    await self.send_posture_data(current_status)  # Send only the status string
                    last_status = current_status
                
                cv2.imshow('PostureTrack', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                await asyncio.sleep(0.033)
                
        except KeyboardInterrupt:
            logger.info("Stopping camera capture...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        logger.info("Camera resources cleaned up")

async def main():
    client = PostureClient()
    
    if not await client.connect_to_backend():
        logger.error("Could not connect to backend. Make sure FastAPI server is running.")
        return
    
    await client.start_camera_capture()
    
    if client.websocket:
        await client.websocket.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
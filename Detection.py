import cv2
import mediapipe as mp
import serial
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.7)

mp_drawing = mp.solutions.drawing_utils

# Initialize Serial Communication
try:
    ser = serial.Serial('COM3', 9600) #change this to your arduino port
    time.sleep(2)  # Allow time for the connection to establish
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

# Start Video Capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get image dimensions
    h, w, _ = frame.shape

    # Process the frame and detect hands
    results = hands.process(rgb_frame)

    # Check if any hands are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            handedness = results.multi_handedness[results.multi_hand_landmarks.index(hand_landmarks)].classification[0].label
            
            if handedness == 'Right':
                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Extract landmark positions and convert them to pixel coordinates
                wrist_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * w)
                wrist_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * h)
                thumb_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * w)
                index_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * w)

                # Calculate angles based on wrist position and thumb/index tip positions
                Xangle = int((wrist_x / w) * 180)
                Yangle = int((wrist_y / h) * 90)
                Tangle = int((thumb_x / w) * 90)
                Iangle = int((index_x / w) * 90)

                # Clamp angles to their respective ranges
                Xangle = max(0, min(180, Xangle))
                Yangle = max(0, min(90, Yangle))
                Tangle = max(0, min(90, Tangle))
                Iangle = max(0, min(90, Iangle))

                # Create command string for serial communication
                command_string = f"X{Xangle}Y{Yangle}T{Tangle}I{Iangle}\n"
                print(f"Sending command: {command_string}")
                
                # Attempt to write command string to serial port with error handling
                try:
                    ser.write(command_string.encode())
                except serial.SerialException as e:
                    print(f"Failed to write to serial port: {e}")

    # Display the processed frame with hand tracking
    cv2.imshow('Right Hand Tracking', frame)

    # Exit loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
ser.close()
cv2.destroyAllWindows()
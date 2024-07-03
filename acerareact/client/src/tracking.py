import cv2
import mediapipe as mp
import numpy as np
import pyautogui

# MediaPipe initialization
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

# Initialize PyAutoGUI for mouse control
screen_width, screen_height = pyautogui.size()
mouse_control_enabled = False

# Function to map hand landmarks to screen coordinates
def map_hand_to_mouse(x, y):
    mapped_x = np.interp(x, [0, 1], [0, screen_width])
    mapped_y = np.interp(y, [0, 1], [0, screen_height])
    return int(mapped_x), int(mapped_y)

# For static images:
IMAGE_FILES = []
BG_COLOR = (192, 192, 192)  # gray

# Initialize Holistic model for static image processing
with mp_holistic.Holistic(
    static_image_mode=True,
    model_complexity=2,
    enable_segmentation=True,
    refine_face_landmarks=True) as holistic:

    for idx, file in enumerate(IMAGE_FILES):
        image = cv2.imread(file)
        image_height, image_width, _ = image.shape

        # Convert the BGR image to RGB before processing.
        results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Access pose landmarks
        if results.pose_landmarks:
            nose_x = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].x * image_width
            nose_y = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE].y * image_height
            print(f'Nose coordinates: ({nose_x}, {nose_y})')

        # Check segmentation mask before drawing
        if results.segmentation_mask is not None:
            # Draw segmentation on the image
            condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
            bg_image = np.zeros(image.shape, dtype=np.uint8)
            bg_image[:] = (192, 192, 192)  # gray background color
            annotated_image = np.where(condition, image, bg_image)
        else:
            annotated_image = image.copy()

        # Draw face landmarks if they exist
        if results.face_landmarks:
            mp_drawing.draw_landmarks(
                annotated_image,
                results.face_landmarks,
                mp_holistic.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

        # Draw pose landmarks
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        cv2.imwrite(f'/tmp/annotated_image{idx}.png', annotated_image)

# For webcam input:
cap = cv2.VideoCapture(0)

# Initialize Holistic model for live webcam processing
with mp_holistic.Holistic(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as holistic:

    while cap.isOpened():
        success, image = cap.read()

        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Flip the image horizontally for a mirror-like view
        image = cv2.flip(image, 1)
        
        # Convert image to RGB and process with Holistic
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = holistic.process(image_rgb)

        # Draw face contours and pose landmarks on the image
        if results.face_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.face_landmarks,
                mp_holistic.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())

        # Draw hand landmarks and control mouse
        def control_mouse(hand_landmarks):
            global mouse_control_enabled
            if hand_landmarks:
                # Use index finger tip as mouse cursor
                index_x = hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP].x
                index_y = hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP].y
                
                # Convert hand coordinates to screen coordinates
                mouse_x, mouse_y = map_hand_to_mouse(index_x, index_y)

                # Move mouse cursor
                pyautogui.moveTo(mouse_x, mouse_y, duration=0.1)
                
                # Perform click action (toggle mouse control with thumb and index finger pinch)
                thumb_tip = hand_landmarks.landmark[mp_holistic.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_holistic.HandLandmark.INDEX_FINGER_TIP]
                thumb_to_index_distance = np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)

                if thumb_to_index_distance < 0.05:  # Adjust threshold as needed
                    if not mouse_control_enabled:
                        pyautogui.click()
                        mouse_control_enabled = True
                else:
                    mouse_control_enabled = False

        if results.right_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.right_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style())
            control_mouse(results.right_hand_landmarks)

        if results.left_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.left_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style())
            control_mouse(results.left_hand_landmarks)

        # Draw pose landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        # Display the image with annotations
        cv2.imshow('MediaPipe Holistic', image)

        # Exit loop if ESC is pressed
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


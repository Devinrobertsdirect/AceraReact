import cv2
import threading
import pyautogui
import re
import time
import traceback
from RealtimeSTT import AudioToTextRecorder
import tools

# Function to execute the appropriate action based on the detected gesture
def execute_gesture_action(gesture, hand_landmarks, screen_width, screen_height, gesture_control):
    if gesture == "click":
        pyautogui.click()
    elif gesture == "double_click":
        pyautogui.doubleClick()
    elif gesture == "right_click":
        pyautogui.rightClick()
    elif gesture == "swipe_left":
        pyautogui.hscroll(-50)
    elif gesture == "swipe_right":
        pyautogui.hscroll(50)
    elif gesture == "scroll_up":
        pyautogui.scroll(50)
    elif gesture == "scroll_down":
        pyautogui.scroll(-50)
    elif gesture == "zoom_in":
        pyautogui.keyDown('ctrl')
        pyautogui.scroll(50)
        pyautogui.keyUp('ctrl')
    elif gesture == "zoom_out":
        pyautogui.keyDown('ctrl')
        pyautogui.scroll(-50)
        pyautogui.keyUp('ctrl')
    elif gesture == "move":
        x, y = gesture_control.smooth_cursor_movement(hand_landmarks, screen_width, screen_height)
        pyautogui.moveTo(x, y)

# Function to capture hand gestures using the GestureControl module
def capture_hand_gestures(gesture_control, screen_width, screen_height, mouse_mode_ref):
    while mouse_mode_ref[0]:
        ret, frame = gesture_control.cap.read()  # Initialize frame variable
        if not ret:
            break
        
        frame, gesture, hand_landmarks = gesture_control.detect_gestures(frame)
        if frame is None:
            break
        
        cv2.imshow("Gesture Recognition", frame)
        
        if gesture:
            execute_gesture_action(gesture, hand_landmarks, screen_width, screen_height, gesture_control)
        
        if cv2.waitKey(1) == ord('q'):
            break
    
    cv2.destroyAllWindows()
    gesture_control.release()
    
# Function to improve speech recognition accuracy
def improve_recognition(text):
    corrections = {
        "aacera": "Acera",
        "ascerra": "Acera",
        "acerra": "Acera",
        "asara": "Acera",
        "sarah": "Acera",
        "sara": "Acera",
        "sera": "Acera",
        "serah": "Acera",
        "asera": "Acera",
        "aserah": "Acera",
        "asura": "Acera",
        "ahsara": "Acera",
    }
    pattern = re.compile('|'.join(corrections.keys()), re.IGNORECASE)
    return pattern.sub(lambda x: corrections[x.group().lower()], text)

# Function to append the current timestamp to the recognized text
def append_timestamp_to_text(text):
    return f"{text} {time.strftime('%Y-%m-%d %H-%M-%S')}"

# Function to handle commands related to hashtags
def handle_hashtag_command(command):
    command = command.lower().strip()
    if command == "play":
        tools.parse_command("play")
    elif command == "pause":
        tools.parse_command("pause")
    elif command == "skip":
        tools.parse_command("skip")
    elif command == "previous":
        tools.parse_command("previous")
    elif command == "spotify":
        tools.parse_command("spotify")
    else:
        return False
    return True

# Main function to start listening for speech commands and process them
def start_listening():
    global mouse_mode, recorder, hot_words, gesture_control, screen_width, screen_height
    while True:
        try:
            current_text = recorder.text()
            if not current_text:
                continue
            
            current_text = improve_recognition(current_text)
            
            # Check if the user explicitly asks for the time
            if "what time is it" in current_text.lower() or "current time" in current_text.lower():
                current_text = append_timestamp_to_text(current_text)
            
            print("Recognized text:", current_text)
            
            if "acera" in current_text.lower():
                recorder.stop()
                try:
                    user_input = re.sub(r'\bacera\b', '', current_text, flags=re.IGNORECASE).strip().lower()
                except Exception as e:
                    print(f"An error occurred while processing user input: {e}")
                    traceback.print_exc()
                    recorder.start()
                    continue
                
                if user_input:
                    print("User:", user_input)
                    if "mouse" in user_input:
                        mouse_mode = not mouse_mode
                        mode_status = "Mouse movement mode activated." if mouse_mode else "ChatGPT assistance mode activated."
                        assist.TTS(mode_status)
                        if mouse_mode:
                            mouse_mode_ref = [mouse_mode]
                            gesture_thread = threading.Thread(target=capture_hand_gestures, args=(gesture_control, screen_width, screen_height, mouse_mode_ref))
                            gesture_thread.start()
                        else:
                            mouse_mode_ref[0] = False
                        recorder.start()
                        continue

                    if mouse_mode:
                        if "up" in user_input:
                            tools.parse_command("move_mouse_up")
                        elif "down" in user_input:
                            tools.parse_command("move_mouse_down")
                        elif "left" in user_input:
                            tools.parse_command("move_mouse_left")
                        elif "right" in user_input:
                            tools.parse_command("move_mouse_right")
                        elif "click" in user_input:
                            pyautogui.click()
                        recorder.start()
                        continue
                    
                    command_response = tools.parse_command(user_input)
                    if command_response:
                        print("Acera:", command_response)
                        assist.TTS(command_response)
                    else:
                        response = assist.ask_question_memory(user_input)
                        print("Acera:", response)
                        assist.TTS(response)
                else:
                    response = "How can I assist you today?"
                    print("Acera:", response)
                    assist.TTS(response)
                recorder.start()
            print("Listening...")
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            recorder.start()  # Ensure recorder is restarted after an exception

if __name__ == '__main__':
    mouse_mode = False
    recorder = AudioToTextRecorder(
        spinner=False,
        model="tiny.en",
        language="en",
        post_speech_silence_duration=0.5,
        silero_sensitivity=0.5
    )
    hot_words = ["acera", "asara", "aserra", "asera", "aserah", "acerra", "sera", "ahsara", "sarah", "serah", "sara", "asura"]

    gesture_control = GestureControl()
    screen_width, screen_height = pyautogui.size()

    print("Say something...")
    start_listening()
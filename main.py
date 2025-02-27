import cv2
import mediapipe as mp
import pyautogui
import tkinter as tk
from tkinter import messagebox
import math

# Initialize mediapipe hands and webcam
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Function to calculate distance between two points
def calculate_distance(p1, p2):
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)

# Function to control the mouse
def move_mouse(x, y):
    screen_width, screen_height = pyautogui.size()
    x = int(screen_width * x)
    y = int(screen_height * y)
    pyautogui.moveTo(x, y)
    print(f"Mouse moved to: ({x}, {y})")

# Function for mouse click
def click_mouse():
    pyautogui.click()
    print("Mouse Clicked")

# Function for right-click
def right_click_mouse():
    pyautogui.rightClick()
    print("Right Clicked")

# Function to scroll
def scroll_mouse(direction):
    pyautogui.scroll(direction)
    print(f"Scrolled {'Up' if direction > 0 else 'Down'}")

# Virtual Mouse Functionality
def virtual_mouse():
    print("Virtual Mouse is starting...")  # Debugging statement

    # Start the webcam feed
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Flip the frame horizontally for a more intuitive interaction
        frame = cv2.flip(frame, 1)
        # Convert to RGB for mediapipe processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # If hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get the position of index, thumb, and middle finger
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

                # Mouse movement (index finger movement)
                move_mouse(index_finger_tip.x, index_finger_tip.y)

                # Check for pinch (index finger and thumb close together)
                distance_thumb_index = calculate_distance(thumb_tip, index_finger_tip)
                if distance_thumb_index < 0.05:  # Threshold distance for a pinch
                    click_mouse()

                # Check for right-click (index and middle finger extended)
                if index_finger_tip.y < middle_finger_tip.y:  # Rough check for the right-click gesture
                    right_click_mouse()

                # Check for scroll (fingers moving up/down)
                if index_finger_tip.y < middle_finger_tip.y and distance_thumb_index > 0.15:  # Scroll if further apart
                    scroll_mouse(10)  # Scroll up

        # Display the frame with hand landmarks
        cv2.imshow("Virtual Mouse", frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting virtual mouse...")
            break

    cap.release()
    cv2.destroyAllWindows()

# GUI Setup
def start_virtual_mouse():
    try:
        # Start the virtual mouse in a separate thread
        print("Starting the virtual mouse...")
        virtual_mouse()
    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def main():
    print("Initializing the Virtual Mouse GUI...")

    # Set up the main window
    root = tk.Tk()
    root.title("Virtual Mouse Control")
    root.geometry("300x150")

    # Button to start the virtual mouse
    start_button = tk.Button(root, text="Start Virtual Mouse", command=start_virtual_mouse)
    start_button.pack(pady=50)

    root.mainloop()

if __name__ == "__main__":
    main()

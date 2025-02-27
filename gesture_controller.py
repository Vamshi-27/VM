import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from hand_tracking import HandRecog, HLabel
from controller import Controller

class GestureController:
    gc_mode = 1
    cap = cv2.VideoCapture(0)
    CAM_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    CAM_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    hr_major = None  # Right Hand by default
    hr_minor = None  # Left Hand by default
    dom_hand = True

    def classify_hands(results):
        left, right = None, None
        try:
            handedness_dict = MessageToDict(results.multi_handedness[0])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[0]
            else:
                left = results.multi_hand_landmarks[0]
        except:
            pass

        try:
            handedness_dict = MessageToDict(results.multi_handedness[1])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[1]
            else:
                left = results.multi_hand_landmarks[1]
        except:
            pass      

        if GestureController.dom_hand:
            GestureController.hr_major = right
            GestureController.hr_minor = left
        else:
            GestureController.hr_major = left
            GestureController.hr_minor = right

    def start(self):
        handmajor = HandRecog(HLabel.MAJOR)
        handminor = HandRecog(HLabel.MINOR)

        with mp.solutions.hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            while GestureController.cap.isOpened() and GestureController.gc_mode:
                success, image = GestureController.cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue              

                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                results = hands.process(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:                   
                    GestureController.classify_hands(results)
                    handmajor.update_hand_result(GestureController.hr_major)
                    handminor.update_hand_result(GestureController.hr_minor)
                    handmajor.set_finger_state()
                    handminor.set_finger_state()

                    gest_name = handminor.get_gesture()
                    if gest_name == "PINCH_MINOR":
                        Controller.handle_controls(gest_name, handminor.hand_result)
                    else:
                        gest_name = handmajor.get_gesture()
                        Controller.handle_controls(gest_name, handmajor.hand_result)
                    
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp.solutions.drawing_utils.draw_landmarks(image, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                else:
                    Controller.prev_hand = None

                cv2.imshow('Virtual Mouse Gesture Controller', image)
                if cv2.waitKey(5) & 0xFF == 13:
                    break

        GestureController.cap.release()
        cv2.destroyAllWindows()

def runvirtualmouse():
    gc1 = GestureController()
    gc1.start()

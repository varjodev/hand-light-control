import mediapipe as mp
import numpy as np

class FingerCounter:
    def __init__(self, method="mediapipe"):
        self.method = method
        if method == "mediapipe":
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5)
            
        self.results = None
            
    def process(self, image):
        results = self.hands.process(image)
        self.results = results
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())
                
        return image
    
    def count(self):
        """ counts fingers by using distances between detected hand points
        """
        finger_counter = None
        palm_enum = 0
        landmark_enums = [4,8,12,16,20] 
        landmark_refs = [1,5,9,13,17] 
        landmark_names = ["thumb", "index", "middle", "ring", "pinky"]
        dist_thresholds = [0.40, 0.55, 0.5, 0.5, 0.4]
        # if self.results.left_hand_landmarks.landmark:
        if self.results.multi_hand_landmarks:
            finger_counter = 0
            hand_landmarks = self.results.multi_hand_landmarks[0]
            landmark_ix = 0
            for landmark in hand_landmarks.landmark:
                if landmark_ix == 0:
                    base = landmark

                if landmark_ix == 4:
                    # Thumb is a special case, because extending it doesn't change the distance
                    # to base much
                    thumb_landmark = landmark

                if landmark_ix == 5:
                    thumb_dist = np.sqrt((landmark.x-thumb_landmark.x)**2+(landmark.y-thumb_landmark.y)**2+(landmark.z-thumb_landmark.z)**2)
                    ratio = thumb_dist/ref_dist
                    if ratio> 1.5:
                        finger_counter += 1

                if landmark_ix in landmark_refs:
                    # Hand and scale depends on the distance to the camera, 
                    # so we use distance ratios
                    ref_dist = np.sqrt((base.x-landmark.x)**2+(base.y-landmark.y)**2+(base.z-landmark.z)**2)
                
                if landmark_ix in landmark_enums[1:]: # excluding thumb
                    dist = np.sqrt((base.x-landmark.x)**2+(base.y-landmark.y)**2+(base.z-landmark.z)**2)
                    ratio = dist/ref_dist
                    # print(ratio)

                    if ratio > 1.5: #dist_thresholds[landmark_enums.index(landmark_ix)]:
                        finger_counter += 1

                    # print(dist)
                # print(landmark)
                # print(landmark_ix)
                landmark_ix+=1
        # print(finger_counter)

        return finger_counter
                

        # if self.results.multi_hand_landmarks:
        #     # lhl = self.results.left_hand_landmarks.landmark
        #     # for hand_landmarks in lhl:
        #     #     print(hand_landmarks)
        
        #     mhl = self.results.multi_hand_landmarks
        #     # print("start")
        #     # print(type(mhl[0]))
        #     for land_ix, landmark in enumerate(mhl.landmark):
        #         print(land_ix)
            # print("end")
            # print(len(mhl))
            # print(mhl[8])
            # print()
            # print(self.results.multi_hand_landmarks)
            # for ix, enum_ix in enumerate(landmark_enums):
            #     print(ix, enum_ix)
            #     print(landmark_names[ix])
            #     print(self.results.multi_hand_landmarks[enum_ix])
            #     print()
        
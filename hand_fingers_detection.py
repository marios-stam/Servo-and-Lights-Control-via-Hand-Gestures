import cv2
import mediapipe as mp
from utils import *

FIST_DETECTED_COLOR=(255,0,0)
LEFT_ORIGIN_X=20
RIGHT_ORIGIN_X=450

POINT_START_INDEX=0
POINT_REF_INDEX=12

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0)

def drawLandmarks(results):
  for hand_landmarks in results.multi_hand_landmarks:
    mp_drawing.draw_landmarks(
        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  counter=0
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      drawLandmarks(results)
      # for hand_landmarks in results.multi_hand_landmarks:
      #   mp_drawing.draw_landmarks(
      #       image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
      points,angles,distances,fistsDetected=[],[],[],[]

      for hand_landmarks in results.multi_hand_landmarks:
        points.append(hand_landmarks.landmark)
        
        for i,p in enumerate(points[-1]):
          points[-1][i].x,points[-1][i].y=convertPointCoordsToImagePlane(image,p)

        angle=getAngle(points[-1][POINT_START_INDEX],points[-1][POINT_REF_INDEX])
        distance=getDistance(points[-1][POINT_START_INDEX],points[-1][POINT_REF_INDEX])
        fistDetect=fistDetected(points[-1])
        
        angles.append(angle)
        distances.append(distance)
        fistsDetected.append(fistDetect)
        # image=drawPointToImage(image,points[0])
        # image=drawPointToImage(image,points[12])

        # txt="%.0f , %.0f" % (points[0].x,points[0].y )
        # image=drawTextToImage(image,txt )
        # txt="%.0f , %.0f" % (points[12].x,points[12].y )
        # image=drawTextToImage(image,txt,origin=(20,60) )

     
    
      if len(results.multi_hand_landmarks)>1:
        txt="angle: %d" % (90-angles[1] )
        image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,25))
        txt="distance: %d" % (distances[1])
        image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,45))
      
        txt="angle: %d" % (90-angles[0] )
        image=drawTextToImage(image,txt,origin=(RIGHT_ORIGIN_X,25))
        txt="distance: %d" % (distances[0])
        image=drawTextToImage(image,txt,origin=(RIGHT_ORIGIN_X,45))
        
        if (fistsDetected[0]):
          txt="FIST DETECTED"
          image=drawTextToImage(image,txt,origin=(RIGHT_ORIGIN_X,70),color=FIST_DETECTED_COLOR )

        if (fistsDetected[1]):
          txt="FIST DETECTED"
          image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,70),color=FIST_DETECTED_COLOR )
      else:
        txt="angle: %d" % (90-angles[0] )
        image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,30))
        txt="distance: %d" % (distances[0])
        image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,50))
        print()
        if (fistsDetected[0]):
          txt="FIST DETECTED"
          image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,70),color=FIST_DETECTED_COLOR )
        
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
    counter=counter+1
    if counter>100:
      pass
      #break
cap.release()

import cv2
import mediapipe as mp
from utils import *
import socket
from time import time

FIST_DETECTED_COLOR=(0,255,0)
LEFT_ORIGIN_X=20
RIGHT_ORIGIN_X=450

POINT_START_INDEX=0
POINT_REF_INDEX=12

#connection with Labview VI set up
TIME_INTERVAL=0.2
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8089))
server.listen(1)
conn, addr = server.accept()
x=conn.recv(9)
print(x)

#Media Pipe set up
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# For webcam input:
cap = cv2.VideoCapture(0)

def drawLandmarks(results):
  for hand_landmarks in results.multi_hand_landmarks:
    mp_drawing.draw_landmarks(
        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

t=time()
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

    points,angles,distances,fistsDetected=[],[],[],[]
    if results.multi_hand_landmarks:
      drawLandmarks(results)
      # for hand_landmarks in results.multi_hand_landmarks:
      #   mp_drawing.draw_landmarks(
      #       image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
      
      points.clear()
      angles.clear()
      distances.clear()
      fistsDetected.clear()
      
      for hand_landmarks in results.multi_hand_landmarks:
        points.append(hand_landmarks.landmark)
        
        for i,p in enumerate(points[-1]):
          points[-1][i].x,points[-1][i].y=convertPointCoordsToImagePlane(image,p)

        angle=getAngle(points[-1][POINT_START_INDEX],points[-1][POINT_REF_INDEX])
        distance=getDistance(points[-1][POINT_START_INDEX],points[-1][POINT_REF_INDEX])
        fistDetect=fistDetected(points[-1])
        
        angles.append(90-angle)
        distances.append(distance)
        fistsDetected.append(1 if fistDetect else 0 )
        # image=drawPointToImage(image,points[0])
        # image=drawPointToImage(image,points[12])

        # txt="%.0f , %.0f" % (points[0].x,points[0].y )
        # image=drawTextToImage(image,txt )
        # txt="%.0f , %.0f" % (points[12].x,points[12].y )
        # image=drawTextToImage(image,txt,origin=(20,60) )

     
    
      if len(results.multi_hand_landmarks)>1:

        if(points[0][12].x>points[1][12].x):
          RIGHT_INDEX=0
          LEFT_INDEX=1
        else:
          RIGHT_INDEX=1
          LEFT_INDEX=0
        
        txt="angle: %d" % (angles[LEFT_INDEX] )
        image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,25))
        txt="distance: %d" % (distances[LEFT_INDEX])
        image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,45))
      
        txt="angle: %d" % (angles[RIGHT_INDEX] )
        image=drawTextToImage(image,txt,origin=(RIGHT_ORIGIN_X,25))
        txt="distance: %d" % (distances[RIGHT_INDEX])
        image=drawTextToImage(image,txt,origin=(RIGHT_ORIGIN_X,45))
        
        if (fistsDetected[RIGHT_INDEX]):
          txt="FIST DETECTED"
          image=drawTextToImage(image,txt,origin=(RIGHT_ORIGIN_X,70),color=FIST_DETECTED_COLOR )

        if (fistsDetected[LEFT_INDEX]):
          txt="FIST DETECTED"
          image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,70),color=FIST_DETECTED_COLOR )
      else:
        txt="angle: %d" % (angles[0] )
        image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,30))
        txt="distance: %d" % (distances[0])
        image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,50))
        
        if (fistsDetected[0]):
          txt="FIST DETECTED"
          image=drawTextToImage(image,txt,origin=(LEFT_ORIGIN_X,70),color=FIST_DETECTED_COLOR )
    
    if (time()-t>TIME_INTERVAL):
      if (len(angles)>0 ):
        should_continue = 1 if len(angles)>1 else 0
        
        angle=int(angles[0])
        angle=limit(angle,0,180)
        light=fistsDetected[0]
        

        txt=str(angle)
        if len(txt)<3:
          txt="0"*(3-len(txt))+txt
        
        txt=txt.encode('utf-8')
        if len(txt)>3:
          print(txt)
        conn.sendall(txt)
        
        # 1st digit-->boolean
        # 2nd digit-->continue receiving
        txt=str(light)+str(should_continue)
        txt=txt.encode('utf-8')
        if len(txt)>2:
          print(txt)
        conn.sendall(txt)

        if should_continue:
          angle=int(angles[1])
          angle=limit(angle,0,180)
          light=fistsDetected[1]
        
          txt=str(angle)
          if len(txt)<3:
            txt="0"*(3-len(txt))+txt
          txt=txt.encode('utf-8')

          if len(txt)>3:
            print(txt)
          conn.sendall(txt)

          txt=str(light)
          txt=txt.encode('utf-8')
          conn.sendall(txt)
          
      t=time()
    
        
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
    counter=counter+1
    if counter>100:
      pass
      #break
cap.release()

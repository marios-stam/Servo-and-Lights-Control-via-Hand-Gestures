import math
import cv2

FIST_DISTANCE_THRESHOLD=100

def getAngle(p1,p2):
  dx=p1.x-p2.x
  dy=p1.y-p2.y
  
  angle=math.atan2(dx,dy)
  return  math.degrees(angle)

def getDistance(p1,p2):
    dx=p1.x-p2.x
    dy=p1.y-p2.y
    d=math.sqrt(dx**2+dy**2)
    return d

def drawTextToImage(image,text,origin=(20,30),color = (255, 0, 255)):
    # font 
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL 

    org=origin
    # fontScale 
    fontScale = 1
    # convert RGB to BGR 
    color= color[::-1]
    # Line thickness of 2 px 
    thickness = 2
    # Using cv2.putText() method 
    image = cv2.putText(image, text, org, font,  
                       fontScale, color, thickness, cv2.LINE_AA) 
    return image

def drawPointToImage(image,point,radius=10):
    x,y=point.x,point.y
    x,y=int(x),int(y)
    center_coordinates = (x,y)    
    # Blue color in BGR
    color = (0, 0, 255)
    
    # Line thickness of 2 px
    thickness = 4
    
    # Using cv2.circle() method
    # Draw a circle with blue line borders of thickness of 2 px
    image = cv2.circle(image, center_coordinates, radius, color, thickness)
    return image

def convertPointCoordsToImagePlane(image,point):
    height, width, channels = image.shape
    x,y=point.x,point.y
    
    return x*width,y*height 

def limit(x,xmin,xmax):
    return min(xmax,max(x,xmin))

def fistDetected(points):
    if len(points)<15:
        return False
    p1=points[0]
    p2=points[12]

    d=getDistance(p1,p2)
    
    return (d<FIST_DISTANCE_THRESHOLD)
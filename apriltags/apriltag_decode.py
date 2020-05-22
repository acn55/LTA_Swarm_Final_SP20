import cv2
from apriltag import apriltag
 
fname = 'test.jpg'
image = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
detector = apriltag("tag16h5")
dets = detector.detect(image)
for det in dets:
    print("%s: %6.1f,%6.1f" % (det["id"], det["center"][0], det["center"][1]))

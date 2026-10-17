import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0035.mp4')
n=0
while True:
    ok,im=c.read()
    if not ok: break
    n+=1
print(n)

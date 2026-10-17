import cv2, sys, numpy as np
vid=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]
rot = vid=='simulation_0017'
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
for i in idx:
    cap.set(cv2.CAP_PROP_POS_FRAMES,i); ok,f=cap.read()
    if rot: f=cv2.rotate(f,cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imwrite(f'frames/{vid}_up_f{i:03d}.png',f)

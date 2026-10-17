import cv2
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0305.mp4')
for i in [1,25,50,71]:
    cap.set(cv2.CAP_PROP_POS_FRAMES,i); ok,f=cap.read()
    cv2.imwrite(f'frames/full_0305_{i:03d}.png',cv2.resize(f,(1280,720)))

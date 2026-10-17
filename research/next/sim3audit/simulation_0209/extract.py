import cv2, sys, os
out='frames'
for vid in ['simulation_0202','simulation_0205','simulation_0206','simulation_0209','simulation_0203','simulation_0207']:
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
    w=cap.get(3); h=cap.get(4)
    print(vid,n,fps,w,h)
    frames=[]
    i=0
    while True:
        ok,fr=cap.read()
        if not ok: break
        if i in (0,n-1) or i==10:
            cv2.imwrite(f'{out}/{vid}_f{i:02d}.png',fr)
        i+=1
    print(' read',i)

import cv2, sys
for vid in ['simulation_0017','simulation_0017_segmented','simulation_0016']:
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
    w=cap.get(3); h=cap.get(4)
    print(vid,n,fps,w,h)
    for i in [0,30,60,n-1]:
        cap.set(cv2.CAP_PROP_POS_FRAMES,i); ok,f=cap.read()
        if ok: cv2.imwrite(f'frames/{vid}_f{i:03d}.png',f)

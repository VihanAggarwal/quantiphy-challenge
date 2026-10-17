import cv2,sys
for c in ['0303','0305','0307']:
    p=f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{c}.mp4'
    cap=cv2.VideoCapture(p)
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
    w=cap.get(3);h=cap.get(4)
    print(c,n,fps,w,h)
    for i in [0,12,24,48,71]:
        cap.set(cv2.CAP_PROP_POS_FRAMES,i); ok,f=cap.read()
        if ok:
            cv2.imwrite(f'frames/{c}_{i:03d}.png',cv2.resize(f,(1280,720)))

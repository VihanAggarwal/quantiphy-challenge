import cv2
boxes={1:(1339,711,659,284),25:(986,524,578,214),71:(577,300,468,148)}
for c in ['0303','0305','0307']:
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{c}.mp4')
    for i,(x,y,w,h) in boxes.items():
        cap.set(cv2.CAP_PROP_POS_FRAMES,i); ok,f=cap.read()
        p=25
        cr=f[y-p:y+h+p,x-p:x+w+p]
        s=1200/cr.shape[1]
        cv2.imwrite(f'frames/crop_{c}_{i:03d}.png',cv2.resize(cr,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC))

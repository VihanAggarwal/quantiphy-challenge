import cv2, sys, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0014%s.mp4'
def load(r):
    cap=cv2.VideoCapture(V%r); fr=[]
    while True:
        ok,im=cap.read()
        if not ok: break
        fr.append(im)
    return fr
if __name__=='__main__':
    for r in ['','s','x']:
        fr=load(r); print(r,len(fr),fr[0].shape)
        for k in [0,10,14,20]:
            cv2.imwrite(f'img/{r or "o"}_{k:02d}.png',fr[k])

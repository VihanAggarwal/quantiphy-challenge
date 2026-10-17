import cv2, sys, numpy as np
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
O='/home/user/quantiphy-challenge/research/next/labaudit2/0034/img/'
def read(v):
    c=cv2.VideoCapture(D+f'captured_0034{v}.mp4'); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    return fr
if __name__=='__main__':
    v=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]
    fr=read(v)
    for i in idx:
        cv2.imwrite(O+f'{v}_{i:02d}.png', fr[i])

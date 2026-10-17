import cv2, numpy as np, sys
v=sys.argv[1]; mode=sys.argv[2]; pos=int(sys.argv[3]); a=int(sys.argv[4]); b=int(sys.argv[5]); w=int(sys.argv[6]) if len(sys.argv)>6 else 2
fi=int(sys.argv[7]) if len(sys.argv)>7 else -1
if fi<0:
    img=cv2.imread(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_05/scr/bg_{v}.png').astype(float)
else:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES,fi); ok,img=c.read(); img=img.astype(float)
if mode=='col':  # vertical profile at x=pos, rows a..b
    p=img[a:b,pos-w:pos+w+1].mean(axis=1)
else:
    p=img[pos-w:pos+w+1,a:b].mean(axis=0)
for i,q in enumerate(p):
    print(a+i, ' '.join('%5.1f'%x for x in q[::-1]))

import cv2, numpy as np, sys
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_04/'
def frames(i, idx):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{i:04d}.mp4')
    out={}; n=0
    while True:
        ok,f=c.read()
        if not ok: break
        if n in idx: out[n]=f
        n+=1
    return out
ids=[int(x) for x in sys.argv[1].split(',')]
fr=[0,24,48]
rows=[]
for i in ids:
    F=frames(i,fr)
    row=[]
    for k in fr:
        im=cv2.resize(F[k],(480,270))
        cv2.putText(im,f'{i} f{k}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        row.append(im)
    rows.append(np.hstack(row))
cv2.imwrite(W+sys.argv[2],np.vstack(rows))

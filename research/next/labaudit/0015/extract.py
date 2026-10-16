import cv2, numpy as np, sys
R='/home/user/quantiphy-challenge/data/QuantiPhy/'
def load(tag):
    v={'o':'captured_0015','s':'captured_0015s','x':'captured_0015x'}[tag]
    c=cv2.VideoCapture(R+v+'.mp4'); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    return fr
if __name__=='__main__':
    for tag in 'osx':
        fr=load(tag)
        sel=list(range(0,len(fr),4))
        th=[cv2.resize(fr[i],(320,180)) for i in sel]
        while len(th)%5: th.append(np.zeros_like(th[0]))
        rows=[np.hstack(th[i:i+5]) for i in range(0,len(th),5)]
        m=np.vstack(rows)
        for k,i in enumerate(sel):
            cv2.putText(m,str(i),((k%5)*320+5,(k//5)*180+22),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
        cv2.imwrite(f'montage_{tag}.jpg',m,[cv2.IMWRITE_JPEG_QUALITY,85])

import cv2, numpy as np
base='/home/user/quantiphy-challenge/data/QuantiPhy/'
out='/home/user/quantiphy-challenge/research/next/labaudit/0031/frames/'
for s in ['','s','x']:
    c=cv2.VideoCapture(base+f'captured_0031{s}.mp4')
    print(s, c.get(cv2.CAP_PROP_FPS), c.get(cv2.CAP_PROP_FRAME_COUNT), c.get(cv2.CAP_PROP_FRAME_WIDTH), c.get(cv2.CAP_PROP_FRAME_HEIGHT))
    i=0; frames=[]
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(out+f'r{s or "0"}_{i:02d}.png',f)
        frames.append(f); i+=1
    sel=frames[::4]
    th=[cv2.resize(f,(320,180)) for f in sel]
    for k,t in enumerate(th):
        cv2.putText(t,str(k*4),(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
    while len(th)%4: th.append(np.zeros_like(th[0]))
    rows=[np.hstack(th[j:j+4]) for j in range(0,len(th),4)]
    cv2.imwrite(out+f'montage_{s or "0"}.png',np.vstack(rows))
    print(s,i)

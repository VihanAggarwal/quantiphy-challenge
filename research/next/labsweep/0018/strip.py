import cv2,sys,numpy as np
v=sys.argv[1]; a,b=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
x0,y0,x1,y1=[int(t) for t in sys.argv[4].split(',')]; sc=float(sys.argv[5]); ncol=int(sys.argv[6])
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
fr=[];i=0
while True:
    ok,f=c.read()
    if not ok: break
    if a<=i<=b:
        g=cv2.resize(f[y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_CUBIC)
        cv2.putText(g,str(i),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
        fr.append(g)
    i+=1
h,w=fr[0].shape[:2]
rows=[]
for r in range(0,len(fr),ncol):
    row=fr[r:r+ncol]
    while len(row)<ncol: row.append(np.zeros_like(fr[0]))
    rows.append(np.hstack(row))
cv2.imwrite(out,np.vstack(rows))

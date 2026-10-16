import cv2, numpy as np, json, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
r=sys.argv[1]; key=sys.argv[2]; idx=[int(x) for x in sys.argv[3].split(',')]; half=int(sys.argv[4]); sc=int(sys.argv[5]); outp=sys.argv[6]
T=json.load(open(d+'track_x.json'))
ims=[]
for i in idx:
    im=cv2.imread(d+'frames/%s_%02d.png'%(r,i))
    t=T[str(i)][key]; cx,cy=int(round(t['cx'])),int(round(t['cy']))
    c=im[cy-half:cy+half,cx-half:cx+half]
    c=cv2.resize(c,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
    cv2.putText(c,str(i),(3,18),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
    ims.append(c)
nc=int(sys.argv[7]) if len(sys.argv)>7 else 6
while len(ims)%nc: ims.append(np.zeros_like(ims[0]))
cv2.imwrite(d+outp,np.vstack([np.hstack(ims[k:k+nc]) for k in range(0,len(ims),nc)]))

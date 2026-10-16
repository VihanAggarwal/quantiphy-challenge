# crops centred on tracked object positions
import cv2, numpy as np, json, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
T=json.load(open(d+'tracks.json'))
pref,obj=sys.argv[1],sys.argv[2]; frames=[int(x) for x in sys.argv[3].split(',')]; half=int(sys.argv[4]); s=float(sys.argv[5]); out=sys.argv[6]
key={'':'o','s':'s','x':'x'}[pref]
ims=[]
for i in frames:
    im=cv2.imread(d+f'frames/0020{pref}_f{i:02d}.png')
    u,v=T[key][obj][str(i)][:2]; u=int(round(u)); v=int(round(v))
    im=cv2.copyMakeBorder(im,half,half,half,half,cv2.BORDER_CONSTANT)
    c=im[v:v+2*half, u:u+2*half]
    c=cv2.resize(c,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
    # grid every 10 px
    for k in range(0,2*half,10):
        cv2.line(c,(int(k*s),0),(int(k*s),4),(0,0,255),1); cv2.line(c,(0,int(k*s)),(4,int(k*s)),(0,0,255),1)
    cv2.putText(c,f'f{i}',(5,15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1); ims.append(c)
ncol=int(sys.argv[7]) if len(sys.argv)>7 else 6
while len(ims)%ncol: ims.append(np.zeros_like(ims[0]))
cv2.imwrite(d+out,np.vstack([np.hstack(ims[k:k+ncol]) for k in range(0,len(ims),ncol)]))

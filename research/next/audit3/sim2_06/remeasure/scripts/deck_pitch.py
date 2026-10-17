import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
v=sys.argv[1]
c=cv2.VideoCapture(D+v+'.mp4'); G=[]
for k in range(50):
    ok,f=c.read()
    if not ok: break
    if k%4==0: G.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
g=np.median(np.array(G),0)
sm=lambda a,k: np.convolve(np.pad(a,k//2,mode="edge"),np.ones(k)/k,mode="valid")
rows={}
for y in range(896,925):
    row=g[y,:]; hp=row-sm(row,31)
    mins=[x for x in range(6,1914) if hp[x]==hp[x-6:x+7].min() and hp[x]<-12]
    rows[y]=[x+0.5*(hp[x-1]-hp[x+1])/(hp[x-1]-2*hp[x]+hp[x+1]) for x in mins]
print('row 924', np.round(rows[924],1))
print('row 910', np.round(rows[910],1))
print('row 898', np.round(rows[898],1))

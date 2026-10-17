import cv2,numpy as np,json
E=json.load(open('edges2.json'))
pl=E['left_L']; pr=E['right_L']; pn=E['near']
# far edge: refit with L channel on averaged static frame
img=cv2.imread('static_mean.png'); L=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)[...,0].astype(float)
L=cv2.GaussianBlur(L,(0,0),0.8)
fe=[]
for x in list(range(572,632,1))+list(range(800,846,1)):
    p=L[412:440,x]; d=np.diff(p); k=np.argmax(d)
    if 0<k<len(d)-1 and d[k]>3:
        a,b_,c=d[k-1],d[k],d[k+1]; off=0.5*(a-c)/(a-2*b_+c)
        fe.append((x,412+k+0.5+off))
fe=np.array(fe); pf=np.polyfit(fe[:,0],fe[:,1],1)
r=fe[:,1]-np.polyval(pf,fe[:,0]); 
m=np.abs(r)<2*r.std(); pf=np.polyfit(fe[m,0],fe[m,1],1)
print('far L fit',pf,'rms',np.std(fe[m,1]-np.polyval(pf,fe[m,0])).round(2), 'n',m.sum())
def inter(pv,ph):
    a,b_=pv; c,d=ph; y=(c*b_+d)/(1-a*c); x=a*y+b_; return [x,y]
C={'NL':inter(pl,pn),'NR':inter(pr,pn),'FL':inter(pl,pf),'FR':inter(pr,pf)}
print({k:np.round(v,1).tolist() for k,v in C.items()})
json.dump(C,open('table_corners2.json','w'))
imgp=np.array([C['NL'],C['NR'],C['FR'],C['FL']],float)
W,Dp=0.603,0.760
obj=np.array([[0,0,0],[W,0,0],[W,Dp,0],[0,Dp,0]],float)
for f in [680,711,740,770,800,850]:
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    ok,rv,tv=cv2.solvePnP(obj,imgp,K,None,flags=cv2.SOLVEPNP_IPPE)
    pr_,_=cv2.projectPoints(obj,rv,tv,K,None)
    err=np.linalg.norm(pr_.reshape(-1,2)-imgp,axis=1)
    R,_=cv2.Rodrigues(rv); n=R[:,2]; cam=-R.T@tv.ravel()
    yh=360-(n[2]*f+n[0]*(735-640))/n[1]
    print('f',f,'reproj',err.round(2),'cam',cam.round(3),'n',n.round(4),'horizon y at x=735: %.1f'%yh)

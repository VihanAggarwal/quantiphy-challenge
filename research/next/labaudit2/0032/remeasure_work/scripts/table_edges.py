import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0032x.mp4'); fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f)
def sub_boundary(prof, th):
    # first index where prof crosses th upward, subpixel
    idx=np.where(prof>th)[0]
    if len(idx)==0: return None
    a=idx[0]
    if a==0: return 0.0
    return a-1+(th-prof[a-1])/(prof[a]-prof[a-1])
res={}
for fi in (44,46,48):
    g=fr[fi].astype(float).sum(2)/3
    L=[];R=[];T=[];F=[]
    for y in range(432,481):
        row=g[y]
        xl=sub_boundary(row[400:720],40); L.append((400+xl,y))
        xr=sub_boundary(row[960:700:-1],40); R.append((960-xr,y))
    for x in range(600,830,5):
        col=g[400:470,x]
        yt=sub_boundary(col,40); T.append((x,400+yt))
    for x in range(480,950,5):
        col=g[465:515,x-1:x+2].mean(1)
        # front top edge: strongest negative gradient (bright top -> dark face)
        d=np.diff(col); k=np.argmin(d)
        # subpixel via half level
        hi=col[max(k-1,0)]; lo=col[k+2]
        th=(hi+lo)/2
        # find crossing near k
        for j in range(max(k-2,0),min(k+3,len(col)-1)):
            if col[j]>=th and col[j+1]<th:
                yy=j+(col[j]-th)/(col[j]-col[j+1]); break
        F.append((x,465+yy))
    def fitx(P):  # x = a + b*y
        P=np.array(P); A=np.c_[np.ones(len(P)),P[:,1]]; c,_,_,_=np.linalg.lstsq(A,P[:,0],rcond=None)
        r=P[:,0]-A@c; return c, r.std()
    def fity(P):
        P=np.array(P); A=np.c_[np.ones(len(P)),P[:,0]]; c,_,_,_=np.linalg.lstsq(A,P[:,1],rcond=None)
        r=P[:,1]-A@c; return c, r.std()
    cl,sl=fitx(L); cr,sr=fitx(R); ct,st=fity(T); cf,sf=fity(F)
    print(fi,'left x=%.2f%+.4f*y sd%.2f'%(cl[0],cl[1],sl),'right x=%.2f%+.4f*y sd%.2f'%(cr[0],cr[1],sr),'far y=%.2f%+.5f*x sd%.2f'%(ct[0],ct[1],st),'front y=%.2f%+.5f*x sd%.2f'%(cf[0],cf[1],sf))
    # lines as homogeneous
    def lx(c): return np.array([1,-c[1],-c[0]])  # x - b y - a = 0
    def ly(c): return np.array([-c[1],1,-c[0]])  # y - b x - a = 0
    Ll,Lr,Lt,Lf=lx(cl),lx(cr),ly(ct),ly(cf)
    def X(a,b):
        p=np.cross(a,b); return p[:2]/p[2]
    corners=dict(FL=X(Ll,Lf),FR=X(Lr,Lf),BR=X(Lr,Lt),BL=X(Ll,Lt))
    print('  corners', {k:np.round(v,1).tolist() for k,v in corners.items()})
    print('  VP sides', np.round(X(Ll,Lr),1), ' VP front/back', np.round(X(Lt,Lf),1))
    res[fi]=corners
np.save('/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/corners.npy', res[48])

import cv2, numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
f=cv2.imread(D+'frames/captured_0023s_48.png').astype(np.float32)
B,G,R=f[...,0],f[...,1],f[...,2]
m=(R-B>25).astype(np.uint8)
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); m=(lab==k)
def rowfit(y0,y1,side):
    P=[]
    for y in range(y0,y1):
        xx=np.nonzero(m[y])[0]
        P.append((y, xx.min() if side=='L' else xx.max()))
    P=np.array(P,float)
    a,b=np.polyfit(P[:,0],P[:,1],1)  # x = a*y+b
    return a,b
aL,bL=rowfit(450,526,'L'); aR,bR=rowfit(450,522,'R')
print('left x=%.4f*y+%.2f  right x=%.4f*y+%.2f'%(aL,bL,aR,bR))
# far edge: top boundary columns
def colfit(xr):
    P=[]
    for x in xr:
        yy=np.nonzero(m[:,x])[0]; P.append((x,yy.min()))
    P=np.array(P,float); c,d=np.polyfit(P[:,0],P[:,1],1); return c,d,P
cF1,dF1,P1=colfit(list(range(440,476))); cF2,dF2,P2=colfit(list(range(690,770)))
print('far edge pts left',P1[::5].tolist()); print('far right',P2[::10].tolist())
P=np.vstack([P1,P2]); cF,dF=np.polyfit(P[:,0],P[:,1],1)
print('far edge y=%.4f*x+%.2f'%(cF,dF))
# front edge: luminance gradient in column window
gray=cv2.cvtColor(f.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)
gy=cv2.Sobel(cv2.GaussianBlur(gray,(5,5),1),cv2.CV_32F,0,1,ksize=3)
Pf=[]
for x in list(range(300,470,4))+list(range(700,900,4)):
    col=-gy[515:545,x]  # bright above, dark below => negative gy... take max of -gy
    y=515+np.argmax(col); Pf.append((x,y))
Pf=np.array(Pf,float); cB,dB=np.polyfit(Pf[:,0],Pf[:,1],1)
res=Pf[:,1]-(cB*Pf[:,0]+dB); print('front edge y=%.4f*x+%.2f  resid sd %.2f'%(cB,dB,res.std()))
def inter_xy(a,b,c,d):
    # x=a*y+b, y=c*x+d
    y=(c*b+d)/(1-c*a); x=a*y+b; return x,y
FL=inter_xy(aL,bL,cB,dB); FR=inter_xy(aR,bR,cB,dB); BL=inter_xy(aL,bL,cF,dF); BR=inter_xy(aR,bR,cF,dF)
corners=dict(FL=FL,FR=FR,BL=BL,BR=BR)
for k,v in corners.items(): print(k,'%.1f %.1f'%v)
json.dump({k:list(v) for k,v in corners.items()},open(D+'scripts/table_corners_s48.json','w'))

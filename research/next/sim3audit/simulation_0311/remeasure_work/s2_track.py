import cv2, numpy as np, json
W='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0311/remeasure_work/'
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0311.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
bg=cv2.imread(W+'bg.png')
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
def carmask(f):
    d=np.abs(f.astype(np.int16)-bg.astype(np.int16)).max(axis=2)
    b,g,r=[f[:,:,i].astype(np.int16) for i in range(3)]
    red=(r-np.maximum(g,b)>40)
    m=((d>30)&red).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<=1: return m*0
    k=1+np.argmax(st[1:,4])
    m=(lab==k).astype(np.uint8)
    m=cv2.dilate(m,np.ones((25,25),np.uint8))
    # also include dark car parts (windows/diffuser) inside: use diff mask within dilated red hull
    m2=((d>30).astype(np.uint8))&m
    return m2
# tracks: dict id -> {frame: (x,y)}
tracks={}; nid=0
active={}  # id -> pt
lk=dict(winSize=(21,21),maxLevel=4,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,0.01))
masks=[]
for k in range(2,72):
    m=carmask(fr[k]); masks.append(int(m.sum()))
    if active:
        ids=list(active.keys()); p0=np.float32([active[i] for i in ids]).reshape(-1,1,2)
        p1,s1,_=cv2.calcOpticalFlowPyrLK(G[k-1],G[k],p0,None,**lk)
        p0b,s2,_=cv2.calcOpticalFlowPyrLK(G[k],G[k-1],p1,None,**lk)
        fb=np.linalg.norm(p0-p0b,axis=2).ravel()
        new={}
        for j,i in enumerate(ids):
            x,y=p1[j,0]
            if s1[j] and s2[j] and fb[j]<0.25 and 0<=x<2560 and 0<=y<1440 and m[int(y),int(x)]:
                new[i]=(float(x),float(y)); tracks[i][k]=(float(x),float(y))
        active=new
    # detect new
    mm=m.copy()
    for (x,y) in active.values(): cv2.circle(mm,(int(x),int(y)),8,0,-1)
    pts=cv2.goodFeaturesToTrack(G[k],maxCorners=400,qualityLevel=0.01,minDistance=8,mask=mm*255)
    if pts is not None:
        for p in pts.reshape(-1,2):
            tracks[nid]={k:(float(p[0]),float(p[1]))}; active[nid]=(float(p[0]),float(p[1])); nid+=1
out={str(i):{str(k):v for k,v in t.items()} for i,t in tracks.items() if len(t)>=6}
json.dump(out,open(W+'tracks.json','w'))
L=[len(t) for t in tracks.values()]
print('ntracks',len(out),'len>=20',sum(l>=20 for l in L),'len>=40',sum(l>=40 for l in L))

from tab import *
import cv2
t=pd.read_pickle(W+'/T.pkl')
vids=t[t.fam.notna()].drop_duplicates('video_id')[['video_id','video_path','fam','base']]
E={}
for r in vids.itertuples():
    cap=cv2.VideoCapture(r.video_path); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ims=[]
    for p in (0.0,0.5):
        cap.set(cv2.CAP_PROP_POS_FRAMES,int(p*(n-1))); ok,im=cap.read()
        if not ok: continue
        g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY); h,w=g.shape
        g=cv2.resize(g,(256,int(round(256*h/w))),interpolation=cv2.INTER_AREA).astype(np.float32)
        hp=g-cv2.GaussianBlur(g,(0,0),6)          # high-pass: removes lighting gradients
        mag=np.abs(hp); mag=cv2.GaussianBlur(mag,(0,0),1.5)
        ims.append(mag)
    cap.release()
    E[r.video_id]=ims
pickle.dump(E,open(W+'/edges.pkl','wb'))
def ncc(a,b):
    if a.shape!=b.shape: return -1.0
    a=a-a.mean(); b=b-b.mean(); return float((a*b).sum()/np.sqrt((a*a).sum()*(b*b).sum()+1e-9))
rows=[]
for f,g in vids.groupby('fam'):
    vs=list(g.video_id)
    for i,a in enumerate(vs):
        for b in vs[i+1:]:
            s=max([ncc(x,y) for x in E[a] for y in E[b]] or [-1])
            rows.append(dict(fam=f,a=a,b=b,encc=s))
P=pd.DataFrame(rows); P.to_pickle(W+'/pairs_edge.pkl'); print(len(P))

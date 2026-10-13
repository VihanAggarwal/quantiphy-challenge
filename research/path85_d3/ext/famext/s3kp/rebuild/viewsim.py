from build_s3 import *
import cv2
res,allch=pickle.load(open(OUT+'/build_res.pkl','rb'))
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
_c={}
def thumb(v):
    if v in _c: return _c[v]
    cap=cv2.VideoCapture(D+v+'.mp4'); n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); cap.set(cv2.CAP_PROP_POS_FRAMES,n//2); ok,f=cap.read(); cap.release()
    g=cv2.cvtColor(cv2.resize(f,(64,64),interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2GRAY).astype(float)
    g=(g-g.mean())/(g.std()+1e-6); _c[v]=g; return g
def ncc(a,b): return float((thumb(a)*thumb(b)).mean())
allpairs={}
for q in allch['S3_PK_DS']:
    per=per_base_values(ti,eq,q,include_self=True)
    vids=sorted(set(ti.loc[p,'video_id'] for b,(rk,vv,p) in per.items()))
    for i,a in enumerate(vids):
        for b in vids[i+1:]:
            if (a,b) not in allpairs: allpairs[(a,b)]=ncc(a,b)
S=pd.Series(allpairs).sort_values(ascending=False)
print(S[S>0.8].round(3).to_string())
S.to_pickle('viewsim.pkl')

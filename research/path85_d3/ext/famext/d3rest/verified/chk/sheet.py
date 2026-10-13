import sys, numpy as np, pandas as pd, cv2
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
t=pd.read_pickle(SP+'/ext/d3rest/work/TS_ext.pkl')
vids=sys.argv[1].split(','); out=sys.argv[2]
fr=[float(x) for x in (sys.argv[3].split(',') if len(sys.argv)>3 else ['0.05','0.5','0.95'])]
W=int(sys.argv[4]) if len(sys.argv)>4 else 480
rows=[]
for v in vids:
    g=t[t.video_id==v]
    if not len(g): print('missing',v); continue
    p=g.video_path.iloc[0]
    cap=cv2.VideoCapture(p); n=int(cap.get(7)); ims=[]
    for f in fr:
        cap.set(1,int(f*(n-1))); ok,im=cap.read()
        if not ok: im=np.zeros((270,480,3),np.uint8)
        im=cv2.resize(im,(W,int(W*im.shape[0]/im.shape[1])))
        ims.append(im)
    hmax=max(i.shape[0] for i in ims); ims=[np.pad(i,((0,hmax-i.shape[0]),(0,0),(0,0))) for i in ims]
    r=np.hstack(ims); cv2.putText(r,v,(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2); rows.append(r)
wmax=max(r.shape[1] for r in rows); rows=[np.pad(r,((0,4),(0,wmax-r.shape[1]),(0,0))) for r in rows]
cv2.imwrite(out,np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,80])
print('ok',out)

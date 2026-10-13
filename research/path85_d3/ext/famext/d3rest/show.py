import sys, numpy as np, pandas as pd, cv2
sys.path.insert(0,'/home/user/quantiphy-challenge')
SP='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
W=SP+'/big/scenegraph/work'
t=pd.read_pickle(W+'/TS.pkl')
p5=pd.read_csv('/home/user/quantiphy-challenge/submissions/trackA_probe5_families_merged.csv').set_index('id').parsed_value
t['p5']=t.qid.map(p5)
vids=[v for v in sys.argv[1].split(",") if (t.video_id==v).any()]
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',90); pd.set_option('display.max_rows',500)
for v in vids:
    g=t[t.video_id==v]
    print(f'=== {v} {g.category.iloc[0]} fam={g.fam.iloc[0]} prior="{g.prior.iloc[0]}"')
    print('   depth:', g.depth_info.iloc[0][:300].replace('\n',' | '))
    for r in g.itertuples():
        print(f'   {r.qid} {r.tkind:12s} {r.question[:90]:90s} p5={r.p5:.4g} v3={r.v3:.4g} {str(r.method)[:22]}')
if len(sys.argv)>2:
    rows=[]
    for v in vids:
        p=t[t.video_id==v].video_path.iloc[0]
        cap=cv2.VideoCapture(p); n=int(cap.get(7)); ims=[]
        for f in (0.05,0.5,0.95):
            cap.set(1,int(f*(n-1))); ok,im=cap.read()
            if not ok: im=np.zeros((180,320,3),np.uint8)
            im=cv2.resize(im,(400,int(400*im.shape[0]/im.shape[1])))
            ims.append(im)
        hmax=max(i.shape[0] for i in ims); ims=[np.pad(i,((0,hmax-i.shape[0]),(0,0),(0,0))) for i in ims]
        r=np.hstack(ims); cv2.putText(r,v,(5,22),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2); rows.append(r)
    wmax=max(r.shape[1] for r in rows); rows=[np.pad(r,((0,4),(0,wmax-r.shape[1]),(0,0))) for r in rows]
    cv2.imwrite(sys.argv[2],np.vstack(rows))

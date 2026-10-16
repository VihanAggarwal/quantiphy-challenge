import numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit/0031/'
tr=json.load(open(D+'track.json'))
cx,cy=640,360
for f in [711]:
    pl=np.load(D+f'scripts/plane_f{f}.npy'); n=pl[:3]; W=pl[3]; L=pl[4]
    Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1.]]))
    for scale_name,h in [('W60.3',60.3/W),('L76',76.0/L)]:
        print('f',f,scale_name,'cam height',round(h,2))
        for r in ['0','x']:
            for name,Dm,key in [('tennis',6.7,'T'),('white',4.0,'W')]:
                rows=[]
                for i in range(49):
                    t=tr[r][key][i]
                    if t[1] is None: rows.append(None); continue
                    u,v,dpx=t[1],t[2],t[6]
                    ray=Kinv@np.array([u,v,1.]); 
                    # centre lies on plane n.X = h - Dm/2  (n.X = h for table plane; ball centre closer to camera by r)
                    X=(h-Dm/2)*ray/(n@ray)
                    Rplane=np.linalg.norm(X)
                    Rsize=f*Dm/dpx
                    Xs=Rsize*ray/np.linalg.norm(ray)
                    rows.append((i,Rplane,Rsize,X,Xs))
                print(' render',r,name)
                for i in [0,10,20,25,30,34,36,38,39,40,42]:
                    if rows[i] is None: continue
                    _,Rp,Rs,X,Xs=rows[i]
                    print('   fr',i,'Rplane %.1f Rsize %.1f ratio %.3f'%(Rp,Rs,Rp/Rs))
                # speeds around frame 38: central over windows
                for (a,b) in [(36,40),(34,42),(37,39),(38,39),(38,40),(40,41)]:
                    if rows[a] and rows[b]:
                        vp=np.linalg.norm(rows[b][3]-rows[a][3])/(b-a)*24
                        vs=np.linalg.norm(rows[b][4]-rows[a][4])/(b-a)*24
                        print('   v[%d,%d] plane %.1f size %.1f cm/s @24fps'%(a,b,vp,vs))

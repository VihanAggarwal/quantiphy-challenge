import numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit/0031/'
tr=json.load(open(D+'track.json')); ci=json.load(open(D+'circ.json'))
f=711.; cx,cy=640,360
Kinv=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1.]]))
pl=np.load(D+'scripts/plane_f711.npy'); n=pl[:3]; W=pl[3]; L=pl[4]
def pos_plane(u,v,h,Dm):
    ray=Kinv@np.array([u,v,1.]); return (h-Dm/2)*ray/(n@ray)
def pos_size(u,v,d,Dm):
    ray=Kinv@np.array([u,v,1.]); return f*Dm/d*ray/np.linalg.norm(ray)
res={}
for r in ['0','x']:
    for key,name,Dm,(a,b) in [('W','white',4.0,(30,46)),('T','tennis',6.7,(28,42))]:
        fr=np.arange(a,b+1)
        u=np.array([tr[r][key][i][1] for i in fr]); v=np.array([tr[r][key][i][2] for i in fr])
        dm=np.array([tr[r][key][i][6] for i in fr]); dc=np.array([ci[r][key][i][3] for i in fr])
        out=[]
        for deg in [1,2]:
            pu=np.polyfit(fr,u,deg); pv=np.polyfit(fr,v,deg)
            pdm=np.polyfit(fr,1/dm,deg); pdc=np.polyfit(fr,1/dc,deg)
            for t0,fps,lab in [(38.4,24,'t*24'),(40.0,25,'t*25')]:
                eps=0.5
                def P(route,t):
                    uu,vv=np.polyval(pu,t),np.polyval(pv,t)
                    if route=='planeW': return pos_plane(uu,vv,60.3/W,Dm)
                    if route=='planeL': return pos_plane(uu,vv,76.0/L,Dm)
                    if route=='size_mask': return pos_size(uu,vv,1/np.polyval(pdm,t),Dm)
                    if route=='size_circ': return pos_size(uu,vv,1/np.polyval(pdc,t),Dm)
                s=[]
                for route in ['planeW','planeL','size_mask','size_circ']:
                    vel=np.linalg.norm(P(route,t0+eps)-P(route,t0-eps))/(2*eps)*fps
                    s.append('%s %.1f'%(route,vel))
                print(r,name,'deg',deg,lab,' | '.join(s), '| R@t0 planeW %.1f size_circ %.1f'%(np.linalg.norm(P('planeW',t0)),np.linalg.norm(P('size_circ',t0))))

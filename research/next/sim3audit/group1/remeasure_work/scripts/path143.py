import numpy as np, json
tr=json.load(open('../simulation_0143_track2.json'))
top=np.array([d['top'] for d in tr],float)
# head-peak frames (local minima of top) refined by parabola on 5-frame smoothed
uniform_filter1d=lambda a,k: np.convolve(np.pad(a,1,mode="edge"),np.ones(3)/3,"valid")
ts=uniform_filter1d(top,3)
pk=[]
for i in range(1,99):
    if ts[i]<=ts[i-1] and ts[i]<ts[i+1]:
        a,b,c=np.polyfit([i-1,i,i+1],ts[i-1:i+2],2); pk.append(-b/(2*a))
print('head peaks',np.round(pk,1))
yh=540.; cx=960.; Hc=1.286
F=[(0,945,836),(12,795,824),(24.5,716,794),(36.5,655,766),(49,722,735),(61.5,770,713),(74.5,821,694),(87,777,682),(99,738,673)]
for K in [1250,2135,2421]:
    P=np.array([[n,(x-cx)*Hc/(y-yh),K/(y-yh)] for n,x,y in F])
    d=np.hypot(np.diff(P[:,1]),np.diff(P[:,2]))
    print('K',K,'steps',np.round(d,2),'mean step',round(d.mean(),3),' speeds(24fps)',np.round(d/np.diff(P[:,0])*24,2))

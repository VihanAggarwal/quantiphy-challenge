import numpy as np, json
yh=540.
def run(clip,F,Hc):
    tr=json.load(open(f'../{clip}_track2.json'))
    top=np.array([d['top'] for d in tr],float)
    n=np.arange(len(top))
    fr=np.array([f[0] for f in F]); w=np.array([1/(f[2]-yh) for f in F])
    wi=np.interp(n,fr,w)
    Ht=Hc*(1+(yh-top)*wi)
    print(clip)
    for i in range(0,len(top)):
        print(i, int(top[i]), round(Ht[i],3), end=' | ')
        if i%6==5: print()
    print()
    return Ht
F143=[(0,945,836),(12,795,824),(24.5,716,794),(36.5,655,766),(49,722,735),(61.5,770,713),(74.5,821,694),(87,777,682),(99,738,673)]
# 0141 plants: heel bottoms at 1051,970,912,867,832 ; mid-stance at head peaks -0.5,12,24.5,37,49.5; pelvis ~ above ankle
F141=[(-0.5,0,1051),(12,0,970),(24.5,0,912),(37,0,867),(49.5,0,832),(62,0,540+1/(1/292+3.67e-4))]
run('simulation_0143',F143,1.286)
run('simulation_0141',F141,1.282)

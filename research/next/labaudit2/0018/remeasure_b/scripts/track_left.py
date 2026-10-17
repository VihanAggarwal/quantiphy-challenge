import sys, json
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0018/remeasure_b/scripts')
sys.argv=[sys.argv[0]]+sys.argv[1:]
import numpy as np, cv2
import track2 as T
vid=T.vid
# soccer ball: bright white/black blob; gate = not skin (low saturation)
def lowsat(i): return (T.hsv[i][...,1] < 60).astype(np.uint8)
tr=json.load(open(f'{T.OUT}/tracks_{vid}.json'))
tr['soccer']=T.track('soccer',(542,262),range(20,49),50,gate=lowsat,minarea=60)
tr['box']=T.track('box',(481,264),range(20,49),50,gate=lowsat,minarea=60)
json.dump(tr,open(f'{T.OUT}/tracks_{vid}.json','w'))
for k in ['soccer','box']:
    print(k)
    for i,r in tr[k].items():
        print(' ',i,None if r is None else ([round(x,1) for x in r['c']],r['bb'],r['a']))

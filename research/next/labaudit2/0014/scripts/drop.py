import cv2, numpy as np, sys
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0014/scripts')
from frames import load
fr=load('')
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in fr]
# person region (behind table, upper area) excluding ball/board area
mask=np.zeros_like(g[0],bool); mask[150:300,380:700]=True; mask[240:330,500:620]=False
mask2=np.zeros_like(g[0],bool); mask2[480:640,440:700]=True  # legs under the table
for k in range(0,30):
    d1=np.abs(g[k+1]-g[k])[mask].mean(); d2=np.abs(g[k+1]-g[k])[mask2].mean()
    print(k,'->',k+1,f'upper {d1:5.2f}  lower {d2:5.2f}', '*' if k==11 else '')

import sys, json, pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',70)
F='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/ext/pool2d/rebuild/'
t=pd.read_pickle(F+'T.pkl').set_index('qid')
for name in sys.argv[1:]:
    J=json.load(open(F+name+'.json'))
    C=pd.DataFrame.from_dict(J['changes'],orient='index'); C.index=C.index.astype(int)
    C['cat']=t.loc[C.index,'category']; C['vid']=t.loc[C.index,'video_id']; C['q']=t.loc[C.index,'question']; C['prior']=t.loc[C.index,'prior']
    C['cam']=t.loc[C.index,'cam']; C['lr']=np.log(C.new/C.old)
    C=C.sort_values('lr',key=abs,ascending=False)
    print(name, len(C), C.cat.value_counts().to_dict())
    print(C.head(25)[['cat','vid','q','prior','old','new','why','lr']].to_string())

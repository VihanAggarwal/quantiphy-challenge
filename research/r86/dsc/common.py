import pandas as pd, numpy as np, re
ROOT='/home/user/quantiphy-challenge'
def load():
    d=pd.read_parquet(f'{ROOT}/data/QuantiPhy/test_dataset.parquet')
    d['qid']=np.arange(1,len(d)+1)
    sub=pd.read_csv(f'{ROOT}/submissions/trackA_combo3_on_combo2.csv')
    assert (sub.id.values==d.qid.values).all()
    d['pred']=sub.parsed_value.values
    d['cg']=d.video_type.str[0].map({'S':'S','V':'D','A':'D'})+d.video_type.str[1]
    return d
def loadval():
    v=pd.read_csv(f'{ROOT}/data/QuantiPhy-validation/validation_dataset.csv')
    v=v.rename(columns={'ground_truth_prior':'prior','ground_truth_posterior':'y'})
    return v
def mra(p,g):
    e=abs(p-g)/abs(g)
    th=np.array([.5,.55,.6,.65,.7,.75,.8,.85,.9,.95])
    return float(np.mean(e<1-th))

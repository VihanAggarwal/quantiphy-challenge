"""D3/S3 non-lab rows asking the same kind (speed/acceleration) of the same object that the clip's OWN prior states.
How far is the current answer from the stated value? (validation labels: evaluation only)."""
from lofo import *
df = pp._questions(load_split('test'))
facts = pp._parse_facts(df)
own = {}
for f in facts:
    own.setdefault(f.video_id, []).append(f)
cur = read_sub(); vl = val_labels()
rows = []
for r in df.itertuples():
    if r.category not in ('D3', 'S3') or r.video_source == 'lab': continue
    s = pp._spec(r)
    if s.kind not in ('speed', 'acceleration') or len(s.objs) != 1 or s.to_si is None: continue
    for f in own.get(r.video_id, []):
        if f.kind != s.kind or pp._same_object(s.objs[0], f.obj) < 0.6: continue
        st = f.si / s.to_si
        rows.append(dict(qid=r.qid, cat=r.category, video=r.video_id, q=r.question[:70], line=f.line, timed=f.timed, stated=st,
                         cur=cur[r.qid], ens=ENS.get(r.qid, np.nan), val=vl.get(r.qid, np.nan)))
X = pd.DataFrame(rows).drop_duplicates('qid')
X['lr'] = np.log(X.cur / X.stated)
pd.set_option('display.width', 260); pd.set_option('display.max_rows', 200); pd.set_option('display.max_colwidth', 70)
print(len(X), X.groupby('cat').size().to_dict(), ' |lr|>.05:', (X.lr.abs() > .05).sum())
print(X.round(3).to_string())
X.to_pickle(OUT / 'ownprior.pkl')

# Review of the Gemini (Jules) lab motion study (2026-10-13)

Jules could not push; its NOTES.md, generate_candidate.py and the 62 changed rows were pasted into the chat
(rows: lab_candidate_changes.txt, "qid new_value"). Checked against p21 and the raw Claude direct answers
(runs/test_v1_high_854/test.csv).

Verdict: NOT adopted.
- The "scene ratio" (stated prior speed / measured prior speed) is 0.958-1.034 for 5 of the 7 events and 1.131
  for captured_0054 (its regex `captured_\d+` merges the separate events 0054a (1.37) and 0054b (1.10)).
- generate_candidate.py sets new = Claude's RAW direct answer x ratio, discarding p21's value for those rows
  (family facts, render pooling, lab rules, emulator). gem/direct is exactly the ratio on every row, while
  gem/p21 ranges 0.57-8.4; 34 of 62 rows move by more than 20%. So the change is mostly "revert 62 rows to the
  raw direct answer", which earlier leaderboard probes had replaced on purpose; it is not a per-scene correction.
- The +0.022 validation claim cannot be reproduced (no validation script was provided; its base 0.722 differs
  from its own time-mapping base 0.646). 5 of the 62 test rows are validation overlaps (unscored).
- Time-mapping finding (forward difference / +-1 frame shifts do not help) agrees with PROBES.md.
- +5 cm depth bias: tuned on ~18 validation rows, contradicts the stated lab size priors (sizes already read
  1.056x stated); not adopted.
A principled variant (p21 x ratio for 0054a/b only) would change ~40 rows by 10-37%; unvalidated, not built.

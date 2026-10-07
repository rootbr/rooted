#!/usr/bin/env python3
"""Hand-built kb-corpus inventory for the audit workflow: make-corpus-inventory.py <cards-dir> <out.md> "<new in this change>" "<validator warnings note>" """
import sys,os,re,glob
cdir,out,new,warn=sys.argv[1:5]
rows=[]
for f in sorted(glob.glob(os.path.join(cdir,"*.md"))):
    t=open(f,encoding="utf-8").read()
    fm=t.split("---")[1]
    g=lambda k: re.search(rf"^{k}:\s*(.+)$",fm,re.M).group(1).strip()
    rows.append(f"| {g('rule_id')} | {g('domain')} | {g('check_kind')} | {g('severity_default')} | `{os.path.basename(f)}` | {t.count(chr(10))+1} |")
hdr=f"""# Discovery inventory — {cdir} (the corpus directory)

| Field | Content |
|--|--|
| `target_type` | kb-corpus |
| `tier` | cold |
| `line_count`, `token_estimate` | {len(rows)} cards; see the per-card rows |
| `taxonomy` | plugins/code-quality/skills/software-craft/references/craft-cards-taxonomy.md (schema and controlled vocabulary); provenance map plugins/code-quality/skills/software-craft/references/craft-cards-provenance.md; pending rules plugins/code-quality/skills/software-craft/references/pending-evidence.md |
| `validator` | python3 plugins/code-quality/skills/software-craft/scripts/validate-craft-cards.py --provenance ... --pending ... {cdir} — {len(rows)} cards, 0 errors, {warn} |
| `new in this change` | {new} |
| `siblings` | plugins/code-quality/skills/reviewing-java/references/review-cards (the Java corpus on the same pattern) |

## cards

| rule_id | domain | check_kind | severity | file | lines |
|--|--|--|--|--|--|
"""
open(out,"w",encoding="utf-8").write(hdr+"\n".join(rows)+"\n")
print(len(rows),"rows ->",out)

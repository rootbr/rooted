// Triage of the harvested Python catalog items for the Python language corpus — one judge per batch.
// Authoring time only; never part of a build or a review run.
//
// Each batch brief is a file scripts/python-corpus.py prepared: the batch's items (summary and the
// head of the explanation), the universal card ids and titles, the topic list and the exclusion
// criteria. The judge reads it in one call, gives one verdict per item through the schema, and
// writes the same verdicts to <state_dir>/triage/<batch>.json as its restart record; the prepare
// script's merge step joins the batch files by rule_key into candidates.json.
//
// Invocation: Workflow({ scriptPath: "<skill>/scripts/python-triage-workflow.js", args: {
//   state_dir, batches: [ { id, brief_path, item_count } ], done: [ batch ids whose file exists ],
//   concurrency: 3                      // batches judged at once; the rest wait in waves
// }})
export const meta = {
  name: 'python-triage-workflow',
  description: 'Triage the harvested Python catalog items into corpus candidates, one judge per batch',
  phases: [{ title: 'Triage', detail: 'one brief-judge per batch of items' }],
}

const A = args || {}
if (!A.state_dir || !Array.isArray(A.batches)) throw new Error('python-triage-workflow: args.state_dir and args.batches are required')
const DONE = new Set(A.done || [])
const MODEL = 'claude-opus-5-5'

const VERDICT = {
  type: 'object', additionalProperties: false,
  properties: {
    verdicts: { type: 'array', items: { type: 'object', additionalProperties: false,
      properties: {
        code: { type: 'string', description: 'the item code as the brief lists it (B006, W0102, S5717, B602)' },
        source: { type: 'string', enum: ['ruff', 'pylint', 'sonar', 'bandit', 'bugbear'] },
        verdict: { type: 'string', enum: ['python-specific-new', 'universal-instance', 'formatting', 'not-checkable', 'not-a-craft-rule', 'out-of-scope', 'duplicate-of'] },
        universal_id: { type: 'string', description: 'for universal-instance: the universal card id (CODE-12); else empty' },
        duplicate_of: { type: 'string', description: 'for duplicate-of: the code of the item in this batch that states the same check; else empty' },
        topic: { type: 'string', description: 'for python-specific-new: the topic slug from the list; else empty' },
        rule_key: { type: 'string', description: 'for python-specific-new: a kebab-case name of the defect, the same for every catalog entry of one check (mutable-default-argument, bare-except, open-without-with); else empty' },
        statement: { type: 'string', description: 'for python-specific-new: the rule in one declarative sentence in the programmer\'s vocabulary, with the Python fact that makes it hold; else empty' },
        note: { type: 'string', description: 'one clause: the reason for the verdict' },
      },
      required: ['code', 'source', 'verdict', 'universal_id', 'duplicate_of', 'topic', 'rule_key', 'statement', 'note'] } },
    batch_note: { type: 'string', description: 'anything the brief left open: an item whose text did not load, a topic that fits no row' },
  },
  required: ['verdicts', 'batch_note'],
}

function prompt(b) {
  return `You are the triage judge of the Python language corpus of the software-craft skill. One batch of ${b.item_count} static-analysis catalog items is in the brief file below; give every item one verdict.

Read the brief with one Bash call (cat ${b.brief_path}; it is about 150 KB, which the Read tool would split over several calls). It holds, in this order: the four criteria a corpus card must meet and the verdict definitions; the topic list with what each topic owns; the universal cards already shipped (id and title); the batch's items with code, source, name, title, summary and the head of the explanation. Work from the brief alone — no other file, no network; the explanation head is enough to decide, and the spine judge of each topic later reads the full texts.

Verdict per item, one of:
- python-specific-new — a craft rule that holds because of Python (its data model, scoping, exception model, typing, standard library, packaging or tooling) and that no universal card states; fill topic, rule_key and statement. Several items that check one defect (a Ruff rule and the Pylint message it reimplements, a Sonar rule on the same construct) share one rule_key, so spell the key from the defect, not from the tool's name.
- universal-instance — a universal card already states the rule for every language, and the item is Python's instance of it; fill universal_id with that card's id.
- formatting — layout, whitespace, quoting, import order, naming style, docstring style.
- not-checkable — a principle with no form a finder can check on a diff hunk.
- not-a-craft-rule — a plain error the interpreter or every linter reports (a syntax error, an undefined name, a wrong argument count to a builtin, an unreachable code path), a type-checker error, or a rule about the tool's own directives (noqa, type: ignore), rather than a way of writing code.
- out-of-scope — framework-specific (Django, pandas, numpy, FastAPI, Airflow, pytest-asyncio internals), concurrency correctness beyond plain idioms, security-critical design beyond ordinary-code hygiene, low-latency tuning, ML or algorithm research.
- duplicate-of — another item of this batch states the same check; fill duplicate_of with that item's code (judge the first occurrence on its merits; mark the later ones duplicate-of it).
A rule the universal corpus states only in part — the universal card gives the principle, Python adds a mechanism the card does not name (a dunder, a context manager, a scoping rule) — is python-specific-new, and its statement names what Python adds; say in note which universal id it extends.

Verdict statistics from the design: roughly a third of the items survive as python-specific-new; a batch far from that is worth a second look, not a forced fit.
Write the result file before you return: ${A.state_dir}/triage/${b.id}.json holding exactly the object you return (one python3 heredoc; mkdir -p the directory; overwrite an existing file). Then return the object via the structured-output tool, once. Write nothing else anywhere. Budget: about 4 tool calls in all — one read, one write, the return.`
}

phase('Triage')
const CONCURRENCY = Number.isInteger(A.concurrency) && A.concurrency > 0 ? A.concurrency : 3
const todo = A.batches.filter(b => !DONE.has(b.id))
log(`Triage: ${A.batches.length} batch(es), ${A.batches.length - todo.length} done on disk, ${todo.length} to run, ${CONCURRENCY} at a time`)
const results = []
for (let i = 0; i < todo.length; i += CONCURRENCY) {
  const wave = todo.slice(i, i + CONCURRENCY)
  results.push(...await parallel(wave.map(b => () =>
    agent(prompt(b), { label: `triage:${b.id}`, phase: 'Triage', schema: VERDICT, model: MODEL, effort: 'xhigh', agentType: 'brief-judge' })
      .then(r => ({ id: b.id, result: r })))))
}
const ran = results.filter(Boolean)
const failed = todo.filter(b => !ran.some(r => r.id === b.id && r.result))
if (failed.length) log(`WARNING: ${failed.length} batch(es) returned nothing: ${failed.map(b => b.id).join(', ')} — re-run the workflow; the done list skips the finished ones`)
const counts = {}
for (const r of ran) for (const v of (r.result && r.result.verdicts) || []) counts[v.verdict] = (counts[v.verdict] || 0) + 1
log(`Triage verdicts this run: ${Object.entries(counts).map(([k, n]) => `${k} ${n}`).join(', ') || 'none'}`)
return { batches: ran.map(r => ({ id: r.id, verdicts: r.result.verdicts, batch_note: r.result.batch_note })), failed: failed.map(b => b.id), counts }

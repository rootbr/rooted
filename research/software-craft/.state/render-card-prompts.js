// Render the four card-agent prompts of research-topic-workflow.js with named placeholders into one Markdown file, the audit target for a prompt change.
// Usage: ARGS=<json with root and a placeholder topic> node render-card-prompts.js <research-topic-workflow.js> <out.md>; then make-inventory.py --target-type agent-prompt --tier warm.
const fs = require('fs'); const path = process.argv[2]
let src = fs.readFileSync(path, 'utf8')
const start = src.indexOf('// ---- args'); const end = src.indexOf('// ---- Phase Sources')
let body = src.slice(start, end).replace(/^let A = args[\s\S]*?const T = A\.topic/m, "let A = JSON.parse(process.env.ARGS)\nconst T = A.topic")
const cp = src.slice(src.indexOf('function closingPrompt'), src.indexOf('// ---- Phases Draft, Verify, Fix'))
const stub = ['parallel','pipeline','phase','log','agent'].map(f => `const ${f} = () => {}`).join('\n')
eval(stub + '\n' + body + '\n' + cp + `
const r = { key: '<rule-key>', rule_id: '<PREFIX-NN>', title: '<rule title>', statement: '<rule statement>', formulation: ['<formulation locator>'], contested: false, positions: [], separating_condition: '', evidence: [{fetch_status:'fetched', admissible_class:'documentation', source:'<citation>', locator:'<locator>', url:'<url>', quote:'<quoted fragment>'}], step:['implement'], applies_to:['universal'], triggers:['<pattern>'], scope:'hunk', check_kind:'mechanical', severity_default:'minor', example_language:'<language>' }
const d = { filename: '<prefix>-NN--<slug>.md', card_markdown: '<the draft card>', provenance_line: '<the provenance line>' }
const v = { verdict: 'revise', note: '<note>', problems: [{kind:'<kind>', detail:'<detail>', required_edit:'<edit>'}], evidence_checked: [] }
const out = ['# Card-agent prompts of research-topic-workflow.js', '', 'Rendered with named placeholders; one section per agent role.', '',
  '## Drafter', '', draftPrompt(r), '', '## Skeptic (first and second verdict)', '', verifyPrompt(r, d, 'skeptic'), '', '## Fix', '', fixPrompt(r, d, v), '', '## Closing edit (the fix prompt with this opening)', '', closingPrompt(r, d, v).split('\\n')[0]]
fs.writeFileSync(process.argv[3], out.join('\\n') + '\\n')
console.log('written', process.argv[3])
`)

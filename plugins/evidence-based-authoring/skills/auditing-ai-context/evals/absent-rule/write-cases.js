export const meta = {
  name: 'absent-rule-write-cases',
  description: 'Write the test cases of the absent-rule experiment and have each one\'s labels checked by a second reader',
  phases: [
    { title: 'Write', detail: 'one writer per drawn domain, by case-brief.md' },
    { title: 'Check', detail: 'one checker per case, by label-check-brief.md, blind to the classes' },
  ],
}

// Invoke: Workflow({ scriptPath: "<this file>", args: {
//   briefPath, checkBriefPath,                       // absolute paths of the two briefs
//   cases: [ { name, domain, dir } ],                // dir: absolute path of the case directory
//   writerType: "brief-worker", checkerType: "brief-judge"   // optional; omit to use the default agent
// }})
// The script reads no file: the writer returns its planted sentences without their classes, and the
// checker receives them in its prompt.

const input = typeof args === 'string' ? JSON.parse(args) : args
if (!input || !Array.isArray(input.cases) || !input.briefPath || !input.checkBriefPath)
  throw new Error('write-cases: args need briefPath, checkBriefPath and cases[]')

const PLANTED_SCHEMA = {
  type: 'object',
  properties: {
    topic: { type: 'string' },
    old_rule: { type: 'string' },
    new_rule: { type: 'string' },
    validate_exit: { type: 'integer', description: 'exit status of the last run of the validate command' },
    planted: {
      type: 'array',
      items: {
        type: 'object',
        properties: { id: { type: 'string' }, text: { type: 'string' } },
        required: ['id', 'text'],
      },
    },
  },
  required: ['topic', 'old_rule', 'new_rule', 'validate_exit', 'planted'],
}

const CHECK_SCHEMA = {
  type: 'object',
  properties: {
    classes: { type: 'object', description: 'planted id -> {class, licence?, reason}' },
    presents_old_rule: { type: 'boolean' },
    presenting_sentence: { type: 'string' },
  },
  required: ['classes', 'presents_old_rule'],
}

const missingTypes = new Set()
async function dispatch(prompt, opts, agentType) {
  if (!agentType || missingTypes.has(agentType)) return agent(prompt, opts)
  try {
    return await agent(prompt, { ...opts, agentType })
  } catch (error) {
    if (!/not found/i.test(String(error && error.message))) throw error
    missingTypes.add(agentType)
    log(`agent type ${agentType} is not registered here; its steps run on the default agent`)
    return agent(prompt, opts)
  }
}

const writerPrompt = c => `Write one test case.

Read the brief at ${input.briefPath} and follow it exactly. Read nothing else in the repository.
Domain: ${c.domain}
Case directory: ${c.dir} (create it; write old.md, new.md and labels.json there and nowhere else)

Return the topic, rule A as old_rule, rule B as new_rule, the exit status of your last run of the validate command, and the ten planted sentences as id and text, word for word as in labels.json — without their classes.`

const checkerPrompt = (c, written) => `Check the labels of one test case.

Read the brief at ${input.checkBriefPath} and follow it exactly.
Case directory: ${c.dir}
The ten planted sentences:
${written.planted.map(p => `${p.id}: ${JSON.stringify(p.text)}`).join('\n')}

Write labels-check.json into the case directory as the brief says, and return the same object.`

const results = await pipeline(
  input.cases,
  c => dispatch(writerPrompt(c),
    { label: `write:${c.name}`, phase: 'Write', schema: PLANTED_SCHEMA, model: 'opus', effort: 'high' },
    input.writerType),
  (written, c) => dispatch(checkerPrompt(c, written),
    { label: `check:${c.name}`, phase: 'Check', schema: CHECK_SCHEMA, model: 'opus', effort: 'xhigh' },
    input.checkerType)
    .then(check => ({ name: c.name, domain: c.domain, written, check })),
)

const done = results.filter(Boolean)
if (done.length < input.cases.length)
  log(`${input.cases.length - done.length} case(s) returned nothing and need a rerun`)
return { cases: done, missing: input.cases.filter(c => !done.some(d => d.name === c.name)).map(c => c.name) }

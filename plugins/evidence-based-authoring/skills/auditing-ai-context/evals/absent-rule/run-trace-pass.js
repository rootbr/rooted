export const meta = {
  name: 'absent-rule-trace-pass',
  description: 'Dispatch the independent reviewers of the trace pass over the test cases: three readings of each list',
  phases: [
    { title: 'Readings', detail: 'independent reviewers give a verdict on every listed sentence' },
  ],
}

// Invoke: Workflow({ scriptPath: "<this file>", args: {
//   instructionsPath,                  // absolute path of agents/trace-reviewer.md
//   cases: [ { name, list, document } ],   // absolute paths
//   readings: 3,
//   model: "sonnet", effort: "medium",
//   agentType: "brief-worker"          // optional: a type that starts without the session's instruction files
// }})
// The script reads no file: every reviewer opens its instruction file, the list and the document
// itself, and returns its verdicts; the session writes them down and runs scripts/check_trace.py.

const input = typeof args === 'string' ? JSON.parse(args) : args
if (!input || !input.instructionsPath || !Array.isArray(input.cases))
  throw new Error('run-trace-pass: args need instructionsPath and cases[]')

const MODEL = input.model || 'sonnet'
const EFFORT = input.effort || 'medium'
const BRIEF = `Open ${input.instructionsPath} with Read. The text after its front matter is your instruction for this task: follow it exactly. The dispatch message it speaks of is this message.`

const VERDICTS_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          target: { type: 'string' },
          verdict: { type: 'string', enum: ['rewrite', 'licensed', 'plain'] },
          quote: { type: 'string' },
          question: { type: 'string' },
          reason: { type: 'string' },
        },
        required: ['id', 'target', 'verdict', 'reason'],
      },
    },
  },
  required: ['file', 'verdicts'],
}

const missingTypes = new Set()
async function dispatch(prompt, opts) {
  const type = input.agentType
  if (!type || missingTypes.has(type)) return agent(prompt, opts)
  try {
    return await agent(prompt, { ...opts, agentType: type })
  } catch (error) {
    if (!/not found/i.test(String(error && error.message))) throw error
    missingTypes.add(type)
    log(`agent type ${type} is not registered here; the reviewers run on the default agent`)
    return agent(prompt, opts)
  }
}

phase('Readings')
const rounds = Number.isInteger(input.readings) && input.readings > 0 ? input.readings : 3
const jobs = input.cases.flatMap(c => Array.from({ length: rounds }, (_, k) => ({ c, reading: k + 1 })))
const read = await parallel(jobs.map(job => () =>
  dispatch(`${BRIEF}\n\nThe list file: ${job.c.list}\nThe document: ${job.c.document}`,
    { label: `review:${job.c.name}:r${job.reading}`, phase: 'Readings', schema: VERDICTS_SCHEMA, model: MODEL, effort: EFFORT })
    .then(r => r && ({ name: job.c.name, reading: job.reading, verdicts: r.verdicts }))))
const done = read.filter(Boolean)
return {
  readings: done,
  missing: jobs.filter(job => !done.some(d => d.name === job.c.name && d.reading === job.reading))
    .map(job => `${job.c.name}:r${job.reading}`),
}

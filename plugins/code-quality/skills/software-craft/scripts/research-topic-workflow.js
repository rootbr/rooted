// Research orchestration for the software-craft skill — one topic in, the material of its cards out.
//
// Phase Sources : three agents in parallel, one per layer of the research protocol — formulation
//                 (what the canon says), reception (what the industry says), evidence (the research,
//                 standard, documentation or hands-on test that backs each candidate rule) — each
//                 returning locators, quotes and a fetch status through a schema.
// Phase Spine   : one agent merges the three layers into the candidate rules in source order, each
//                 with its formulation locator, its reception (contested or not, by whom), its evidence
//                 anchor or the search that found none, its checkability on a diff and its facets.
// Phase Draft   : one agent per candidate rule writes the card, its provenance line and, where the
//                 rule cannot ship, its pending entry.
// Phase Verify  : one skeptic per draft checks entailment of the Thesis by the evidence, self-
//                 containment, the Example's compilability in its language, the triggers' sanity and
//                 the separating condition of a contested rule, and returns a verdict with the edits
//                 it requires.
// Phase Fix     : the drafter applies the verdict once; a draft rejected twice goes to pending.
//
// The workflow writes no files. It returns the research note's material (sources, spine, outcomes),
// the cards, the provenance lines and the pending entries; scripts/write-topic-result.py writes them
// into the tree, and the orchestrator runs the validator and the audit and commits.
//
// Invocation (the Workflow tool; args is a JSON object, never a JSON string):
//   Workflow({ scriptPath: "<skill-dir>/scripts/research-topic-workflow.js", args: {
//     root: "<absolute repository root>",
//     topic: { slug, title, group, domain, prefix, locators, candidate_evidence: [..], contested: bool, notes },
//     next_id: 1,                         // the next free NN in the domain; ids are provisional until written
//     existing_titles: [ "..." ],         // titles of the cards already shipped, so no rule is carded twice
//     max_rules: 12,                      // cap on candidate rules drafted; the rest is logged and held
//     rotation_start: 0                   // index into the example-language rotation for this topic
//   }})
// Every agent runs on claude-opus-5-5: xhigh for the source, spine and draft agents, max for the skeptic.

export const meta = {
  name: 'research-craft-topic',
  description: 'Research one software-craft topic: three source layers in parallel, a spine of candidate rules, one drafter and one skeptic per rule, one fix round',
  phases: [
    { title: 'Sources', detail: 'formulation, reception and evidence agents in parallel', model: 'claude-opus-5-5' },
    { title: 'Spine', detail: 'one agent merges the layers into candidate rules with evidence anchors', model: 'claude-opus-5-5' },
    { title: 'Draft', detail: 'one drafter per candidate rule: the card, its provenance line, its pending entry', model: 'claude-opus-5-5' },
    { title: 'Verify', detail: 'one skeptic per draft: entailment, self-containment, example, triggers, separating condition', model: 'claude-opus-5-5' },
    { title: 'Fix', detail: 'the drafter applies the verdict once; a second rejection sends the rule to pending', model: 'claude-opus-5-5' },
  ],
}

// ---- args ---------------------------------------------------------------------------------
let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { /* validated below */ } }
if (!A || typeof A !== 'object') throw new Error('research-topic-workflow: args must be an object { root, topic, next_id, existing_titles?, max_rules?, rotation_start? }')
const T = A.topic
for (const k of ['slug', 'title', 'group', 'domain', 'prefix']) {
  if (!T || typeof T[k] !== 'string' || !T[k]) throw new Error(`research-topic-workflow: topic.${k} is required`)
}
const ROOT = A.root
if (typeof ROOT !== 'string' || !ROOT.startsWith('/')) throw new Error('research-topic-workflow: root must be the absolute repository root')
if (!Number.isInteger(A.next_id) || A.next_id < 1) throw new Error('research-topic-workflow: next_id must be a positive integer')
const NEXT_ID = A.next_id
const EXISTING = Array.isArray(A.existing_titles) ? A.existing_titles : []
const MAX_RULES = Number.isInteger(A.max_rules) && A.max_rules > 0 ? A.max_rules : 12
const ROT = Number.isInteger(A.rotation_start) ? A.rotation_start : 0
const LOCATORS = typeof T.locators === 'string' ? T.locators : ''
const CANDIDATE_EVIDENCE = Array.isArray(T.candidate_evidence) ? T.candidate_evidence : []
const CONTESTED = T.contested === true
const NOTES = typeof T.notes === 'string' ? T.notes : ''

const MODEL = 'claude-opus-5-5'
const EFFORT = { source: 'xhigh', spine: 'xhigh', draft: 'xhigh', skeptic: 'max' }
const LANGS = ['java', 'python', 'typescript', 'go', 'rust']
const STEPS = ['design', 'implement', 'handle-errors', 'test', 'refactor', 'document', 'review']
const APPLIES_TO = ['universal', 'object-oriented', 'functional', 'public-api', 'service-boundary', 'library',
  'exceptions', 'result-types', 'garbage-collected', 'manual-memory', 'static-types', 'dynamic-types',
  'tests', 'build-config', 'prose']
const SIGNALS = ['long_routine', 'deep_nesting', 'many_parameters', 'boolean_argument', 'empty_handler',
  'magic_number', 'commented_out_code', 'todo_marker', 'duplicate_block', 'test_file', 'added_file']
const SKILL = `${ROOT}/plugins/code-quality/skills/software-craft`
const TAXONOMY = `${SKILL}/references/craft-cards-taxonomy.md`
const DESIGN = `${ROOT}/research/2026-09-26_software-craft-cards.md`

// ---- channel policy and source map (the environment's egress policy) ---------------------------
const CHANNELS = `Fetch channel — the authoring environment's egress policy admits three hosts and denies the rest; never retry a denied host, never disable TLS checks:
- Reachable: raw.githubusercontent.com (any public GitHub file: \`curl -sS -A Mozilla https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>\`; the branch is main or master; a 404 means a wrong path, so try the other branch and the repository's known layout), pkg.go.dev (Go package documentation), pypi.org (package pages). A github.com HTML page answers 403: use the raw form.
- Denied: arxiv.org, doi.org, dl.acm.org, ieeexplore.ieee.org, link.springer.com, every publisher, author and university site, the vendors' documentation sites (docs.oracle.com, docs.python.org, eslint.org, rules.sonarsource.com, pmd.github.io, checkstyle.org, rust-lang.org, go.dev, typescriptlang.org, readthedocs), cwe.mitre.org, cheatsheetseries.owasp.org, wiki.sei.cmu.edu, rfc-editor.org, unicode.org, aws.amazon.com, computer.org, abseil.io, refactoring.com, martinfowler.com, blog.cleancoder.com, news.ycombinator.com, lobste.rs, wikipedia.org, scholar.google.com.
- The WebSearch tool works (load it through ToolSearch when it is not in your tool list). Its result snippets and summaries are the only access to papers, threads and vendor pages: a statement you take from them is relayed, and you quote the relayed text verbatim with the URL the result names.
Fetch status, one per citation: fetched — you opened the text from this environment with curl and quote it; relayed — a WebSearch snippet or summary states the claim and you quote that snippet; unfetched — neither, so you cite from memory, mark it, and never let it be a card's only anchor.`

const SOURCE_MAP = `Where openable sources live (raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>):
- Static-analysis rule documentation (an admissible source class: documentation of a check tools run in practice): ESLint — eslint/eslint main docs/src/rules/<rule>.md; typescript-eslint — typescript-eslint/typescript-eslint main packages/eslint-plugin/docs/rules/<rule>.mdx; Error Prone — google/error-prone master docs/bugpattern/<Name>.md; PMD — pmd/pmd main pmd-java/src/main/resources/category/java/{bestpractices,codestyle,design,documentation,errorprone,performance,security}.xml (rule descriptions and default properties inside the XML); Checkstyle — checkstyle/checkstyle master src/site/xdoc/checks/<category>/<check>.xml, lower case (sizes/methodlength.xml, sizes/parameternumber.xml, coding/magicnumber.xml, metrics/cyclomaticcomplexity.xml, naming/methodname.xml, blocks/emptycatchblock.xml); Pylint — pylint-dev/pylint main pylint/checkers/<checker>.py (message texts) and doc/data/messages/<first letter>/<message-name>/{bad.py,good.py}; Ruff — astral-sh/ruff main crates/ruff_linter/src/rules/<plugin>/rules/<rule>.rs (the doc comment is the rule page); clippy — rust-lang/rust-clippy master clippy_lints/src/<lint>.rs or <group>/mod.rs (doc comments) and book/src/lint_configuration.md (defaults); go vet — golang/tools master go/analysis/passes/<pass>/doc.go, golang/go master src/cmd/vet/doc.go, or pkg.go.dev/golang.org/x/tools/go/analysis/passes/<pass>; SpotBugs — spotbugs/spotbugs master spotbugs/etc/messages.xml; Semgrep — semgrep/semgrep-rules develop <language>/<path>.yaml; SonarSource (the RSPEC rule text ships in each language plugin) — SonarSource/sonar-python master python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S<n>.html and S<n>.json, SonarSource/sonar-go master sonar-go-plugin/src/main/resources/org/sonar/l10n/go/rules/go/S<n>.html, SonarSource/sonar-java master java-checks/src/main/resources/org/sonar/l10n/java/rules/java/S<n>.html.
- Official documentation with GitHub sources (an admissible class): python/cpython main Doc/<section>/<page>.rst; python/peps main peps/pep-NNNN.rst; golang/go master doc/go_spec.html and src/<pkg>/*.go doc comments; golang/website master _content/doc/effective_go.html and _content/doc/faq.md; rust-lang/book main src/chNN-NN-*.md; rust-lang/reference master src/*.md; rust-lang/api-guidelines master src/*.md; rust-lang/rust master library/{core,std}/src/**; microsoft/TypeScript-Website v2 packages/documentation/copy/en/handbook-v2/*.md; openjdk/jdk jdk-21-ga src/java.base/share/classes/**; google/styleguide gh-pages javaguide.html, pyguide.md, tsguide.html, go/*.md; google/eng-practices master review/reviewer/*.md and review/developer/*.md; uber-go/guide master style.md.
- Standards with GitHub sources (an admissible class): OWASP/CheatSheetSeries master cheatsheets/<Name>_Cheat_Sheet.md; OWASP/ASVS master 5.0/en/0x<NN>-V<n>-<Name>.md; httpwg/http-core main (the RFC 9110–9112 sources); ietf-wg-httpapi/idempotency main; semver/semver master semver.md; eggert/tz main theory.html (the tz database's theory and practice); unicode-org/icu main docs/ and unicode-org/unicodetools main.
- Canon in openable form (formulation only, never evidence): 97-things/97-things-every-programmer-should-know master en/SUMMARY.md and en/thing_NN/README.md (CC-licensed essays); johnousterhout/aposd-vs-clean-code main README.md (the public discussion of the authors of A Philosophy of Software Design and Clean Code).
- Papers: WebSearch only. Search the exact title in quotes with the venue; read the abstract snippet; quote it. Prefer a result whose snippet carries the number the rule needs.`

const EVIDENCE_RULE = `Evidence-Based Rule of the repository: a card cites one admissible class in a form anyone can open — academic research (an arXiv id or a DOI); a technical standard or official documentation (an IEEE or ISO/IEC standard by clause, the SWEBOK Guide V4.0 by section, an RFC by section, a language specification or its official documentation, a SEI CERT rule, a CWE entry, an OWASP cheat sheet or ASVS item, a static-analysis rule page as documentation of a check tools run in practice); or verified hands-on experience in an openable form (a test under the skill's evals/fixture/, a benchmark in a public repository, a linked gist or commit). A trade book, a practitioner blog, a talk or a forum thread is never evidence: it is the formulation a rule follows and the reception it met, named in the provenance map and the research note, never inside a card. A claim taken from a source must be stated as the source states it: no inversion, no stripped precondition, no conditional flattened to an absolute, no refuted position stated as a recommendation.`

// ---- schemas --------------------------------------------------------------------------------
const CITATION_PROPS = {
  source: { type: 'string', description: 'full citation: authors, title, venue, year and identifier (arXiv id, DOI, rule id, document and section)' },
  locator: { type: 'string', description: 'the chapter, section, rule id or path that anchors the statement' },
  quote: { type: 'string', description: 'the verbatim text that states the claim; a relayed snippet verbatim; a paraphrase only when unfetched, and then marked (paraphrase)' },
  fetch_status: { type: 'string', enum: ['fetched', 'relayed', 'unfetched'] },
  url: { type: 'string', description: 'the URL opened or the result URL the search named; empty when unfetched' },
  admissible_class: { type: 'string', enum: ['research', 'standard', 'official-documentation', 'tool-rule', 'hands-on', 'formulation', 'reception'] },
}
const SOURCES = {
  type: 'object', additionalProperties: false,
  properties: {
    layer: { type: 'string', enum: ['formulation', 'reception', 'evidence'] },
    items: {
      type: 'array',
      items: { type: 'object', additionalProperties: false,
               properties: { claim: { type: 'string', description: 'the candidate rule or position this item bears on, as one sentence in the programmer\'s vocabulary' },
                             ...CITATION_PROPS,
                             contested: { type: 'boolean', description: 'true when another named source disputes this position' },
                             notes: { type: 'string', description: 'caveats: sample, language, threshold, what the source does not say' } },
               required: ['claim', 'source', 'locator', 'quote', 'fetch_status', 'url', 'admissible_class', 'contested', 'notes'] },
    },
    summary: { type: 'string', description: 'three to six sentences: what this layer found, what it could not open, where the canon disagrees' },
  },
  required: ['layer', 'items', 'summary'],
}
const RULE = {
  type: 'object', additionalProperties: false,
  properties: {
    key: { type: 'string', description: 'short kebab-case key, unique within the topic' },
    title: { type: 'string', description: 'the card title: one complete, checkable declarative claim, language-agnostic, without a colon or a question mark' },
    statement: { type: 'string', description: 'the rule in two or three sentences with its threshold, condition and qualifiers, as the evidence states them' },
    formulation: { type: 'array', items: { type: 'string' }, description: 'canon locators that formulate the rule (book and chapter, essay, discussion)' },
    contested: { type: 'boolean' },
    positions: { type: 'array', items: { type: 'object', additionalProperties: false,
                 properties: { side: { type: 'string' }, holder: { type: 'string' }, statement: { type: 'string' }, evidence: { type: 'string', description: 'the openable evidence for this side, with fetch status, or "none"' } },
                 required: ['side', 'holder', 'statement', 'evidence'] } },
    separating_condition: { type: 'string', description: 'for a contested rule, the sourced condition that separates the cases; empty when the rule is not contested or no condition was found' },
    evidence: { type: 'array', items: { type: 'object', additionalProperties: false, properties: CITATION_PROPS,
                required: ['source', 'locator', 'quote', 'fetch_status', 'url', 'admissible_class'] } },
    checkable_on_diff: { type: 'boolean', description: 'true when a finder holding the card and the diff hunks can answer one binary question' },
    disposition: { type: 'string', enum: ['card', 'pending-no-evidence', 'pending-no-separating-condition', 'held-not-checkable', 'folded'] },
    hold_reason: { type: 'string', description: 'why the rule is not carded, or the card it folds into; empty for a card' },
    searched: { type: 'string', description: 'for a held rule: what was searched and what would unblock it' },
    step: { type: 'array', items: { type: 'string', enum: STEPS } },
    applies_to: { type: 'array', items: { type: 'string', enum: APPLIES_TO } },
    triggers: { type: 'array', items: { type: 'string' }, description: 'Python re patterns against added lines in any language, or signal:<name>; [] means every diff' },
    scope: { type: 'string', enum: ['hunk', 'file', 'base-compare', 'callers'] },
    check_kind: { type: 'string', enum: ['mechanical', 'semantic'] },
    severity_default: { type: 'string', enum: ['major', 'minor', 'suggestion'] },
  },
  required: ['key', 'title', 'statement', 'formulation', 'contested', 'positions', 'separating_condition', 'evidence', 'checkable_on_diff',
             'disposition', 'hold_reason', 'searched', 'step', 'applies_to', 'triggers', 'scope', 'check_kind', 'severity_default'],
}
const SPINE = {
  type: 'object', additionalProperties: false,
  properties: {
    summary: { type: 'string', description: 'the topic in one paragraph: what the canon says, where the industry disagrees, what the evidence supports' },
    rules: { type: 'array', items: RULE },
    dropped: { type: 'array', items: { type: 'string' }, description: 'source items that yielded no rule, each with the reason' },
  },
  required: ['summary', 'rules', 'dropped'],
}
const DRAFT = {
  type: 'object', additionalProperties: false,
  properties: {
    status: { type: 'string', enum: ['card', 'pending'] },
    filename: { type: 'string', description: '<prefix lower-case>-NN--<slug>.md' },
    card_markdown: { type: 'string', description: 'the whole card file, frontmatter included; empty when pending' },
    provenance_line: { type: 'string', description: 'one Markdown list item beginning with "- **<RULE_ID>** · "; empty when pending' },
    pending_entry: { type: 'string', description: 'one Markdown list item for pending-evidence.md; empty when the card ships' },
    notes: { type: 'string', description: 'what the drafter could not confirm, or why the rule went to pending' },
  },
  required: ['status', 'filename', 'card_markdown', 'provenance_line', 'pending_entry', 'notes'],
}
const VERDICT = {
  type: 'object', additionalProperties: false,
  properties: {
    verdict: { type: 'string', enum: ['accept', 'revise', 'reject'] },
    problems: { type: 'array', items: { type: 'object', additionalProperties: false,
                properties: { kind: { type: 'string', enum: ['entailment', 'evidence-status', 'self-containment', 'example', 'trigger', 'separating-condition', 'schema', 'facet', 'wording', 'other'] },
                              detail: { type: 'string' }, required_edit: { type: 'string', description: 'the exact edit that resolves it' } },
                required: ['kind', 'detail', 'required_edit'] } },
    evidence_checked: { type: 'array', items: { type: 'object', additionalProperties: false,
                        properties: { citation: { type: 'string' }, how: { type: 'string', enum: ['fetched', 'relayed', 'unfetched'] },
                                      states_claim: { type: 'boolean' }, note: { type: 'string' } },
                        required: ['citation', 'how', 'states_claim', 'note'] } },
    note: { type: 'string' },
  },
  required: ['verdict', 'problems', 'evidence_checked', 'note'],
}

// ---- prompts --------------------------------------------------------------------------------
const NO_WRITES = 'Write nothing under the repository; scratch files, compiled snippets and downloads go under /tmp/craft-research/. Tools: Read, Grep, Glob, Bash (curl to the reachable hosts, compilers on your own snippets), WebSearch; the structured-output tool returns your result.'

function topicBlock() {
  return `Topic: ${T.title} (slug ${T.slug}; group ${T.group}; domain ${T.domain}; id prefix ${T.prefix}${CONTESTED ? '; marked CONTESTED in the design note' : ''}).
Formulation locators from the design note: ${LOCATORS || '(none: research this topic from the evidence layer)'}.
Topic notes (ownership between neighbouring topics, scope): ${NOTES || '(none)'}.
Candidate evidence to search first, from memory and unverified — titles to search, not citations to copy; drop any that does not state the claim you need:
${CANDIDATE_EVIDENCE.length ? CANDIDATE_EVIDENCE.map(c => `- ${c}`).join('\n') : '- (none listed)'}`
}

function sourcePrompt(layer) {
  const jobs = {
    formulation: `Layer: FORMULATION — what the canon says about this topic. Read the chapters and sections the locators name through openable forms where one exists (the 97 Things essays, the aposd-vs-clean-code discussion, official style guides and engineering-practice documents on GitHub); where a book is not openable from here, state from memory what the chapter formulates, as a paraphrase marked (paraphrase, unfetched) — a formulation is never evidence, so an unfetched formulation is admissible as a formulation. Also record what the authors say beyond the books — errata, later reflections, the public discussion between the authors of A Philosophy of Software Design and Clean Code (fetch it) — as relayed or fetched items. Return one item per distinct rule or position the canon formulates, in the source's order, with the chapter or section as the locator.`,
    reception: `Layer: RECEPTION — what the industry says. Use WebSearch for named practitioners' critiques and defenses of the canon's rules on this topic, the threads where they are argued (Hacker News, Lobsters, named blogs), practitioner surveys and reading lists from 2024 to 2026 as a freshness check, and the rule pages of static-analysis tools (fetch them from GitHub: they record what the industry checks mechanically, and a tool rule page is an admissible source, so mark its admissible_class tool-rule and quote its text and default threshold). Reception decides which rules are contested and shapes their Limits; it is never evidence. Mark contested=true on an item when a named source disputes the position, and say who. Return one item per position, critique, defense or tool rule.`,
    evidence: `Layer: EVIDENCE — the research, standard, documentation or hands-on test that backs each candidate rule of this topic. For each rule you expect the canon to formulate on this topic, search for the empirical software-engineering study (IEEE TSE, ICSE, FSE, EMSE, MSR, ICPC, ESEM, SANER), the standard or the documentation that states it, starting with the candidate evidence list; open what is openable (curl), relay what is not (WebSearch snippet, quoted verbatim), and record what you searched when nothing states the claim. Keep the number the source gives (a percentage, a threshold, a sample size) inside the quote. State the source's own scope and caveat in notes (language studied, participants, whether the effect was measured or hypothesized). Also include the contrary evidence where a rule is contested. Return one item per (rule, source) pair.`,
  }
  return `You are one source agent of the research workflow that builds the software-craft card corpus (language-agnostic craft rules, one checkable rule per card, an openable source per card).

${topicBlock()}

${jobs[layer]}

${EVIDENCE_RULE}

${CHANNELS}

${SOURCE_MAP}

Discipline: quote verbatim what you opened; never present a paraphrase as a quote; never upgrade a relayed or unfetched status; record a search that found nothing as an item with fetch_status unfetched, quote "(none found)", and the search terms in notes. Twenty to forty items is a normal size for a layer; fewer is fine when the topic is narrow. ${NO_WRITES}
Return the sources object via the structured-output tool.`
}

function spinePrompt(sources) {
  const text = sources.map(s => `### ${s.layer.toUpperCase()} — ${s.summary}\n` + s.items.map(i => `- [${i.fetch_status}/${i.admissible_class}${i.contested ? '/contested' : ''}] claim: ${i.claim}\n  source: ${i.source} — ${i.locator} — ${i.url}\n  quote: ${i.quote}\n  notes: ${i.notes}`).join('\n')).join('\n\n')
  return `You are the spine agent of the research workflow that builds the software-craft card corpus. Merge the three source layers below into the topic's candidate rules, in the canon's source order, so a drafter can write one card per rule.

${topicBlock()}

${EVIDENCE_RULE}

The corpus already ships cards with these titles (do not propose a rule one of them states; a rule that extends one is a new rule only if its Thesis differs):
${EXISTING.length ? EXISTING.map(t => `- ${t}`).join('\n') : '- (none yet)'}

For each candidate rule decide:
- disposition "card" when the rule has at least one evidence item that is fetched or relayed and states the claim as the rule words it, and the rule is checkable on a diff (a finder holding the card and the hunks can answer one binary question); the Thesis carries no more than the evidence states — a relayed snippet's number is the number, a fetched page's condition is the condition.
- "pending-no-evidence" when the formulation exists but no fetched or relayed item states the claim; fill searched with what was searched and what would unblock.
- "pending-no-separating-condition" when the rule is contested and no openable source gives the condition that separates the cases; fill positions with both sides and their evidence.
- "held-not-checkable" when the principle has no checkable form on a diff; state in hold_reason which candidate rule's Rationale it feeds, or that it is recorded in the research note only.
- "folded" when another candidate rule of this topic states the same concept; name it in hold_reason.
A contested rule ships as a card only with a separating condition that has its own openable evidence on each side; write that condition in separating_condition.
Facets for a card: step (the moments of the developer's work at which the rule is applied: ${STEPS.join(', ')}); applies_to (${APPLIES_TO.join(', ')} — universal stands alone); triggers (two to six Python re patterns matched against single added lines in any language — name the vocabulary of the defect across languages, escape parentheses, write a literal dot as [.] — or signal:<name> with a name from: ${SIGNALS.join(', ')}; [] only for a rule with no signature at all, which the corpus keeps to a handful); scope (hunk: decided from the added lines; file: the whole file; base-compare: the base version too; callers: usages across the repository); check_kind (mechanical: the pattern or signal is the finding once one light context question is confirmed; semantic: the finder traces something); severity_default (major: a correctness or maintainability defect the evidence ties to failures or measured cost; minor: a clarity or design cost; suggestion: style, naming, documentation).
The title is the whole claim in one declarative sentence with its threshold and qualifier, language-agnostic, without a colon or a question mark. Eight to twelve candidate rules is a normal size for a topic; a narrow topic yields fewer. Put in dropped the source items that yielded no rule, each with its reason.

<sources>
${text}
</sources>

${NO_WRITES}
Return the spine object via the structured-output tool.`
}

const EXEMPLAR = `---
title: A boolean parameter that selects between two behaviours is replaced by two routines or an enumeration
rule_id: CODE-NN
domain: code
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['signal:boolean_argument', '\\b(flag|enabled|verbose|force)\\b\\s*[:=)]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A boolean parameter that selects between two behaviours is replaced by two routines or an enumeration

## Thesis
<the rule as one checkable claim, positive, with its threshold and condition, naming no language>

## Rationale
<the mechanism and its numbers, attribution-free: why the defect costs what it costs, which property the rule restores>

## Example
\`\`\`python
bad:  def render(order, compact): ...
      render(order, True)
good: def render_compact(order): ...
      render_compact(order)
\`\`\`

## Limits
<when the pattern is correct; a documented project tolerance; the scope the rule does not reach; for a contested rule, the sourced condition that separates the cases>

## Validator
<imperatives to the finder: what to grep in the hunk, what to open at the card's scope, what to trace> Validator question: **<one binary question whose yes is the finding>?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (\`rule_id: CODE-NN\`, severity minor, \`file\`, \`symbol\`, \`code\` = <what to quote verbatim from the diff>, \`fix\` = <what the fix shows, in the file's language>, \`rationale\` = <what the rationale names>).

## Source
<compact locators of the admissible evidence with a quoted fragment each — a rule id and its documented text, an arXiv id or DOI with the relayed statement — plus any one-line caveat>`

function ruleBlock(r) {
  return `RULE ${r.rule_id} (key ${r.key}; example language ${r.example_language})
title: ${r.title}
statement: ${r.statement}
formulation: ${r.formulation.join(' | ') || '(none)'}
contested: ${r.contested}${r.contested ? `\npositions: ${JSON.stringify(r.positions)}\nseparating condition: ${r.separating_condition}` : ''}
evidence:
${r.evidence.map(e => `- [${e.fetch_status}/${e.admissible_class}] ${e.source} — ${e.locator} — ${e.url}\n  quote: ${e.quote}`).join('\n') || '- (none)'}
facets: step ${JSON.stringify(r.step)}; applies_to ${JSON.stringify(r.applies_to)}; triggers ${JSON.stringify(r.triggers)}; scope ${r.scope}; check_kind ${r.check_kind}; severity_default ${r.severity_default}`
}

function draftPrompt(r) {
  return `You are the drafter of one software-craft card. Write the card, its provenance line and — only if the rule cannot ship — its pending entry.

${topicBlock()}

${ruleBlock(r)}

Read the corpus schema at ${TAXONOMY} (frontmatter keys and order, allowed values, body blocks, trigger discipline, filename, provenance) and the design note's sections "Card schema", "Structural signals" and "Source policy" at ${DESIGN}. The card's shape, with placeholders:

${EXEMPLAR}

Rules of the card:
- Frontmatter: exactly title, rule_id, domain, step, applies_to, triggers, scope, check_kind, severity_default, in that order; lists are inline (['a', 'b'] for triggers, [design, implement] for step and applies_to); rule_id is ${r.rule_id}; domain is ${T.domain}. The title has no colon and no period at the end and equals the H1.
- Body blocks in order: Thesis, Rationale, Example, Limits, Validator, Finding output, Source; nothing between the H1 and Thesis; no other headings.
- Language-agnostic: the Thesis, Rationale, Limits and Validator name no language. The Example is one fenced block tagged ${r.example_language}, a bad: line group and a good: line group, at most ten lines in total, generic names, no diff markers; the good half compiles in a plausible enclosing scope of ${r.example_language} once each { ... } or ... elision gets a body. Check it: write the good half to /tmp/craft-research/ and compile it (javac, python3 -c compile, tsc --noEmit, gofmt or go vet, rustc --emit=metadata).
- Every threshold, condition and qualifier of the rule is in the Thesis or the Rationale, with the number the evidence gives; positive framing; at most three ALL-CAPS markers (MUST, NEVER, ALWAYS, ONLY, SHALL) in the whole card, ideally none.
- Self-contained: no sibling card id, no "the skill", "this checklist", "see above"; no author, book, blog, talk or course named anywhere in the card — not in the Source either: a trade book or a practitioner text goes to the provenance line as the formulation the rule follows.
- Faithful: the Thesis follows from the evidence as the evidence states it — no inversion, no stripped precondition, no conditional flattened to an absolute; a contested rule states the rule where the evidence holds and carries the separating condition in Limits with each side's evidence.
- Validator: imperatives to the finder — what to grep in the hunk, what to open at scope ${r.scope}, what to trace — ending in one bold binary question whose "yes" is the finding, then "Yes → flag."
- Finding output: the one sentence in the exemplar's shape, naming rule_id ${r.rule_id} and severity ${r.severity_default}.
- Source: compact locators only, each with a quoted fragment; a relayed paper is cited by its arXiv id or DOI as the search index gave it, with the relayed statement; write "(relayed)" after such a locator and "(fetched)" after one you opened; one-line caveat where the evidence's scope narrows the rule.
- Triggers: patterns compile as Python re, match the bad half of the Example on at least one line, and stay broad; test them with python3 -c "import re; ...". A signal trigger names one of: ${SIGNALS.join(', ')}.
- No dates, ticket ids or narration of how the rule changed; the card states the present rule.
- filename: ${T.prefix.toLowerCase()}-NN--<slug>.md with NN the digits of ${r.rule_id} and the slug a kebab-case of the title's central claim, at most about sixty characters.
Provenance line, one Markdown list item: "- **${r.rule_id}** · <full citation of each evidence source with its fetch status in bold where not fetched (**relayed** / **unfetched**) and the quoted statement> · topic: ${T.slug} (research/software-craft/${T.slug}.md) · formulation: <the canon locator(s) whose wording the rule follows, named here and nowhere in the card> · reception: <contested by whom, or "not contested"> · notes: <confidence high/moderate/low; the evidence's scope; what the card does not carry and why>".
Pending entry, only when the rule cannot ship (an evidence item you re-check turns out not to state the claim, or the contested rule has no sourced separating condition): "- ${T.domain} · ${T.slug} · \\"<the rule's original wording>\\" · formulation: <source> · searched: <what> · what would unblock: <what>"; for a contested rule put both positions with their formulation sources in the entry and begin it with "no separating condition ·".
Re-open the fetched evidence (curl) and re-run the search for a relayed one before you write; if the source does not state the claim, set status pending and say so in notes.

${CHANNELS}

${NO_WRITES}
Return the draft object via the structured-output tool.`
}

function verifyPrompt(r, d) {
  return `You are the skeptic of one software-craft card draft. Try to reject it. Accept only what you verified yourself; a problem you cannot demonstrate is not a problem, and a card that survives your checks is a real result.

${topicBlock()}

${ruleBlock(r)}

<draft filename="${d.filename}">
${d.card_markdown}
</draft>
<provenance_line>
${d.provenance_line}
</provenance_line>

Run these checks and record each:
1. Entailment — for every citation in the Source and the provenance line, open it yourself: curl the fetched ones (raw.githubusercontent.com, pkg.go.dev, pypi.org; a github.com page answers 403, use the raw form); re-run WebSearch for a relayed paper and read the snippet. Does the anchored text state the Thesis as the card words it — same threshold, same precondition, same direction, no refuted position stated as a recommendation? A citation that does not state the claim, or a fetched claim that turns out to be from memory, is an entailment problem. Fill evidence_checked per citation.
2. Evidence status — is every status honest (fetched only when you can open it, relayed only when a search snippet states it)? Is at least one evidence item fetched or relayed? A card whose only anchor is a trade book, a blog or an unfetched memory fails.
3. Self-containment — grep the card for a sibling rule id (${T.prefix}-NN other than ${r.rule_id}, or any other prefix-NN), for "the skill", "this checklist", "see above", and for an author, book, blog, talk or course name (McConnell, Code Complete, Pragmatic Programmer, Hunt, Thomas, Clean Code, Martin, Uncle Bob, Ousterhout, Philosophy of Software Design, Feathers, Legacy Code, Kernighan, Pike, Practice of Programming, Software Engineering at Google, Winters, Manshreck, Tidy First, Beck, Fowler, Refactoring the book, Seemann, Code That Fits, 97 Things, Bloch, Effective Java, Evans, Domain-Driven Design, Hacker News, Lobsters, Medium, Stack Overflow); none may appear.
4. Schema — frontmatter keys exactly title, rule_id, domain, step, applies_to, triggers, scope, check_kind, severity_default in that order; rule_id ${r.rule_id}; domain ${T.domain}; step values from ${STEPS.join(', ')}; applies_to values from ${APPLIES_TO.join(', ')}; blocks Thesis, Rationale, Example, Limits, Validator, Finding output, Source in order; H1 equals the title; the title has no colon and no trailing period; the Finding output names rule_id ${r.rule_id}; exactly one bold question ending in "?" in the Validator; at most three ALL-CAPS markers.
5. Example — one fenced block tagged ${r.example_language}, bad: and good: groups, at most ten lines; compile the good half yourself in /tmp/craft-research/ with a plausible enclosing scope (javac / python3 -c compile / tsc --noEmit / go vet or gofmt / rustc --emit=metadata) and report the command; a good half that does not compile is an example problem.
6. Triggers — each pattern compiles as Python re (python3 -c "import re; re.compile(...)"), matches at least one line of the bad half of the Example, is not a Java-only or Python-only spelling when the rule is universal, and is not so broad that it matches every line of any diff (a bare \\w+ or a single common keyword); a signal trigger names one of ${SIGNALS.join(', ')}. A card with [] triggers must state a reason in its Limits or Validator why no signature exists.
7. Separating condition — for a contested rule: the Limits state the condition that separates the cases, and each side has openable evidence in the Source or the provenance line; a contested rule that picks one side without the condition is rejected.
8. Language-agnostic wording — the Thesis, Rationale, Limits and Validator name no language; a rule that only holds in one language belongs to another corpus and is rejected.
9. Present design — no dates, ticket ids, "previously", "instead of", "now" contrasts; the card states the rule as it is.
Verdict: accept when every check passes; revise when the problems have exact edits that keep the rule; reject when the rule itself fails (no entailed evidence, not checkable, not language-agnostic, contested without a condition). Each problem carries the exact edit that resolves it.

${CHANNELS}

${NO_WRITES}
Return the verdict object via the structured-output tool.`
}

function fixPrompt(r, d, v) {
  return `You are the drafter of one software-craft card, applying a skeptic's verdict once. Make every required edit exactly; change nothing the verdict did not name unless the edit forces it; keep the rule's claim within what the evidence states. If a problem cannot be resolved without evidence you do not have, set status pending with a pending entry that records the wording, the formulation source, what was searched and what would unblock.

${topicBlock()}

${ruleBlock(r)}

<draft filename="${d.filename}">
${d.card_markdown}
</draft>
<provenance_line>
${d.provenance_line}
</provenance_line>
<verdict>
verdict: ${v.verdict}
note: ${v.note}
problems:
${(v.problems || []).map(p => `- [${p.kind}] ${p.detail}\n  required edit: ${p.required_edit}`).join('\n') || '- (none listed)'}
evidence checked:
${(v.evidence_checked || []).map(e => `- ${e.citation} — ${e.how} — states the claim: ${e.states_claim} — ${e.note}`).join('\n') || '- (none listed)'}
</verdict>

The card's rules are unchanged: the schema at ${TAXONOMY}; frontmatter keys in order; rule_id ${r.rule_id}; example fenced as ${r.example_language}, at most ten lines, its good half compiled by you; self-contained and attribution-free; Source locators with quoted fragments and their fetch status; the provenance line and the pending entry in the shapes below.
Provenance line: "- **${r.rule_id}** · <citations with fetch status and quoted statements> · topic: ${T.slug} (research/software-craft/${T.slug}.md) · formulation: <canon locator(s)> · reception: <contested by whom, or not contested> · notes: <confidence; scope; what the card does not carry>".
Pending entry: "- ${T.domain} · ${T.slug} · \\"<original wording>\\" · formulation: <source> · searched: <what> · what would unblock: <what>" (a contested rule without a condition begins with "no separating condition ·" and lists both positions).

${CHANNELS}

${NO_WRITES}
Return the draft object via the structured-output tool.`
}

// ---- Phase Sources ----------------------------------------------------------------------------
phase('Sources')
const LAYERS = ['formulation', 'reception', 'evidence']
const sources = (await parallel(LAYERS.map(l => () =>
  agent(sourcePrompt(l), { label: `sources:${l}`, phase: 'Sources', schema: SOURCES, model: MODEL, effort: EFFORT.source })
    .then(s => s ? { ...s, layer: s.layer || l } : null)))).filter(Boolean)
if (sources.length === 0) throw new Error('research-topic-workflow: every source agent returned nothing')
if (sources.length < LAYERS.length) log(`WARNING: ${LAYERS.length - sources.length} source layer(s) returned nothing; the spine works from ${sources.map(s => s.layer).join(', ')}`)
log(`Sources: ${sources.map(s => `${s.layer} ${s.items.length} item(s)`).join(', ')}`)

// ---- Phase Spine ------------------------------------------------------------------------------
phase('Spine')
const spine = await agent(spinePrompt(sources), { label: 'spine', phase: 'Spine', schema: SPINE, model: MODEL, effort: EFFORT.spine })
if (!spine || !Array.isArray(spine.rules)) throw new Error('research-topic-workflow: the spine agent returned no rules')
const allRules = spine.rules
const cardRules = allRules.filter(r => r.disposition === 'card')
const held = allRules.filter(r => r.disposition !== 'card')
if (cardRules.length > MAX_RULES) {
  log(`WARNING: ${cardRules.length} candidate cards exceed max_rules ${MAX_RULES}; the last ${cardRules.length - MAX_RULES} are held as "held-cap" and listed in the result`)
  for (const r of cardRules.slice(MAX_RULES)) { r.disposition = 'held-cap'; r.hold_reason = `beyond max_rules ${MAX_RULES}; re-run the topic with a higher cap or a later next_id`; held.push(r) }
}
const drafted = cardRules.slice(0, MAX_RULES)
drafted.forEach((r, i) => {
  r.rule_id = `${T.prefix}-${String(NEXT_ID + i).padStart(2, '0')}`
  r.example_language = LANGS[(ROT + i) % LANGS.length]
})
log(`Spine: ${allRules.length} candidate rule(s) — ${drafted.length} to draft, ${held.length} held (${held.map(r => r.disposition).join(', ') || 'none'})`)

// ---- Phases Draft, Verify, Fix — one pipeline per rule, no barrier ----------------------------------
const summarize = v => v ? `${v.verdict}: ${(v.problems || []).map(p => `[${p.kind}] ${p.detail}`).join('; ') || v.note}` : 'no verdict returned'
const opts = (label, ph, schema, effort) => ({ label, phase: ph, schema, model: MODEL, effort })
const outcomes = await pipeline(drafted,
  r => agent(draftPrompt(r), opts(`draft:${r.key}`, 'Draft', DRAFT, EFFORT.draft)).then(d => ({ rule: r, draft: d })),
  s => {
    if (!s || !s.draft) return { rule: s ? s.rule : null, final: 'pending', reason: 'the drafter returned nothing' }
    if (s.draft.status !== 'card') return { ...s, final: 'pending', reason: s.draft.notes || 'the drafter sent the rule to pending' }
    return agent(verifyPrompt(s.rule, s.draft), opts(`verify:${s.rule.key}`, 'Verify', VERDICT, EFFORT.skeptic)).then(v => ({ ...s, verdict: v }))
  },
  s => {
    if (!s || s.final) return s
    if (!s.verdict) return { ...s, final: 'pending', reason: 'the skeptic returned no verdict' }
    if (s.verdict.verdict === 'accept') return { ...s, final: 'card' }
    return agent(fixPrompt(s.rule, s.draft, s.verdict), opts(`fix:${s.rule.key}`, 'Fix', DRAFT, EFFORT.draft))
      .then(d2 => ({ ...s, draft1: s.draft, verdict1: s.verdict, draft: d2 }))
  },
  s => {
    if (!s || s.final) return s
    if (!s.draft) return { ...s, final: 'pending', reason: `the fix returned nothing after ${summarize(s.verdict1)}` }
    if (s.draft.status !== 'card') return { ...s, final: 'pending', reason: s.draft.notes || 'the fix sent the rule to pending' }
    return agent(verifyPrompt(s.rule, s.draft), opts(`verify2:${s.rule.key}`, 'Verify', VERDICT, EFFORT.skeptic))
      .then(v => ({ ...s, verdict: v, final: v && v.verdict === 'accept' ? 'card' : 'pending',
                    reason: v && v.verdict === 'accept' ? '' : `rejected twice — ${summarize(v)}` }))
  },
)

// ---- assemble the result --------------------------------------------------------------------------
const cards = [], provenanceLines = [], pendingEntries = [], results = []
for (const s of outcomes.filter(Boolean)) {
  if (!s.rule) continue
  const r = s.rule
  const entry = { key: r.key, rule_id: r.rule_id, title: r.title, final: s.final, reason: s.reason || '',
                  verdict1: s.verdict1 ? summarize(s.verdict1) : (s.verdict ? summarize(s.verdict) : ''),
                  verdict2: s.verdict1 && s.verdict ? summarize(s.verdict) : '' }
  results.push(entry)
  if (s.final === 'card' && s.draft && s.draft.card_markdown) {
    cards.push({ rule_id: r.rule_id, key: r.key, title: r.title, filename: s.draft.filename, example_language: r.example_language, markdown: s.draft.card_markdown })
    provenanceLines.push(s.draft.provenance_line)
  } else {
    const fallback = `- ${T.domain} · ${T.slug} · "${r.statement}" · formulation: ${r.formulation.join('; ') || 'none named'} · searched: ${r.searched || r.evidence.map(e => e.source).join('; ') || 'see the research note'} · held: ${s.reason || 'no card'}`
    pendingEntries.push({ key: r.key, entry: (s.draft && s.draft.pending_entry) || fallback, reason: s.reason || '' })
  }
}
for (const r of held) {
  if (r.disposition === 'pending-no-evidence' || r.disposition === 'pending-no-separating-condition') {
    const lead = r.disposition === 'pending-no-separating-condition' ? 'no separating condition · ' : ''
    const positions = r.positions && r.positions.length ? ` · positions: ${r.positions.map(p => `${p.side} (${p.holder}): ${p.statement} — evidence: ${p.evidence}`).join(' / ')}` : ''
    pendingEntries.push({ key: r.key, entry: `- ${lead}${T.domain} · ${T.slug} · "${r.statement}" · formulation: ${r.formulation.join('; ') || 'none named'}${positions} · searched: ${r.searched || 'see the research note'} · what would unblock: ${r.hold_reason || 'an openable source stating the claim'}`, reason: r.disposition })
  }
}
const agentsRun = sources.length + 1 + outcomes.filter(Boolean).reduce((n, s) => n + (s.draft ? 1 : 0) + (s.verdict ? 1 : 0) + (s.draft1 ? 2 : 0), 0)
log(`Result: ${cards.length} card(s), ${pendingEntries.length} pending entr${pendingEntries.length === 1 ? 'y' : 'ies'}, ${held.filter(r => r.disposition === 'held-not-checkable' || r.disposition === 'folded').length} held or folded; ${agentsRun} agent(s) run`)

return {
  topic: T,
  next_id: NEXT_ID,
  sources,
  spine: { summary: spine.summary, rules: allRules, dropped: spine.dropped || [] },
  outcomes: results,
  cards,
  provenance_lines: provenanceLines,
  pending_entries: pendingEntries,
  held: held.map(r => ({ key: r.key, title: r.title, disposition: r.disposition, hold_reason: r.hold_reason })),
  cost: { agents_run: agentsRun },
}

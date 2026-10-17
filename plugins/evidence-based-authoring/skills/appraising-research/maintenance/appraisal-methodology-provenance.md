# Provenance of the appraisal methodology

One line per source reference behind a claim of the run set — `references/appraisal-methodology.md`, `SKILL.md` and `agents/debate/prompt.md` — keyed by the file and section, so that the run-set line and its provenance line together carry everything known. Each line holds the citation as it stood in the run-set text, then the claim or method it backs. The verification flags close this file: cautions on citations whose wording or figures were not confirmed first-hand.

## SKILL.md

- **SKILL.md § Load-bearing design rule** · Huang et al. 2023 — intrinsic self-correction can degrade reasoning (full entry under § Why a critic needs external grounding).
- **SKILL.md § Load-bearing design rule** · Sharma et al. 2023 — models are sycophantic.
- **SKILL.md § Load-bearing design rule** · Zheng et al. 2023 — models are self-preferring.
- **SKILL.md § Inputs — depth_budget caps (quick 3 / standard 6 / deep 10 debated findings) and the method length targets** · house defaults; no external source, not verified by a measured run.

## agents/debate/prompt.md

- **debate prompt, opening paragraph** · Du et al., arXiv:2305.14325; Irving et al., arXiv:1805.00899 — the separate context of a debate is the mechanism intrinsic self-reflection lacks.
- **debate prompt § role = judge — evidence over verbosity and tone, randomized reading order; G-02** · Zheng et al., "Judging LLM-as-a-Judge with MT-Bench", arXiv:2306.05685 (NeurIPS 2023) — position bias and verbosity bias, the same source as appraisal-methodology § self-preference; the spot-check of the decisive piece of evidence is house convention, hands-on.

## references/appraisal-methodology.md

- **appraisal-methodology § Why a critic needs external grounding — self-correction** · Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet", arXiv:2310.01798 (ICLR 2024) — revision from the model's own knowledge often does not improve and sometimes drops; earlier gains leaked oracle information.
- **appraisal-methodology § Why a critic needs external grounding — sycophancy** · Sharma et al., "Towards Understanding Sycophancy in Language Models", arXiv:2310.13548 (Anthropic 2023).
- **appraisal-methodology § Why a critic needs external grounding — self-preference** · Zheng et al., "Judging LLM-as-a-Judge with MT-Bench", arXiv:2306.05685 (NeurIPS 2023) — self-preference, position and verbosity bias.
- **appraisal-methodology § design invariant 3, retrieval grounding** · RARR, Gao et al., arXiv:2210.08726; FActScore, Min et al., arXiv:2305.14251.
- **appraisal-methodology § rubric-driven design** · Constitutional AI, Bai et al., arXiv:2212.08073.
- **appraisal-methodology § c01 GRADE certainty rating** · Guyatt GH et al., "GRADE: an emerging consensus on rating quality of evidence and strength of recommendations", *BMJ* 2008;336:924–926.
- **appraisal-methodology § c01 Hierarchy of evidence** · OCEBM Levels of Evidence Working Group, "The Oxford 2011 Levels of Evidence", Oxford Centre for Evidence-Based Medicine.
- **appraisal-methodology § c01 Risk-of-bias signal** · RoB 2: Sterne JAC et al., *BMJ* 2019;366:l4898; ROBINS-I: Sterne et al., *BMJ* 2016;355:i4919, seven-domain 2016 list.
- **appraisal-methodology § c01 Quality-of-Information Check** · Heuer RJ Jr. & Pherson RH, *Structured Analytic Techniques for Intelligence Analysis*, CQ Press.
- **appraisal-methodology § c02 Lateral reading** · Wineburg S. & McGrew S., "Lateral Reading" (Stanford History Education Group WP 2017-A1; *Teachers College Record* 2019;121(11)).
- **appraisal-methodology § c02 SIFT** · Caulfield M., "SIFT (The Four Moves)", *Hapgood*, 2019.
- **appraisal-methodology § c02 Argument-from-expert-opinion critical questions** · Walton D., Reed C. & Macagno F., *Argumentation Schemes*, Cambridge University Press, 2008 — the six critical questions.
- **appraisal-methodology § c02 Claim-source match** · RARR, Gao et al., arXiv:2210.08726 — the discipline of attribution.
- **appraisal-methodology § c03 Toulmin warrant reconstruction** · Toulmin S., *The Uses of Argument*, Cambridge University Press, 1958.
- **appraisal-methodology § c03 Key Assumptions Check** · Pherson RH, *Overcoming Analytic Mindsets* (2005); Heuer & Pherson, *Structured Analytic Techniques* — roughly one in four assumptions collapses under written scrutiny.
- **appraisal-methodology § c03 Correlation vs. causation** · Hill AB, "The Environment and Disease: Association or Causation?", *Proc. R. Soc. Med.* 1965;58:295–300.
- **appraisal-methodology § c04 ACH** · Heuer RJ Jr., *Psychology of Intelligence Analysis*, CIA Center for the Study of Intelligence, 1999 (ch. 8).
- **appraisal-methodology § c05 Premortem** · Klein G., "Performing a Project Premortem", *Harvard Business Review*, Sept 2007; underlying study Mitchell, Russo & Pennington, *J. Behavioral Decision Making* 1989;2(1):25–38 — prospective hindsight raises correct identification of reasons by ~30%.
- **appraisal-methodology § c05 Devil's advocacy / red team / what-if** · Heuer & Pherson, *Structured Analytic Techniques*.
- **appraisal-methodology § c05 Suppressed evidence / survivorship / base rate** · Walton D., *Fundamentals of Critical Argumentation*, CUP 2006; Tversky A. & Kahneman D., "Judgment under Uncertainty", *Science* 1974;185:1124–1131.
- **appraisal-methodology § c05 WYSIATI** · Kahneman D., *Thinking, Fast and Slow*, 2011.
- **appraisal-methodology § c06 Cui bono / stakeholder map** · cui bono (Cicero, attributing L. Cassius Longinus Ravilla); Freeman RE, *Strategic Management: A Stakeholder Approach*, Pitman, 1984.
- **appraisal-methodology § c06 Sponsorship-bias check** · Lundh A et al., "Industry sponsorship and research outcome", *Cochrane* 2017, MR000033.pub3 — RR 1.27 (95% CI 1.17–1.37) for favourable results, RR 1.34 (95% CI 1.19–1.51) for favourable conclusions. Historical illustration: Kearns, Schmidt & Glantz, *JAMA Intern. Med.* 2016;176:1680–1685 (Sugar Research Foundation).
- **appraisal-methodology § c06 Conflict-of-interest & purpose** · CRAAP-Purpose: Blakeslee, *LOEX Quarterly* 2004.
- **appraisal-methodology § c07 Paul-Elder intellectual standards** · Paul R. & Elder L., *The Miniature Guide to Critical Thinking* / criticalthinking.org (universal intellectual standards); the count of standards varies 8/9/10 across Foundation for Critical Thinking publications.
- **appraisal-methodology § c07 Fallacy sweep** · Walton, *Fundamentals of Critical Argumentation*, CUP 2006; Tindale C., *Fallacies and Argument Appraisal*, CUP 2007; Stanford Encyclopedia of Philosophy, "Fallacies".
- **appraisal-methodology § c07 Internal consistency** · Bloom "Checking"/"Critiquing"; Anderson & Krathwohl, *A Taxonomy for Learning, Teaching, and Assessing*, Longman, 2001.
- **appraisal-methodology § Adversarial debate protocol** · Du Y. et al., "Improving Factuality and Reasoning… through Multiagent Debate", arXiv:2305.14325; foundational AI safety via debate, Irving G. et al., arXiv:1805.00899.

## Verification flags

Citations to treat with caution when quoting, as the methodology carried them.

- Walton critical questions for *argument from popular opinion* and *cause to effect*: schemes verified; exact CQ wording not confirmed verbatim from an open source.
- Paul-Elder: number of standards varies 8/9/10 across Foundation publications; "Significance" sample questions are reconstructed.
- Herzog & Hertwig (2009) dialectical-bootstrapping effect: reported as a task figure (error 130.8→123.2), not a universal effect size.
- "Superforecasters ~30% better than intelligence officers": journalistic/GJP reporting, not a single controlled effect size.
- ROBINS-I: use the 2016 seven-domain list; a V2 (2025) restructures the domains.
- Mitchell/Russo/Pennington 1989 volume/pages inferred from Klein's attribution; verify the journal record before formal citation.

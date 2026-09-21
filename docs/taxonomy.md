<!-- GENERATED FILE - edit data/ and run `make build`; CI rejects manual edits. -->

# Taxonomy

Six dimensions, one vocabulary file. Every term below is defined in
[`data/taxonomy.yaml`](../data/taxonomy.yaml); the JSON Schema, the README sections,
the issue forms and every figure are generated from it, so a term cannot drift.

Adding or renaming a term is a taxonomy change: open the *taxonomy change* issue
template first, because it re-labels work that is already merged.

## Loop stage

*Field `stage` · one or more values.*

Which turn of the data flywheel does this work act on? The first value decides which README section the entry is filed under.

### Data Generation & Synthesis

`generation` · 5 entries

Producing new training data - instructions, traces, problems, proofs, rollouts - from a model, a program, or a simulator rather than from human annotators.

**Include**

- Self-instruct style bootstrapping and instruction evolution
- Synthetic pretraining corpora and textbook-style data
- Rejection sampling / best-of-n traces harvested for training

**Do not include**

- Human-annotated dataset releases with no model in the loop

### Selection, Filtering & Mixing

`curation` · 4 entries

Deciding what to keep, drop, weight or reorder in a corpus - quality filters, deduplication, influence/attribution, domain mixing.

**Include**

- Importance resampling, influence functions, datamodels, coresets
- Deduplication, decontamination, quality classifiers
- Domain-mixture optimisation and data-constrained scaling

**Do not include**

- Pure architecture or optimiser work with a fixed corpus

### Verification, Reward & Judging

`verification` · 2 entries

Manufacturing the correctness signal that lets a loop keep its own output - verifiers, process reward models, executable checks, judges.

**Include**

- Outcome and process reward models, verifier training
- LLM-as-a-judge, self-taught evaluators, debate and prover-verifier
- Execution, unit tests and formal proof checking as a data filter

**Do not include**

- Human preference collection without a model-side judge

### Assimilation & Self-Training

`assimilation` · 5 entries

Folding the loop's own accepted output back into the weights - self-training, expert iteration, self-play RL, distillation.

**Include**

- STaR / ReST / expert-iteration style iterated fine-tuning
- Self-play and self-rewarding preference optimisation
- Distillation from a stronger or from a past self

**Do not include**

- Prompt-only improvement that never updates parameters

### Task, Curriculum & Environment Generation

`curriculum` · 4 entries

Growing the problem distribution itself: generating tasks, goals, environments and difficulty schedules that keep the loop learnable.

**Include**

- Automatic task / environment generation and open-ended search
- Difficulty scheduling, statement curricula, goal proposal
- Reward-function synthesis for new tasks

**Do not include**

- Fixed benchmarks used only for evaluation

### Experience, Memory & Skill Libraries

`memory` · 1 entries

Non-parametric self-improvement: accumulating experience, skills and workflows that change future behaviour without a weight update.

**Include**

- Skill libraries, agent workflow memory, experience replay for agents
- Verbal reinforcement and reflection stores
- Long-term memory architectures for agents

**Do not include**

- Plain retrieval over a static corpus

### Scaffold & Self-Modification

`scaffold` · 1 entries

The system rewrites the artefact that produced it - its prompts, its code, its agent graph - instead of (or as well as) its data.

**Include**

- Self-referential code improvement and agent-design search
- Prompt evolution and textual gradient optimisation
- Automated design of agentic systems

**Do not include**

- Manual prompt engineering studies

### Benchmarks & Measurement

`measurement` · 1 entries

The instruments: benchmarks, evaluation substrates and metrics that make claims about self-improvement falsifiable.

**Include**

- Benchmarks for autonomous R&D, ML engineering and software agents
- Evaluation protocol and judge-reliability studies
- Capability-trend measurement across model generations

**Do not include**

- Leaderboards without a released, reproducible task set

### Loop Dynamics, Limits & Safety

`dynamics` · 1 entries

What happens when the loop runs many times - collapse, drift, reward hacking, diversity loss, and the theory that predicts them.

**Include**

- Model collapse, self-consuming loops, data accumulation effects
- Reward over-optimisation, self-preference bias, deceptive feedback
- Scaling laws for repeated, pruned or synthetic data

**Do not include**

- Generic robustness work unrelated to a training loop

## Improvement signal

*Field `signal` · one or more values.*

Where does the signal that separates good data from bad data come from?

| Key | Label | Meaning | Entries |
| --- | --- | --- | --: |
| `self` | Self-generated | The same model critiques, scores or filters its own output. | 4 |
| `peer-model` | Peer or teacher model | A separate model provides the signal - a stronger teacher, a reward model, an ensemble, or an LLM judge. | 2 |
| `verifier` | Programmatic verifier | A deterministic check decides: unit tests, execution, answer match, a proof assistant or a symbolic engine. | 5 |
| `environment` | Environment feedback | An interactive environment or game returns reward, success or failure. | 3 |
| `human` | Human supervision | Human seeds, demonstrations, preferences or annotations are a load bearing part of the loop. | 1 |
| `intrinsic` | Intrinsic statistics | No external judge - likelihood, agreement, uncertainty, influence or novelty statistics carry the signal. | 5 |

## Recursion depth

*Field `recursion` · exactly one value · ordered scale.*

How many times does the output of the loop re-enter its own input, and does the loop get to change its own problem space?

| Key | Label | Meaning | Entries |
| --- | --- | --- | --: |
| `single-pass` | Single pass | A one-shot pipeline. Data is produced or curated once; no output of the system is fed back into a later round of itself. | 5 |
| `bootstrap` | One bootstrap round | Generate, filter, train - once. The improved model is the end of the study, not the seed of the next round. | 2 |
| `iterated` | Iterated rounds | The same loop is run for N rounds, each round seeded by the model the previous round produced. | 3 |
| `online` | Continuous / online loop | The loop runs continuously during training or deployment; there is no clean round boundary. | 1 |
| `open-ended` | Open-ended | The loop also expands its own task, goal or environment space, so the objective is never fixed. | 3 |

## Improved artefact

*Field `artifact` · one or more values.*

What does the loop actually leave changed?

| Key | Label | Meaning | Entries |
| --- | --- | --- | --: |
| `data` | Dataset / corpus | The persistent output is a corpus, not a model. | 10 |
| `weights` | Model weights | Parameters are updated by the loop. | 6 |
| `prompt` | Prompts & instructions | The loop optimises text that conditions a frozen model. | 1 |
| `scaffold` | Agent scaffold / code | The loop rewrites the surrounding program or agent graph. | 1 |
| `tools` | Tools & skills | The loop accumulates reusable tools, skills or workflows. | 2 |
| `environment` | Tasks & environments | The loop produces new tasks, problems or environments. | 2 |
| `verifier` | Verifier / reward model | The loop improves the thing that judges, not the thing judged. | 1 |

## Domain

*Field `domain` · one or more values.*

Where is the loop demonstrated?

| Key | Label | Meaning | Entries |
| --- | --- | --- | --: |
| `language` | General language | Instruction following, alignment, general-purpose text. | 8 |
| `code` | Code & software | Program synthesis, software engineering, execution feedback. | 4 |
| `math` | Mathematics & reasoning | Mathematical problem solving and formal theorem proving. | 3 |
| `agent` | Agents & embodiment | Tool use, web/OS agents, embodied and robotic control. | 3 |
| `multimodal` | Multimodal | Vision, audio or joint-modality loops. | 1 |
| `science` | Scientific discovery | Automated research, experiment design, algorithm discovery. | 0 |
| `games` | Games & control | Board games, video games and classical RL control. | 3 |
| `theory` | Theory & domain-general | Results about loops in general rather than in one application - proofs, statistical models, frameworks and position arguments. | 1 |

## Contribution type

*Field `contribution` · exactly one value.*

What kind of artefact is the paper itself?

| Key | Label | Meaning | Entries |
| --- | --- | --- | --: |
| `method` | Method | A new technique, algorithm or training recipe. | 10 |
| `dataset` | Dataset / model release | A released corpus, recipe or model whose contribution is the data. | 0 |
| `benchmark` | Benchmark | An evaluation suite or measurement instrument. | 1 |
| `analysis` | Empirical or theoretical analysis | A study of when and why a loop works or fails. | 1 |
| `survey` | Survey | A literature review or systematisation. | 1 |
| `toolkit` | System / toolkit | Open infrastructure for running these loops. | 1 |
| `position` | Position paper | An argument about direction rather than a result. | 0 |

## Tags

Cross-cutting labels. Optional, flat, and reviewed like any other vocabulary change.

| Tag | Meaning | Entries |
| --- | --- | --: |
| `agent-memory` | Persistent experience stores for agents. | 1 |
| `classic` | Pre-LLM work that established the idea. | 2 |
| `data-mixing` | Choosing domain proportions in a corpus. | 3 |
| `deduplication` | Removing repeated or near-duplicate training text. | 2 |
| `distillation` | A stronger or slower teacher supplies targets for a student. | 0 |
| `diversity` | Coverage, novelty or entropy of the generated data is the concern. | 1 |
| `evolution` | Population-based or mutation/selection search. | 2 |
| `expert-iteration` | Search at inference time, distil the search result back into the policy. | 2 |
| `instruction-tuning` | Post-training on instruction/response pairs. | 1 |
| `model-collapse` | Degradation caused by training on a model's own distribution. | 1 |
| `open-endedness` | The system is meant never to converge. | 3 |
| `process-reward` | Step-level rather than outcome-level supervision. | 1 |
| `reasoning-traces` | Long chains of thought treated as the training asset. | 2 |
| `rejection-sampling` | Oversample, keep only what passes a filter, train on the survivors. | 3 |
| `reward-hacking` | The loop optimises the measure and loses the goal. | 0 |
| `rlaif` | Preference data authored by a model rather than a person. | 1 |
| `scaling-laws` | Quantitative scaling behaviour of data quantity, quality or repetition. | 0 |
| `self-play` | Two or more copies of a system generate each other's training signal. | 1 |
| `test-time-compute` | Trading inference compute for quality, often as a data generator. | 1 |
| `theorem-proving` | Formal mathematics with a proof assistant in the loop. | 0 |
| `weak-to-strong` | A weaker supervisor eliciting stronger capability. | 0 |

## Venue types

| Key | Label |
| --- | --- |
| `conference` | Conference |
| `journal` | Journal |
| `workshop` | Workshop |
| `preprint` | Preprint |
| `tech-report` | Technical report |
| `blog` | Blog / release note |
| `thesis` | Thesis |

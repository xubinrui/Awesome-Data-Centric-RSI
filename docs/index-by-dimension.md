<!-- GENERATED FILE - edit data/ and run `make build`; CI rejects manual edits. -->

# Index by dimension

The same entries as the README, re-cut along every dimension. An entry appears
under each value it carries.

## Improvement signal

### `self` - Self-generated

*The same model critiques, scores or filters its own output.*

- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) · Bai et al. · arXiv 2022
- [Self-Instruct: Aligning Language Models with Self-Generated Instructions](https://arxiv.org/abs/2212.10560) · Wang et al. · ACL 2023
- [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) · Zelikman et al. · NeurIPS 2022
- [Mastering the game of Go without human knowledge](https://doi.org/10.1038/nature24270) · Silver et al. · Nature 2017

### `peer-model` - Peer or teacher model

*A separate model provides the signal - a stronger teacher, a reward model, an ensemble, or an LLM judge.*

- [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) · Lightman et al. · ICLR 2024
- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) · Bai et al. · arXiv 2022

### `verifier` - Programmatic verifier

*A deterministic check decides: unit tests, execution, answer match, a proof assistant or a symbolic engine.*

- [Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954) · Zhang et al. · arXiv 2025
- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) · DeepSeek-AI · arXiv 2025
- [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770) · Jimenez et al. · ICLR 2024
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) · Wang et al. · TMLR 2024
- [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) · Zelikman et al. · NeurIPS 2022

### `environment` - Environment feedback

*An interactive environment or game returns reward, success or failure.*

- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) · Wang et al. · TMLR 2024
- [Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions](https://arxiv.org/abs/1901.01753) · Wang et al. · arXiv 2019
- [Mastering the game of Go without human knowledge](https://doi.org/10.1038/nature24270) · Silver et al. · Nature 2017

### `human` - Human supervision

*Human seeds, demonstrations, preferences or annotations are a load bearing part of the loop.*

- [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) · Lightman et al. · ICLR 2024

### `intrinsic` - Intrinsic statistics

*No external judge - likelihood, agreement, uncertainty, influence or novelty statistics carry the signal.*

- [A Survey on Data Selection for Language Models](https://arxiv.org/abs/2402.16827) · Albalak et al. · arXiv 2024
- [Data Selection for Language Models via Importance Resampling](https://arxiv.org/abs/2302.03169) · Xie et al. · NeurIPS 2023
- [Data-Juicer: A One-Stop Data Processing System for Large Language Models](https://arxiv.org/abs/2309.02033) · Chen et al. · arXiv 2023
- [The Curse of Recursion: Training on Generated Data Makes Models Forget](https://arxiv.org/abs/2305.17493) · Shumailov et al. · arXiv 2023
- [Self-Instruct: Aligning Language Models with Self-Generated Instructions](https://arxiv.org/abs/2212.10560) · Wang et al. · ACL 2023

## Recursion depth

### `single-pass` - Single pass

*A one-shot pipeline. Data is produced or curated once; no output of the system is fed back into a later round of itself.*

- [A Survey on Data Selection for Language Models](https://arxiv.org/abs/2402.16827) · Albalak et al. · arXiv 2024
- [Data Selection for Language Models via Importance Resampling](https://arxiv.org/abs/2302.03169) · Xie et al. · NeurIPS 2023
- [Data-Juicer: A One-Stop Data Processing System for Large Language Models](https://arxiv.org/abs/2309.02033) · Chen et al. · arXiv 2023
- [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) · Lightman et al. · ICLR 2024
- [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770) · Jimenez et al. · ICLR 2024

### `bootstrap` - One bootstrap round

*Generate, filter, train - once. The improved model is the end of the study, not the seed of the next round.*

- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) · Bai et al. · arXiv 2022
- [Self-Instruct: Aligning Language Models with Self-Generated Instructions](https://arxiv.org/abs/2212.10560) · Wang et al. · ACL 2023

### `iterated` - Iterated rounds

*The same loop is run for N rounds, each round seeded by the model the previous round produced.*

- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) · DeepSeek-AI · arXiv 2025
- [The Curse of Recursion: Training on Generated Data Makes Models Forget](https://arxiv.org/abs/2305.17493) · Shumailov et al. · arXiv 2023
- [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) · Zelikman et al. · NeurIPS 2022

### `online` - Continuous / online loop

*The loop runs continuously during training or deployment; there is no clean round boundary.*

- [Mastering the game of Go without human knowledge](https://doi.org/10.1038/nature24270) · Silver et al. · Nature 2017

### `open-ended` - Open-ended

*The loop also expands its own task, goal or environment space, so the objective is never fixed.*

- [Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954) · Zhang et al. · arXiv 2025
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) · Wang et al. · TMLR 2024
- [Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions](https://arxiv.org/abs/1901.01753) · Wang et al. · arXiv 2019

## Improved artefact

### `data` - Dataset / corpus

*The persistent output is a corpus, not a model.*

- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) · DeepSeek-AI · arXiv 2025
- [A Survey on Data Selection for Language Models](https://arxiv.org/abs/2402.16827) · Albalak et al. · arXiv 2024
- [Data Selection for Language Models via Importance Resampling](https://arxiv.org/abs/2302.03169) · Xie et al. · NeurIPS 2023
- [Data-Juicer: A One-Stop Data Processing System for Large Language Models](https://arxiv.org/abs/2309.02033) · Chen et al. · arXiv 2023
- [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) · Lightman et al. · ICLR 2024
- [The Curse of Recursion: Training on Generated Data Makes Models Forget](https://arxiv.org/abs/2305.17493) · Shumailov et al. · arXiv 2023
- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) · Bai et al. · arXiv 2022
- [Self-Instruct: Aligning Language Models with Self-Generated Instructions](https://arxiv.org/abs/2212.10560) · Wang et al. · ACL 2023
- [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) · Zelikman et al. · NeurIPS 2022
- [Mastering the game of Go without human knowledge](https://doi.org/10.1038/nature24270) · Silver et al. · Nature 2017

### `weights` - Model weights

*Parameters are updated by the loop.*

- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) · DeepSeek-AI · arXiv 2025
- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) · Bai et al. · arXiv 2022
- [Self-Instruct: Aligning Language Models with Self-Generated Instructions](https://arxiv.org/abs/2212.10560) · Wang et al. · ACL 2023
- [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) · Zelikman et al. · NeurIPS 2022
- [Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions](https://arxiv.org/abs/1901.01753) · Wang et al. · arXiv 2019
- [Mastering the game of Go without human knowledge](https://doi.org/10.1038/nature24270) · Silver et al. · Nature 2017

### `prompt` - Prompts & instructions

*The loop optimises text that conditions a frozen model.*

- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) · Wang et al. · TMLR 2024

### `scaffold` - Agent scaffold / code

*The loop rewrites the surrounding program or agent graph.*

- [Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954) · Zhang et al. · arXiv 2025

### `tools` - Tools & skills

*The loop accumulates reusable tools, skills or workflows.*

- [Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954) · Zhang et al. · arXiv 2025
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) · Wang et al. · TMLR 2024

### `environment` - Tasks & environments

*The loop produces new tasks, problems or environments.*

- [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770) · Jimenez et al. · ICLR 2024
- [Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions](https://arxiv.org/abs/1901.01753) · Wang et al. · arXiv 2019

### `verifier` - Verifier / reward model

*The loop improves the thing that judges, not the thing judged.*

- [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) · Lightman et al. · ICLR 2024

## Domain

### `language` - General language

*Instruction following, alignment, general-purpose text.*

- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) · DeepSeek-AI · arXiv 2025
- [A Survey on Data Selection for Language Models](https://arxiv.org/abs/2402.16827) · Albalak et al. · arXiv 2024
- [Data Selection for Language Models via Importance Resampling](https://arxiv.org/abs/2302.03169) · Xie et al. · NeurIPS 2023
- [Data-Juicer: A One-Stop Data Processing System for Large Language Models](https://arxiv.org/abs/2309.02033) · Chen et al. · arXiv 2023
- [The Curse of Recursion: Training on Generated Data Makes Models Forget](https://arxiv.org/abs/2305.17493) · Shumailov et al. · arXiv 2023
- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) · Bai et al. · arXiv 2022
- [Self-Instruct: Aligning Language Models with Self-Generated Instructions](https://arxiv.org/abs/2212.10560) · Wang et al. · ACL 2023
- [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) · Zelikman et al. · NeurIPS 2022

### `code` - Code & software

*Program synthesis, software engineering, execution feedback.*

- [Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954) · Zhang et al. · arXiv 2025
- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) · DeepSeek-AI · arXiv 2025
- [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770) · Jimenez et al. · ICLR 2024
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) · Wang et al. · TMLR 2024

### `math` - Mathematics & reasoning

*Mathematical problem solving and formal theorem proving.*

- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) · DeepSeek-AI · arXiv 2025
- [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) · Lightman et al. · ICLR 2024
- [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) · Zelikman et al. · NeurIPS 2022

### `agent` - Agents & embodiment

*Tool use, web/OS agents, embodied and robotic control.*

- [Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954) · Zhang et al. · arXiv 2025
- [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770) · Jimenez et al. · ICLR 2024
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) · Wang et al. · TMLR 2024

### `multimodal` - Multimodal

*Vision, audio or joint-modality loops.*

- [Data-Juicer: A One-Stop Data Processing System for Large Language Models](https://arxiv.org/abs/2309.02033) · Chen et al. · arXiv 2023

### `science` - Scientific discovery

*Automated research, experiment design, algorithm discovery.*

- *(no entries yet)*

### `games` - Games & control

*Board games, video games and classical RL control.*

- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) · Wang et al. · TMLR 2024
- [Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions](https://arxiv.org/abs/1901.01753) · Wang et al. · arXiv 2019
- [Mastering the game of Go without human knowledge](https://doi.org/10.1038/nature24270) · Silver et al. · Nature 2017

### `theory` - Theory & domain-general

*Results about loops in general rather than in one application - proofs, statistical models, frameworks and position arguments.*

- [The Curse of Recursion: Training on Generated Data Makes Models Forget](https://arxiv.org/abs/2305.17493) · Shumailov et al. · arXiv 2023

## Contribution type

### `method` - Method

*A new technique, algorithm or training recipe.*

- [Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954) · Zhang et al. · arXiv 2025
- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) · DeepSeek-AI · arXiv 2025
- [Data Selection for Language Models via Importance Resampling](https://arxiv.org/abs/2302.03169) · Xie et al. · NeurIPS 2023
- [Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) · Lightman et al. · ICLR 2024
- [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) · Wang et al. · TMLR 2024
- [Constitutional AI: Harmlessness from AI Feedback](https://arxiv.org/abs/2212.08073) · Bai et al. · arXiv 2022
- [Self-Instruct: Aligning Language Models with Self-Generated Instructions](https://arxiv.org/abs/2212.10560) · Wang et al. · ACL 2023
- [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) · Zelikman et al. · NeurIPS 2022
- [Paired Open-Ended Trailblazer (POET): Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions](https://arxiv.org/abs/1901.01753) · Wang et al. · arXiv 2019
- [Mastering the game of Go without human knowledge](https://doi.org/10.1038/nature24270) · Silver et al. · Nature 2017

### `dataset` - Dataset / model release

*A released corpus, recipe or model whose contribution is the data.*

- *(no entries yet)*

### `benchmark` - Benchmark

*An evaluation suite or measurement instrument.*

- [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770) · Jimenez et al. · ICLR 2024

### `analysis` - Empirical or theoretical analysis

*A study of when and why a loop works or fails.*

- [The Curse of Recursion: Training on Generated Data Makes Models Forget](https://arxiv.org/abs/2305.17493) · Shumailov et al. · arXiv 2023

### `survey` - Survey

*A literature review or systematisation.*

- [A Survey on Data Selection for Language Models](https://arxiv.org/abs/2402.16827) · Albalak et al. · arXiv 2024

### `toolkit` - System / toolkit

*Open infrastructure for running these loops.*

- [Data-Juicer: A One-Stop Data Processing System for Large Language Models](https://arxiv.org/abs/2309.02033) · Chen et al. · arXiv 2023

### `position` - Position paper

*An argument about direction rather than a result.*

- *(no entries yet)*

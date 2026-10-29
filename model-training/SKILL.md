---
name: model-training
description: Train, fine-tune, pretrain, or continue training ML models on the shared HPC server with official recommended defaults, durable checkpoints, and automatic recovery. Use for model-training workloads; do not use for inference-only, evaluation-only, or generic data-processing tasks.
---

# Model Training

Treat training as a durable task, not a one-shot Slurm job. Preserve the intended training semantics across submission, interruption, and recovery.

## Precedence

Apply instructions in this order:

1. The user's explicit choices.
2. Changes strictly required by the actual server environment or dataset schema.
3. The complete official recommended configuration for the selected model, method, dataset recipe, and software version.

Before planning or launching training, read [references/official-defaults.md](references/official-defaults.md). Treat the official recipe as an indivisible baseline. Never tune, “improve,” fill gaps from habit, or guess any training or preprocessing setting silently.

Before submission, read [references/recovery.md](references/recovery.md). Automatic recovery is the target contract, **but the current HPC Agent CLI does not yet implement an autonomous recovery supervisor**. Do not promise unattended recovery; if it is essential for this run, pause in WAITING_USER until a tested supervisor is available or the user explicitly accepts monitored manual recovery.

## Scope

This skill inherits only the server-use contract below from `$hpc-agent`. It does not inherit that skill's routing for inference, evaluation, benchmarking, robotics, or unrelated model-project work.

## Server-use contract

- Use `h100-15` unless the user explicitly selects another permitted environment.
- Start with `ssh h100-15 '~/hpc-agent/bin/hpc-agent recovery-check'`.
- Inspect the project, task database, Git state, and locked duplicate check before submission.
- Use `~/hpc-agent/bin/hpc-agent` for task lifecycle operations. Submit all GPU work through Slurm; never launch GPU training directly in a login shell.
- Keep medium priority by default. Low priority requires explicit “not urgent” intent; high priority or interrupting another normal job requires explicit approval.
- Ask before requesting at least 24 GPUs, raising QOS, interrupting a normal job, destructive cleanup, semantic reruns, or overwriting outputs.
- Keep smoke validation and formal training in the same allocation when practical. Register durable non-GPU stages and run them through the agent rather than an unmanaged shell.
- Do not push code or artifacts unless the user asks.

## Training launch contract

Before submission:

1. Resolve the complete official recipe and record every required deviation. If any effective setting cannot be traced to that recipe, an explicit user choice, or a strictly necessary adaptation, do not launch.
2. Save the resolved configuration, launch command, source URL or file, dependency versions, dataset identity, and Git commit with the run.
3. Run a small validation that checks data loading, forward/backward passes, checkpoint writing, and checkpoint resumption without changing formal-run semantics.
4. Use a new output directory unless the action is a validated resume of the same task.
5. Define a durable checkpoint directory and a tested resume command. Preserve model, optimizer, scheduler, scaler, global step, random state, and data/sampler progress when the framework supports them.
6. Configure Slurm requeue and durable remote supervision. Do not claim that a run can recover automatically merely because checkpoints exist.

Before submission, compare the complete effective configuration and preprocessing pipeline with the official baseline. The difference must be empty except for explicitly authorized or strictly necessary adaptations. Unexplained differences fail closed in `WAITING_USER`.

Show the user a concise summary of the official baseline, permitted differences, resources, checkpoint plan, and recovery behavior. Ordinary-cost training may then proceed; apply the server-use approval gates above.

## Recovery invariant

Unless the user explicitly stops the task, or training is probably incorrect and needs the user's decision, every failed or interrupted training task remains active and must be recovered automatically from the latest valid checkpoint.

- Keep recovery under the same task and stage; do not create a duplicate task or silently restart from step zero.
- Infrastructure failures may change placement, requested host memory, or other non-semantic execution settings. They must not silently change the model or training recipe.
- If an exact resume is impossible, corrupted, or ambiguous, stop in `WAITING_USER` and explain what state would be lost before offering a restart.
- A suspected data, configuration, numerical, or objective error also enters `WAITING_USER`; repeated preemption, host unavailability, or scheduler delay does not.

Follow the failure-class decisions and validation requirements in [references/recovery.md](references/recovery.md).

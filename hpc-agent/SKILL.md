---
name: hpc-agent
description: Route model, VLA/VLM/LLM, robotics, training, GPU inference, evaluation, benchmark, and remote model-project work through the shared h100-15 HPC Agent. Use when work needs the remote GPU cluster or continues an HPC task; do not use when the user explicitly requests local execution.
---

# HPC Agent

- Treat the user's current instruction as authoritative, then project configuration, then these defaults.
- Default model/HPC work to `h100-15`. At the start, run `ssh h100-15 '~/hpc-agent/bin/hpc-agent recovery-check'` and briefly report anything needing attention.
- Use `~/hpc-agent/bin/hpc-agent` for task state and Slurm actions. Never run a GPU workload outside Slurm.
- Before submission, inspect the project and existing task state, protect uncommitted work, and let `hpc-agent submit` perform the final locked duplicate check. Show its execution summary, then proceed without another confirmation for an ordinary task.
- Ask immediately before high-cost or high-risk changes: very large/long allocations, `>=24` GPUs, higher Slurm priority, interrupting a valid normal-priority job, destructive output changes, reruns, or changes to experimental meaning. “Urgent” does not authorize higher QOS.
- Use medium priority unless the user explicitly says the task is not urgent; only then use low priority. Never select high priority without explicit approval.
- Keep smoke and formal training in one allocation with `--smoke-command` plus `--command` when they are one workflow. Do CPU preflight before submission.
- Register every long task. Use `run-detached` for non-GPU long work and keep predetermined stages remote so they survive local Agent shutdown.
- Do not silently change batch size, learning rate, model/loss, resolution, data filtering, LoRA rank, metrics, or training strategy. Do not push Git changes unless asked.

> Implementation note (2026-10-29): The CLI currently performs manual, checkpoint-explicit resume only. The autonomous supervisor described below is a required **future capability**, not currently implemented. Do not claim it is deployed.\n\n# Automatic Training Recovery

## Required design before launch

A formal run must have all of the following:

- a durable checkpoint directory outside ephemeral job-local storage;
- periodic full-state checkpoints at a cadence derived from the official recipe, not an invented tuning choice;
- a resume command tested during validation;
- Slurm requeue or equivalent handling for preemption and node failure;
- durable remote supervision that observes terminal job state and resubmits when Slurm cannot requeue it;
- enough recorded task metadata to reproduce the same allocation and command.

Checkpoint existence alone is not automatic recovery. The job must be able to relaunch without an interactive Codex or Claude session and select the newest valid checkpoint.

## Failure decisions

### Preemption, eviction, node failure, or scheduler interruption

Requeue or resubmit automatically on an allowed node. Resume the same task from the newest valid checkpoint. Do not count ordinary preemptions as permission to lower priority, change the recipe, or restart from zero.

### Training restricted to one server or requested node unavailable

Keep the task queued for the permitted server and retry with bounded backoff. Changing Slurm placement is allowed only within the server policy. Do not redirect data or work to an unapproved machine.

### Requested host memory exceeded

Confirm host-memory OOM from scheduler evidence, then increase only the Slurm host-memory request within the node's available capacity and resume automatically. Keep the training command and recipe unchanged. If the workload exceeds physical capacity, diagnose the source; do not silently alter data or model semantics.

### GPU out of memory

Treat this separately from host memory. Automatically use only an official, documented execution mode for the exact recipe when it preserves the intended semantics, and record it as an environment adaptation. If recovery would alter the official training or preprocessing recipe, enter `WAITING_USER`; resource pressure is not permission to tune parameters.

### Transient storage, network, or distributed communication failure

Retry the same stage from the newest valid checkpoint with bounded backoff. Verify storage health and checkpoint integrity before resubmission. Do not delete a questionable checkpoint until a valid earlier checkpoint is confirmed.

### Suspected training error

Loss divergence, persistent NaN/Inf, invalid labels, data leakage, incompatible shapes, corrupt inputs, wrong objective, or a materially unexpected metric trend is not an infrastructure retry. Stop further spending, preserve evidence, and enter `WAITING_USER` with the smallest concrete decision required.

## Resume validation

Before resubmission, validate that the selected checkpoint belongs to the same task, dataset, code commit, model configuration, and output lineage. Prefer the newest checkpoint that is complete and readable.

Verify restoration of model weights and, when supported, optimizer, scheduler, scaler, global step, random state, and sampler/data-loader progress. Confirm that the first resumed log continues from the recorded step and does not overwrite earlier artifacts.

If the framework saves weights only, state that exact continuation is impossible. Do not call a warm start or step-zero restart a resume.

## Recovery loop and stop conditions

- Keep one task ID and append recovery events to its history.
- Requeue/resubmit transient infrastructure failures automatically. Use bounded backoff to avoid a tight retry loop.
- Make at most two automatic corrective configuration changes for the same failure signature. Pure requeues with no recipe change do not consume this budget.
- After a correction, run the smallest validation that proves checkpoint continuation before spending on the full allocation.
- Stop automatically only for an explicit user stop, a suspected training error, an invalid or ambiguous checkpoint, a recovery that would change semantics or cross an approval gate, or repeated identical failures with no new safe corrective action. Use `WAITING_USER` and preserve all evidence.
- Never raise QOS, add GPUs, cancel another normal job, overwrite outputs, or restart from zero as an automatic recovery action.

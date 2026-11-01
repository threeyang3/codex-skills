# Official Baseline and Closed-World Deviations

## Source order

Use the first applicable source below for the exact model, training method, dataset recipe, and installed software version:

1. An official upstream training config or official example command.
2. The official documentation for that exact release.
3. A checked-in project config that explicitly and verifiably mirrors the upstream default.

If no authoritative default can be identified, ask the user. Do not construct a plausible recipe from memory, a third-party tutorial, or a different model variant.

Record the source URL or repository path, release or commit, retrieval date, and the final resolved configuration. Preserve the official training entrypoint and all configuration artifacts needed to resolve its behavior.

## Closed-world baseline

The complete official recipe is frozen as a unit, including every explicit value, inherited default, preprocessing step, training objective, and framework behavior that affects the run. A setting does not become editable merely because it is implicit, absent from a command line, or not mentioned in this reference.

Do not substitute personal conventions, remembered best practices, values from another model or dataset, or settings chosen for convenience. Do not reinterpret an official omission as permission to invent a value; preserve the upstream program's own default behavior.

Only two classes of differences are permitted:

1. A choice explicitly requested by the user.
2. The smallest change proven necessary for the actual environment or dataset interface.

Everything else is forbidden. If the necessity, provenance, or semantic effect of a difference is uncertain, enter `WAITING_USER` rather than making the change.

## Required adaptations

Make only the smallest change that is necessary and traceable. Keep adaptations in a thin launch or data-interface layer when possible so the official recipe remains intact and auditable.

Environment adaptations may include paths, caches, output directories, launcher topology, permitted node placement, CPU workers, host-memory requests, and container or dependency wiring. These must not alter training semantics.

Dataset adaptations may include file paths, column or feature mappings, split names, label mappings, and the official processor/tokenizer required by the model. A changed number of classes, head shape, tokenizer vocabulary, resolution, sequence length, sampling distribution, or loss is semantic: explain it and obtain direction unless the user's request already makes that change necessary and unambiguous.

Resource pressure is not general permission to tune. Use only an official, documented execution mode for the exact recipe when it preserves the intended semantics. If resolving the pressure requires changing the recipe, stop in `WAITING_USER` unless the user has already authorized that specific adaptation.

## Mandatory difference gate

Before training, compare the fully resolved effective configuration and preprocessing pipeline against the official baseline. Maintain an allowlist containing only explicit user choices and proven required adaptations. Every observed difference must match one allowlist entry and carry its source, necessity, and semantic impact.

Launch only when the unexplained-difference set is empty. This is a fail-closed gate: inability to inspect or resolve a setting is a reason to pause, not a reason to assume equivalence.

## Reproducibility record

Persist with every run:

- the untouched official source, the fully resolved effective configuration, and their machine-readable difference;
- the exact command, dependency versions, environment identity, and Git commit;
- dataset version or manifest and preprocessing identity;
- requested resources, effective global batch, seed, and output directory;
- the complete allowlist of user overrides and required adaptations, with evidence and reason;
- confirmation that no unexplained difference remained at submission time.

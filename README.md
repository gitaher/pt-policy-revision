# PersonalTrader Policy Revision

Choose a signal-confidence threshold using only mature calibration feedback and deterministic error costs.

Makes lightweight policy revision measurable with a fixed underlying LLM. No orders, holdings or transaction-log reconstruction are involved.

## Tools

- `compute`: typed `TaskInput` to `TaskOutput`. No network, no model, no file writes.
- `revise-policy`: agent task; call `compute` with the input and submit its typed result.
  The agent is permitted to choose its tool call, while arithmetic stays in code.
  No reference tool is needed: the verifier independently recomputes from immutable task arguments.

`contract.py` defines all fields. `tests/fixture.json` is a hand-computed example input and expected output.
The executable specification is in `verifier/checks.py`; the tool uses a separate implementation in
`src/plugin/logic.py`. Numeric tolerance is 1e-9 absolute/relative; all other values and order are exact.
Cutoffs are inclusive. UTC timestamps must be YYYY-MM-DDTHH:MM:SSZ. Invalid inputs raise errors.

## Layout

`src/plugin/`: MCP runtime and tools. `verifier/`: pure deterministic checks.
`tests/`: positive, negative and boundary tests plus a synthetic fixture.
`ui/`: schema renderer. `product/`: marketplace description.
Reports and execution evidence are deliberately kept outside this repository.

## Develop and run

Requires Git, uv, Python >=3.12. Dependencies are pinned in `uv.lock`.
The lock graph originates from the official arxiv-source reference, whose dependencies match this
plugin; only this project's name/version were changed. Validate it before publishing.

```bash
uv lock --check
uv sync --frozen --extra dev
uv run pytest
uv run ruff check .
```

Offline core verification (no dependencies, Python >=3.12):

```bash
python3 -m unittest discover -s tests -v
```

The contract round-trip test is skipped if slimconfig is unavailable; this is not full harness validation.
For full checks, install nanoagent separately and run `nanoagent plugin inspect <absolute-plugin-path>`.
Use `nanoagent plugin agent` with a `PluginOpenRouterAgentConfig` and an arguments JSON containing
the `input` object from `tests/fixture.json`; save the resulting verdict and trajectory outside this repo.
The platform selects its model; the plugin never selects or calls one itself.

Task limitations: Calibration loss improvement is not out-of-sample trading improvement. Strength and correctness are supplied labels. A later untouched test period and costs are needed to establish economic benefit.

Status remains `in-development` until frozen dependency setup, harness checks and a real agent run pass.
This repository contains synthetic test data, not Alpaca/SEC/live news observations or a completed trading study.

# Baseline Audit Report

Date: 2026-10-11  
Repository: `https://github.com/syamsunderab-hub/adaptive-security-framework`  
Baseline commit: `295307e feat: Initial release of Adaptive Security Framework Command Center (SAFER-D)`  
Baseline branch: `main` tracking `origin/main`

## Scope and baseline safety

The workspace contained an empty Git repository with no local files, commits, remotes, or untracked user work. The supplied repository was fetched into that repository and checked out as `main`; no destructive Git operation was used. The initial repository had one commit.

## Architecture and component inventory

| Component | Files | Baseline status | Findings |
|---|---|---|---|
| Cloud, fog, and edge topology | `backend/app/core/config.py`, `backend/app/services/global_controller.py` | Implemented but not adequately tested | Seven in-process `NodeState` objects model the hierarchy. They are not independent processes or networked distributed nodes. |
| Local MAPE-K loop | `services/monitor.py`, `analyzer.py`, `planner.py`, `executor.py`, `knowledge.py` | Implemented but not adequately tested | The stages execute in order for each online node. Knowledge is mostly process memory; the executor has no explicit enforcement adapter or verification result. |
| Global controller | `services/global_controller.py`, `adaptation_manager.py` | Partially implemented | Upstream propagation and full/partial mode transitions exist. Coordination is deterministic parent escalation, not multi-controller reconciliation or partition conflict resolution. |
| Monitoring and analysis | `services/monitor.py`, `services/analyzer.py` | Implemented but not adequately tested | Weighted rule-based score exists. Inputs are not range-validated, timestamps are not checked for staleness, and threat evidence is not persisted with every adaptation decision. |
| Planning and policy | `services/planner.py`, `services/security_manager.py`, `services/knowledge.py` | Implemented but not adequately tested | Thresholds and restrictions exist. There is no hysteresis, dwell time, cooldown, or overlap-aware de-escalation policy. |
| Execution and enforcement | `services/executor.py` | Partially implemented | Security levels and restriction labels are changed in memory and an adaptation record is written. Actions are simulated, but baseline records no explicit simulated/requested/verified/failed status. |
| Heartbeats and recovery | `services/heartbeat_manager.py` | Implemented but not adequately tested | Timeout, duplicate-offline suppression, recovering state, and partial mode callbacks exist. Recovery is timer-based and does not validate fresh telemetry or safe posture before reintegration. |
| Persistence and audit history | `core/database.py`, `services/knowledge.py`, `state/system_state.py` | Partially implemented | SQLite tables exist for events, threats, adaptations, and heartbeats. In-memory history takes precedence over DB history, so persisted records are hidden after restart if any new in-memory event exists. Writes swallow errors. |
| REST and WebSocket API | `api/routes_*.py`, `main.py`, `core/websocket_manager.py` | Implemented but not adequately tested | Core node, event, security, simulation, and WebSocket paths exist. WebSocket broadcasts are best effort and there is no API for structured decision audit records. |
| Frontend dashboard | `frontend/src/**` | Implemented but not build-verified | React/TypeScript topology, timeline, MAPE-K, and simulation views exist. The build could not run because npm packages were not installed in the baseline environment. |
| Threat simulation | `services/simulation_engine.py` | Simulated only | ICMP flood, port scan, brute-force, failure, recovery, and demo scenarios mutate synthetic telemetry. They do not represent real attack detection or network enforcement. |
| Tests | `backend/tests/test_framework.py` | Partially implemented | Six baseline tests exist. Async tests are marked with `pytest.mark.asyncio` but `pytest-asyncio` is missing from requirements and the environment. |

## Baseline commands and results

| Command | Result |
|---|---|
| `python -m pytest backend/tests/test_framework.py -q` | 3 passed, 3 failed at collection/execution because async functions were unsupported; `pytest-asyncio` was absent. |
| `python -m compileall -q backend` | Passed. |
| `npm run build` from `frontend` | Could not run: `tsc` was not installed because npm dependencies were absent. |
| Git inspection | Clean `main` branch at baseline commit; no local changes before this report. |

No backend service or browser workflow was started during the baseline because the missing async test dependency and frontend packages were first recorded as environment gaps. SQLite persistence and WebSocket behavior were inspected statically.

## Confirmed defects and risks

1. Adaptation execution reports no action mode, enforcement result, or verification result. A simulated in-memory restriction can therefore appear equivalent to successful enforcement.
2. Analysis accepts negative, non-finite, and stale telemetry without validation. Identical valid inputs are deterministic, but invalid/missing-data semantics are undefined.
3. Every noisy observation can change the target level; there is no hysteresis, dwell time, or cooldown to prevent oscillation.
4. Recovery changes an offline node to `ONLINE` after a sleep without validating fresh telemetry, state, or safe de-escalation.
5. `SystemState.get_events()` returns only in-memory events whenever that list is non-empty, hiding older SQLite history after restart.
6. SQLite write errors are printed and discarded, so the caller cannot distinguish durable audit success from failure.
7. The project is an in-process simulation. The node agent only polls the controller and does not implement an independent local loop or real enforcement.

## Prioritized implementation plan

- **P0:** Make execution outcomes explicit and truthful; validate telemetry and never claim simulated actions are enforced.
- **P1:** Add structured decision audit records, persistence/API access, safe hysteresis/cooldown controls, and recovery validation.
- **P2:** Add deterministic experiment scenarios and comparative baselines; improve frontend observability after the backend contract is stable.
- **P3:** Consider advanced detection algorithms and real isolated enforcement adapters only when a controlled test environment is available.

## Baseline conclusion

The prototype demonstrates the shape of a local and global MAPE-K loop, but baseline evidence supports describing it as a single-process, simulated adaptive-security command center. The first implementation pass will preserve the existing API and UI while making audit and enforcement semantics explicit and testable.

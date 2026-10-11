"""Run deterministic comparisons of static, local-only, and coordinated adaptation.

This runner uses synthetic telemetry only. It measures the prototype's rule-based
detector and policy selection; it does not claim to model real network attacks.
"""
import argparse
import json
import random
import time
from pathlib import Path
from typing import Dict, Any

from backend.app.models.node import NodeTelemetry, SecurityLevel
from backend.app.models.threat import ThreatType
from backend.app.services.analyzer import analyzer_engine
from backend.app.services.security_manager import security_level_manager

BASELINE = {"traffic": 85.0, "connections": 25.0, "cpu": 8.0}

def make_observation(step: int, scenario: str, rng: random.Random) -> NodeTelemetry:
    jitter = rng.uniform(-2.0, 2.0)
    if scenario == "normal":
        return NodeTelemetry(cpu_percent=8.0 + jitter, network_traffic_pps=85.0 + jitter, connection_count=25, failed_auth_count=0)
    if scenario == "icmp_flood":
        return NodeTelemetry(cpu_percent=15.0 + step * 12, network_traffic_pps=85.0 + step * 1800, connection_count=25 + step * 35, failed_auth_count=0)
    if scenario == "multiple_threats":
        return NodeTelemetry(cpu_percent=25.0 + step * 10, network_traffic_pps=85.0 + step * 1200, connection_count=25 + step * 100, failed_auth_count=step * 4)
    raise ValueError(f"Unknown scenario: {scenario}")

def run_strategy(strategy: str, scenario: str, seed: int) -> Dict[str, Any]:
    rng = random.Random(seed)
    level = SecurityLevel.DEFCON_5
    trace = []
    detection_step = None
    for step in range(1, 5):
        telemetry = make_observation(step, scenario, rng)
        started = time.perf_counter()
        risk, threat, severity, confidence, description, _ = analyzer_engine.analyze(telemetry, BASELINE)
        requested = security_level_manager.calculate_level_from_score(risk)
        proposed = SecurityLevel.DEFCON_5 if strategy == "static" else requested
        if strategy == "coordinated" and requested.level_int <= 3:
            proposed = SecurityLevel.from_int(max(1, requested.level_int - 1))
        if detection_step is None and threat != ThreatType.NORMAL:
            detection_step = step
        trace.append({
            "step": step, "telemetry": telemetry.model_dump(), "risk_score": risk,
            "threat": threat.value, "severity": severity.value, "confidence": confidence,
            "previous_level": level.value, "requested_level": requested.value,
            "selected_level": proposed.value, "latency_ms": round((time.perf_counter() - started) * 1000, 4),
            "description": description,
        })
        level = proposed
    return {
        "strategy": strategy,
        "scenario": scenario,
        "seed": seed,
        "metrics": {
            "detection_step": detection_step,
            "detection_latency_steps": detection_step,
            "adaptation_count": sum(1 for item in trace if item["selected_level"] != item["previous_level"]),
            "final_level": level.value,
            "availability": 1.0,
        },
        "trace": trace,
    }

def run_experiment(seed: int = 7, scenario: str = "icmp_flood") -> Dict[str, Any]:
    results = [run_strategy(strategy, scenario, seed) for strategy in ("static", "local_only", "coordinated")]
    return {
        "experiment": "adaptive-security-strategy-comparison",
        "generated_at": time.time(),
        "configuration": {"seed": seed, "scenario": scenario, "baseline": BASELINE},
        "metric_definitions": {
            "detection_latency_steps": "First synthetic observation step classified as non-NORMAL; one step is one generated sample.",
            "adaptation_count": "Number of trace samples where selected security level differs from previous level.",
            "availability": "Fraction of simulated nodes available; this runner has one always-available synthetic node, so it is 1.0.",
        },
        "results": results,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--scenario", choices=("normal", "icmp_flood", "multiple_threats"), default="icmp_flood")
    parser.add_argument("--output", type=Path, default=Path("experiment-results.json"))
    args = parser.parse_args()
    result = run_experiment(args.seed, args.scenario)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "summary": [item["metrics"] for item in result["results"]]}, indent=2))

if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path


WEB = Path(__file__).resolve().parents[1]
ASSET = WEB / "assets/index-closedloop-20260719-v2.js"
ROOT = Path("/Users/yutinghuang/Documents/agent code/chem-agent-dll-main-online-transfer-eval-20260719")
BASE = ROOT / "result/chem-agent-eval-20260719-170009"
LOOP = ROOT / "result/device-retry-C01-C02-D01-20260719/closed-loop"
FINAL_ITERATION = {"C01": 1, "C02": 3, "D01": 1}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compact_research(state: dict) -> dict:
    keep = [
        "campaign_id", "status", "current_branch", "next_branch", "event",
        "survey_queries", "survey_report", "knowledge_hits", "extracted_protocols",
        "stage_route", "current_stage", "current_stage_plan", "stage_route_reason",
        "current_stage_reason", "macro_plan", "previous_macro_plan", "plan_revisions",
        "latest_observation", "cumulative_device_constraints", "failed_plan_signatures",
        "logs", "errors", "created_at",
    ]
    return {key: state[key] for key in keep if key in state}


def iteration_rows(case: str, final_iteration: int) -> list[dict]:
    rows: list[dict] = []
    for iteration in range(1, final_iteration + 1):
        research = load(LOOP / case / f"iteration-{iteration}-research-state.json")
        package = load(LOOP / case / f"iteration-{iteration}-device-package.json")
        rows.append({
            "iteration": iteration,
            "phase": "closed_loop_device_mapping",
            "status": package.get("status", "unknown"),
            "research_status": research.get("status"),
            "research_stage": research.get("current_stage"),
            "macro_steps": len(research.get("macro_plan") or []),
            "device_status": package.get("status"),
            "device_steps": len((package.get("workflow_json") or {}).get("steps") or []),
            "feedback_type": package.get("feedback_type"),
        })
    return rows


def build_case(case: str) -> dict:
    iteration = FINAL_ITERATION[case]
    original_input = load(BASE / case / "input.json")
    research = load(LOOP / case / f"iteration-{iteration}-research-state.json")
    device = load(LOOP / case / f"iteration-{iteration}-device-package.json")
    history = iteration_rows(case, iteration)
    device["evaluation"] = {
        "process_completion": "yes",
        "paper_quality_summary": "low",
        "dispatch_schema_match": "not_reaudited_after_closed_loop",
        "capability_classification": "Research↔Device 闭环成功",
        "capability_summary": (
            f"初始 Device 返回 feasibility_error 后，Research B2 根据设备约束重新规划；"
            f"最终第 {iteration} 轮 Device 生成 {len((device.get('workflow_json') or {}).get('steps') or [])} 个步骤并返回 success。"
        ),
        "capability_tone": "success",
        "requires_scientific_review": True,
    }
    logs = []
    for row in history:
        logs.append(
            f"[closed-loop] iteration={row['iteration']} research={row['research_status']} "
            f"macro={row['macro_steps']} device={row['device_status']} steps={row['device_steps']}"
        )
    final_steps = len((device.get("workflow_json") or {}).get("steps") or [])
    return {
        "job": {
            "schema_version": "1.0",
            "id": f"demo-{case}",
            "campaign_id": f"{case}-20260719-170009",
            "demo": True,
            "source_case": case,
            "mode": "full_campaign",
            "adapter": "read_only_demo",
            "query": original_input["query"],
            "status": "success",
            "phase": "device_mapping",
            "stop_reason": "completed",
            "iteration": iteration,
            "created_at": "2026-07-19T17:00:09+08:00",
            "updated_at": "2026-07-19T19:30:00+08:00",
        },
        "research": compact_research(research),
        "device": device,
        "plan_revisions": research.get("plan_revisions") or [],
        "iterations": history,
        "final_report": (
            f"初始设备方案不可行后，Device 约束已反馈至 Research B2。"
            f"经过 {iteration} 轮 Research↔Device 闭环，最终生成 {final_steps} 个 Device Step，状态 success。"
        ),
        "logs": {"lines": logs, "cursor": len(logs)},
        "status": "completed",
        "phase": "device_mapping",
        "stop_reason": "completed",
        "demo": True,
        "source_case": case,
    }


def replace_case(source: str, case: str, next_case: str | None) -> str:
    markers = [
        f'{{job:{{schema_version:"1.0",id:"demo-{case}"',
        f'{{"job":{{"schema_version":"1.0","id":"demo-{case}"',
        f'{{"job":{{"id":"demo-{case}"',
    ]
    start_marker = next(marker for marker in markers if marker in source)
    start = source.index(start_marker)
    if next_case:
        end_markers = [
            f',{{job:{{schema_version:"1.0",id:"demo-{next_case}"',
            f',{{"job":{{"schema_version":"1.0","id":"demo-{next_case}"',
            f',{{"job":{{"id":"demo-{next_case}"',
        ]
        end_marker = next(marker for marker in end_markers if marker in source)
        end = source.index(end_marker, start)
        return source[:start] + json.dumps(build_case(case), ensure_ascii=False, separators=(",", ":")) + source[end:]
    raise ValueError("A following case marker is required")


def main() -> None:
    source = ASSET.read_text(encoding="utf-8")
    source = replace_case(source, "C01", "C02")
    source = replace_case(source, "C02", "D01")
    source = replace_case(source, "D01", "D02")
    source = source.replace(
        'F==="completed"?"Research + Device":F==="manual_required"?"Research 质量门":"Device 可行性"',
        '(F==="completed"||F==="success")?"Research + Device":F==="manual_required"?"Research 质量门":"Device 可行性"',
    )
    ASSET.write_text(source, encoding="utf-8")
    print(ASSET)


if __name__ == "__main__":
    main()

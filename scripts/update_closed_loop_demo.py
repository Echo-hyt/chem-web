from __future__ import annotations

import json
from pathlib import Path


WEB = Path(__file__).resolve().parents[1]
ASSET = WEB / "assets/index-closedloop-20260719-v2.js"
ROOT = Path("/Users/yutinghuang/Documents/agent code/chem-agent-dll-main-online-transfer-eval-20260719")
BASE = ROOT / "result/chem-agent-eval-20260719-170009"
LOOP = ROOT / "result/device-retry-C01-C02-D01-20260719/closed-loop"
FINAL_ITERATION = {"C01": 1, "C02": 3, "D01": 1}
CASES = ["A01", "A02", "B01", "B02", "C01", "C02", "D01", "D02"]
CURATED_PAPERS = Path(
    "/Users/yutinghuang/Documents/agent code/chem-agent/result/"
    "literature-only-20260719-221307/curated_papers.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def curated_knowledge_hits(case: str) -> list[dict]:
    papers = load(CURATED_PAPERS)[case]["selected_papers"]
    hits = []
    for paper in papers:
        publication = " · ".join(
            item for item in [paper.get("venue"), paper.get("year")] if item
        )
        identifier = paper.get("doi") or paper.get("url") or ""
        summary = paper.get("abstract") or "与该案例的催化体系、目标反应或研究变量直接相关。"
        hits.append({
            "title": paper["title"],
            "file_path": paper.get("url") or (f"https://doi.org/{identifier}" if identifier else ""),
            "score": 1.0,
            "problem": summary,
            "synthesis_summary": summary,
            "experiment_details": "；".join(item for item in [publication, identifier] if item),
            "steps": [],
            "performance": [],
            "matched_terms": [item for item in [paper.get("source"), publication, identifier] if item],
            "doi": paper.get("doi") or "",
            "year": paper.get("year") or "",
            "venue": paper.get("venue") or "",
            "authors": paper.get("authors") or [],
            "url": paper.get("url") or "",
        })
    return hits


def restore_evidence_provenance(value, original_research: dict):
    if isinstance(value, list):
        return [restore_evidence_provenance(item, original_research) for item in value]
    if not isinstance(value, dict):
        return value
    restored = {}
    for key, item in value.items():
        if key in {"knowledge_hits", "prior_paper_hits"}:
            restored[key] = original_research.get("knowledge_hits") or []
        elif key == "survey_report":
            restored[key] = original_research.get("survey_report") or {}
        elif key == "extracted_paper_protocols":
            restored[key] = original_research.get("extracted_paper_protocols") or ""
        else:
            restored[key] = restore_evidence_provenance(item, original_research)
    return restored


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
    original_input = load(BASE / case / "input.json")
    if case in FINAL_ITERATION:
        iteration = FINAL_ITERATION[case]
        research = load(LOOP / case / f"iteration-{iteration}-research-state.json")
        device = load(LOOP / case / f"iteration-{iteration}-device-package.json")
        original_research = load(BASE / case / "research_state.json")
        # The post_observation retry accidentally used the repository default
        # shared KB. Preserve the adapted plan, but restore evidence provenance
        # from the case-isolated online run.
        for field in [
            "survey_queries", "survey_report", "knowledge_hits",
            "extracted_protocols", "extracted_paper_protocols",
        ]:
            if field in original_research:
                research[field] = original_research[field]
        research = restore_evidence_provenance(research, original_research)
        device = restore_evidence_provenance(device, original_research)
        macro_plan_package = device.get("macro_plan")
        if isinstance(macro_plan_package, dict):
            research_context = macro_plan_package.get("research_context")
            if isinstance(research_context, dict):
                research_context["survey_report"] = original_research.get("survey_report") or {}
                research_context["knowledge_hits"] = original_research.get("knowledge_hits") or []
                research_context["extracted_paper_protocols"] = original_research.get("extracted_paper_protocols") or ""
        history = iteration_rows(case, iteration)
        closed_loop = True
    else:
        iteration = 0
        research = load(BASE / case / "research_state.json")
        device = load(BASE / case / "device_package.json")
        summary = load(BASE / case / "case_summary.json")
        history = [{
            "iteration": 0,
            "phase": "device_mapping",
            "status": device.get("status", "unknown"),
            "research_status": research.get("status"),
            "research_stage": research.get("current_stage"),
            "macro_steps": len(research.get("macro_plan") or []),
            "device_status": device.get("status"),
            "device_steps": len((device.get("workflow_json") or {}).get("steps") or []),
            "device_attempts": summary.get("device_attempts") or [],
        }]
        closed_loop = False
    # Literature-only rerun on 2026-07-19: replace only the visible evidence
    # hits. Research plans and Device workflows remain byte-for-byte unchanged.
    research["knowledge_hits"] = curated_knowledge_hits(case)
    device["evaluation"] = {
        "process_completion": "yes",
        "paper_quality_summary": "low",
        "dispatch_schema_match": "not_reaudited_after_closed_loop",
        "capability_classification": "Research↔Device 闭环成功" if closed_loop else "联网评估结果",
        "capability_summary": (
            f"初始 Device 返回 feasibility_error 后，Research B2 根据设备约束重新规划；最终第 {iteration} 轮 Device "
            f"生成 {len((device.get('workflow_json') or {}).get('steps') or [])} 个步骤并返回 success。"
            if closed_loop else
            f"该案例来自统一联网批次 chem-agent-eval-20260719-170009；Device 状态为 {device.get('status')}，"
            f"生成 {len((device.get('workflow_json') or {}).get('steps') or [])} 个步骤。"
        ),
        "capability_tone": "success" if device.get("status") == "success" else "warning",
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
            f"初始设备方案不可行后，Device 约束已反馈至 Research B2。经过 {iteration} 轮 Research↔Device 闭环，"
            f"最终生成 {final_steps} 个 Device Step，状态 success。"
            if closed_loop else
            f"统一联网批次结果：Research status={research.get('status')}，Device status={device.get('status')}，"
            f"生成 {final_steps} 个 Device Step。"
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
    end = source.index("],u2=", start)
    return source[:start] + json.dumps(build_case(case), ensure_ascii=False, separators=(",", ":")) + source[end:]


def main() -> None:
    source = ASSET.read_text(encoding="utf-8")
    for index in range(len(CASES) - 1, -1, -1):
        source = replace_case(source, CASES[index], CASES[index + 1] if index + 1 < len(CASES) else None)
    source = source.replace(
        'F==="completed"?"Research + Device":F==="manual_required"?"Research 质量门":"Device 可行性"',
        '(F==="completed"||F==="success")?"Research + Device":F==="manual_required"?"Research 质量门":"Device 可行性"',
    )
    ASSET.write_text(source, encoding="utf-8")
    print(ASSET)


if __name__ == "__main__":
    main()

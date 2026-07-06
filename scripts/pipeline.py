#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康行业AI落地诊断 - Pipeline 编排引擎
=======================================
对应 cognee 借鉴点：
  1. 三层API设计（顶层4函数 → 中层Task → 底层脚本）
  2. Pipeline + Task 任务编排架构
  3. 双记忆体系（session_state 会话状态 + 持久化存储）
  4. 真相子空间（data_validation 数据一致性校验）

顶层API（4个入口）：
  - run_full_diagnosis()  完整诊断流程
  - run_roi_only()        仅ROI测算
  - run_store_diagnose()  门店服务诊断
  - run_pitfall_check()   坑点排查

使用方式：
  python3 pipeline.py --input '{"action": "full_diagnosis", "company_info": {...}}'
  python3 pipeline.py --input input.json --output output.json
  python3 pipeline.py --self-test
"""

import json
import sys
import os
import argparse
import uuid
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

# 导入本体知识库
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ontology import (
    get_industry_config, get_score_conclusion, get_top_pitfalls,
    get_pitfalls_by_category, DATA_VALIDATION_RULES,
    ROADMAP_TEMPLATE, SCENARIO_BASELINE, DIMENSION_DEFS,
    get_ontology_summary
)


# ============================================================
# 状态枚举
# ============================================================
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    NEEDS_INPUT = "needs_input"


# ============================================================
# 会话状态（对应 cognee 双记忆体系）
# ============================================================
@dataclass
class SessionState:
    """诊断会话状态 - 支持持久化保存/加载（中断续答）"""
    session_id: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0
    current_task: str = "info_collection"
    task_statuses: Dict[str, str] = field(default_factory=dict)

    # 输入数据
    company_info: Dict[str, Any] = field(default_factory=dict)
    industry_type: str = "default"

    # 中间计算结果
    score_result: Dict[str, Any] = field(default_factory=dict)
    roi_result: Dict[str, Any] = field(default_factory=dict)
    scenario_result: Dict[str, Any] = field(default_factory=dict)
    validation_result: Dict[str, Any] = field(default_factory=dict)

    # 最终产出
    final_report: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "current_task": self.current_task,
            "task_statuses": self.task_statuses,
            "company_info": self.company_info,
            "industry_type": self.industry_type,
            "score_result": self.score_result,
            "roi_result": self.roi_result,
            "scenario_result": self.scenario_result,
            "validation_result": self.validation_result,
            "final_report": self.final_report,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SessionState':
        state = cls()
        for key, value in data.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state

    def save(self, filepath: str) -> str:
        """保存会话状态到文件"""
        self.updated_at = time.time()
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return filepath

    @classmethod
    def load(cls, filepath: str) -> 'SessionState':
        """从文件加载会话状态"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


# ============================================================
# Task 基类
# ============================================================
class BaseTask:
    """任务基类 - 对应 cognee 的 Task 抽象"""

    name: str = "base"
    label: str = "基础任务"
    description: str = ""
    dependencies: List[str] = []  # 依赖的前置任务

    def __init__(self, state: SessionState):
        self.state = state
        self.status = TaskStatus.PENDING

    def can_run(self) -> bool:
        """检查依赖是否满足"""
        for dep in self.dependencies:
            dep_status = self.state.task_statuses.get(dep, TaskStatus.PENDING.value)
            if dep_status not in [TaskStatus.COMPLETED.value, TaskStatus.SKIPPED.value]:
                return False
        return True

    def run(self) -> Dict[str, Any]:
        """执行任务，返回结果字典"""
        raise NotImplementedError

    def execute(self) -> Dict[str, Any]:
        """执行包装 - 状态管理"""
        if not self.can_run():
            self.status = TaskStatus.SKIPPED
            self.state.task_statuses[self.name] = self.status.value
            return {"status": "skipped", "reason": "dependencies not met"}

        self.status = TaskStatus.RUNNING
        self.state.task_statuses[self.name] = self.status.value
        self.state.current_task = self.name

        try:
            result = self.run()
            self.status = TaskStatus.COMPLETED
            self.state.task_statuses[self.name] = self.status.value
            self.state.updated_at = time.time()
            return {"status": "completed", "result": result}
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.state.task_statuses[self.name] = self.status.value
            return {"status": "failed", "error": str(e)}


# ============================================================
# 具体任务实现
# ============================================================

class DataValidationTask(BaseTask):
    """数据一致性校验 - 对应 cognee 真相子空间（truth_subspace）"""
    name = "data_validation"
    label = "数据合理性校验"
    description = "检查企业输入数据的合理性，发现矛盾或异常时提示确认"
    dependencies = []

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        issues = []
        passed = []

        for rule in DATA_VALIDATION_RULES:
            try:
                check = rule["check"]
                # 简单的表达式计算（安全范围内）
                val = None
                if "revenue" in check and "employee_count" in check:
                    if info.get("revenue") and info.get("employee_count"):
                        val = info["revenue"] / info["employee_count"]
                elif "store_count" in check and "employee_count" in check:
                    if info.get("store_count", 0) > 0 and info.get("employee_count"):
                        val = info["employee_count"] / info["store_count"]
                elif "customer_count" in check and "employee_count" in check:
                    if info.get("customer_count") and info.get("employee_count"):
                        val = info["customer_count"] / info["employee_count"]
                elif "it_budget" in check and "revenue" in check:
                    if info.get("it_budget") and info.get("revenue", 0) > 0:
                        val = info["it_budget"] / info["revenue"]

                if val is not None:
                    if val < rule["min"] or val > rule["max"]:
                        issues.append({
                            "rule": rule["rule"],
                            "value": round(val, 2),
                            "expected": f"{rule['min']}-{rule['max']} {rule['unit']}",
                            "severity": rule["severity"],
                            "suggestion": f"该指标{val:.2f}{rule['unit']}超出常规范围({rule['min']}-{rule['max']})，请确认数据准确性",
                        })
                    else:
                        passed.append(rule["rule"])
            except (ZeroDivisionError, KeyError, TypeError):
                pass  # 数据不全时跳过

        result = {
            "total_rules": len(DATA_VALIDATION_RULES),
            "passed": len(passed),
            "issues": len(issues),
            "issue_list": issues,
            "passed_list": passed,
            "overall": "warning" if issues else "passed",
        }
        self.state.validation_result = result
        return result


class ScoreCalculationTask(BaseTask):
    """五维度评分计算"""
    name = "score_calculation"
    label = "五维度AI落地评分"
    description = "根据企业信息计算5维度评分，按行业动态权重校准"
    dependencies = ["data_validation"]

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        industry = self.state.industry_type
        weights = get_industry_config(industry)

        # 简化评分逻辑（实际应调用 calculate_score.py 的完整逻辑）
        # 这里基于公司信息做快速估算
        dimension_scores = {}
        dim_factors = {
            "digital_base": ["it_system_count", "data_quality", "it_budget_ratio"],
            "resource_readiness": ["budget_amount", "it_headcount", "management_support"],
            "pain_urgency": ["labor_cost_ratio", "efficiency_bottleneck", "customer_churn"],
            "team_acceptance": ["avg_age", "learning_willingness", "change_resistance"],
            "compliance_risk": ["regulation_level", "data_sensitivity", "marketing_strictness"],
        }

        for dim, max_score in [(k, v["max_score"]) for k, v in DIMENSION_DEFS.items()]:
            # 简化：如果有对应数据用数据，否则用行业中位数
            raw_score = max_score * 0.6  # 默认基准分60%
            if dim == "digital_base" and info.get("it_system_count"):
                raw_score = min(max_score, info["it_system_count"] * max_score / 8)
            elif dim == "resource_readiness" and info.get("it_budget") and info.get("revenue"):
                ratio = info["it_budget"] / info["revenue"]
                raw_score = min(max_score, ratio * max_score / 0.05)
            elif dim == "pain_urgency" and info.get("labor_cost_ratio"):
                raw_score = min(max_score, info["labor_cost_ratio"] * max_score / 0.6)
            elif dim == "team_acceptance" and info.get("avg_age"):
                raw_score = max(0, max_score * (1 - (info["avg_age"] - 25) / 30))
            elif dim == "compliance_risk" and industry in ["medical", "experiential"]:
                raw_score = max_score * 0.8  # 高合规行业风险分高（分越高越需要重视）

            dimension_scores[dim] = {
                "raw_score": round(raw_score, 1),
                "max_score": DIMENSION_DEFS[dim]["max_score"],
                "weight": weights[dim],
                "weighted_score": round(raw_score * weights[dim], 2),
                "label": DIMENSION_DEFS[dim]["label"],
            }

        total_weighted = sum(d["weighted_score"] for d in dimension_scores.values())
        weight_values = {k: v for k, v in weights.items() if k != "label"}
        # 计算加权满分：sum(维度满分 * 维度权重)
        total_max = sum(DIMENSION_DEFS[dim]["max_score"] * weight_values[dim] for dim in DIMENSION_DEFS)
        total_percent = round(total_weighted / total_max * 100, 1) if total_max > 0 else 0

        conclusion = get_score_conclusion(total_percent)

        result = {
            "industry": industry,
            "industry_label": weights.get("label", "通用"),
            "dimension_scores": dimension_scores,
            "total_weighted": round(total_weighted, 2),
            "total_percent": total_percent,
            "level": conclusion["level"],
            "conclusion": conclusion["conclusion"],
            "action": conclusion["action"],
        }
        self.state.score_result = result
        return result


class ScenarioRecommendationTask(BaseTask):
    """场景推荐计算"""
    name = "scenario_recommendation"
    label = "AI落地场景推荐"
    description = "基于企业特征动态计算10大场景适配度，输出Top 3推荐"
    dependencies = ["score_calculation"]

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        industry = self.state.industry_type
        score = self.state.score_result

        scenario_scores = {}
        for sid, sdata in SCENARIO_BASELINE.items():
            # 基础适配分
            base = 60

            # 行业适配加分
            if "all" in sdata["fit_industries"] or industry in sdata["fit_industries"]:
                base += 15

            # 基于企业特征的调整
            if info.get("store_count", 0) > 5 and sid in ["store_monitor", "supply_chain"]:
                base += 15
            if info.get("customer_count", 0) > 1000 and sid in ["customer_service", "private_domain"]:
                base += 10
            if info.get("employee_count", 0) > 50 and sid in ["training_learning", "sales_assistant"]:
                base += 10
            if info.get("marketing_team", 0) > 5 and sid in ["content_marketing", "data_analysis"]:
                base += 10

            # 难度调整（评分低的企业推荐低难度场景）
            if score and score.get("total_percent", 60) < 60 and sdata["difficulty"] <= 2:
                base += 10
            if score and score.get("total_percent", 60) >= 80 and sdata["difficulty"] >= 3:
                base += 5

            scenario_scores[sid] = {
                **sdata,
                "id": sid,
                "fit_score": min(100, base),
            }

        # 按适配度排序
        sorted_scenarios = sorted(
            scenario_scores.values(),
            key=lambda x: x["fit_score"],
            reverse=True
        )

        result = {
            "total_scenarios": len(sorted_scenarios),
            "top3": sorted_scenarios[:3],
            "all_sorted": sorted_scenarios,
            "recommendation_basis": f"基于{industry}行业特征+企业规模+评分等级综合计算",
        }
        self.state.scenario_result = result
        return result


class ROICalculationTask(BaseTask):
    """ROI分析计算"""
    name = "roi_calculation"
    label = "ROI投资回报分析"
    description = "三档回本测算+隐性成本+策略对比"
    dependencies = ["scenario_recommendation"]

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        scenarios = self.state.scenario_result.get("top3", [])

        # 估算总投入和收益
        total_software_cost = sum(s.get("typical_cost_range", [3, 10])[1] for s in scenarios[:2])

        revenue = info.get("revenue", 1000)  # 万
        labor_cost_ratio = info.get("labor_cost_ratio", 0.3)
        labor_cost = revenue * labor_cost_ratio

        # 三档测算
        gears = []
        for gear_config in [
            {"name": "保守档", "saving_mult": 0.3, "cost_mult": 1.5},
            {"name": "基准档", "saving_mult": 0.5, "cost_mult": 1.0},
            {"name": "激进档", "saving_mult": 0.8, "cost_mult": 0.8},
        ]:
            annual_saving = labor_cost * 0.1 * gear_config["saving_mult"]  # 假设10%人力被优化
            total_cost = total_software_cost * gear_config["cost_mult"]
            hidden_cost = total_cost * 1.0  # 首年隐性成本1:1
            total_first_year = total_cost + hidden_cost

            payback_months = round(total_first_year / (annual_saving / 12), 1) if annual_saving > 0 else 99

            gears.append({
                "gear": gear_config["name"],
                "software_cost": round(total_software_cost, 1),
                "hidden_cost": round(hidden_cost, 1),
                "total_first_year": round(total_first_year, 1),
                "annual_saving": round(annual_saving, 1),
                "payback_months": payback_months,
                "roi_3year": round((annual_saving * 3 - total_first_year) / total_first_year * 100, 1) if total_first_year > 0 else 0,
            })

        result = {
            "base_assumptions": {
                "annual_revenue": revenue,
                "labor_cost_ratio": labor_cost_ratio,
                "annual_labor_cost": round(labor_cost, 1),
                "selected_scenarios": [s["label"] for s in scenarios[:2]],
            },
            "gears": gears,
            "conclusion": self._get_roi_conclusion(gears),
        }
        self.state.roi_result = result
        return result

    def _get_roi_conclusion(self, gears: List[Dict]) -> str:
        baseline = next((g for g in gears if g["gear"] == "基准档"), gears[1])
        if baseline["payback_months"] <= 6:
            return f"回报周期极短（{baseline['payback_months']}个月），强烈推荐立即启动"
        elif baseline["payback_months"] <= 12:
            return f"回报周期合理（{baseline['payback_months']}个月），建议尽快启动"
        elif baseline["payback_months"] <= 24:
            return f"回报周期中等（{baseline['payback_months']}个月），建议试点验证后推广"
        else:
            return f"回报周期较长（{baseline['payback_months']}个月），建议降低投入或延后"


class RoadmapTask(BaseTask):
    """路线图生成"""
    name = "roadmap_generation"
    label = "三阶段落地路线图"
    description = "根据企业情况生成定制化的三阶段落地路线图"
    dependencies = ["roi_calculation"]

    def run(self) -> Dict[str, Any]:
        score = self.state.score_result
        scenarios = self.state.scenario_result.get("top3", [])

        level = score.get("level", "B") if score else "B"

        # 根据等级调整节奏
        pace_map = {
            "S": {"mult": 1.2, "note": "基础好，可加速推进"},
            "A": {"mult": 1.0, "note": "正常节奏推进"},
            "B": {"mult": 0.8, "note": "适当放缓，先补基础"},
            "C": {"mult": 0.6, "note": "从低成本工具入手"},
            "D": {"mult": 0.4, "note": "先做数字化基础建设"},
        }
        pace = pace_map.get(level, pace_map["B"])

        roadmap = {}
        for phase_key, phase_data in ROADMAP_TEMPLATE.items():
            adjusted_budget = [
                round(b * pace["mult"], 0) for b in phase_data["budget_range"]
            ]
            roadmap[phase_key] = {
                **phase_data,
                "adjusted_budget_range": adjusted_budget,
                "priority_scenarios": [s["label"] for s in scenarios[:2]] if phase_key == "phase1" else [],
            }

        result = {
            "level": level,
            "pace_note": pace["note"],
            "phases": roadmap,
        }
        return result


class PitfallCheckTask(BaseTask):
    """坑点排查 - 可独立运行"""
    name = "pitfall_check"
    label = "落地坑点排查"
    description = "根据企业特征匹配最可能踩的坑，提前预警"
    dependencies = []

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        industry = self.state.industry_type

        # 基于企业特征匹配相关坑点
        relevant_pitfalls = []
        all_pitfalls = get_top_pitfalls(25)

        for pitfall in all_pitfalls:
            relevance = 0

            # 行业相关
            if pitfall["category"] == "合规" and industry in ["medical", "experiential", "chain_store"]:
                relevance += 30
            if pitfall["category"] == "数据" and info.get("customer_count", 0) > 500:
                relevance += 20
            if pitfall["category"] == "组织" and info.get("employee_count", 0) > 20:
                relevance += 20
            if pitfall["category"] == "内容" and info.get("marketing_team", 0) > 3:
                relevance += 15
            if pitfall["category"] == "成本" and info.get("it_budget", 0) > 0:
                relevance += 10

            # 严重程度基础分
            severity_score = {"critical": 30, "high": 20, "medium": 10, "low": 5}
            relevance += severity_score.get(pitfall["severity"], 5)

            relevant_pitfalls.append({
                **pitfall,
                "relevance_score": relevance,
            })

        relevant_pitfalls.sort(key=lambda x: x["relevance_score"], reverse=True)

        result = {
            "total_pitfalls": len(relevant_pitfalls),
            "top10": relevant_pitfalls[:10],
            "by_category": {
                cat: [p for p in relevant_pitfalls if p["category"] == cat][:3]
                for cat in ["合规", "组织", "数据", "成本", "内容", "技术"]
            },
            "most_critical": relevant_pitfalls[:3],
        }
        return result


# ============================================================
# Pipeline 引擎
# ============================================================
class DiagnosisPipeline:
    """诊断流水线 - 对应 cognee 的 Pipeline 编排"""

    TASK_CLASSES = {
        "data_validation": DataValidationTask,
        "score_calculation": ScoreCalculationTask,
        "scenario_recommendation": ScenarioRecommendationTask,
        "roi_calculation": ROICalculationTask,
        "roadmap_generation": RoadmapTask,
        "pitfall_check": PitfallCheckTask,
    }

    FULL_DIAGNOSIS_FLOW = [
        "data_validation",
        "score_calculation",
        "scenario_recommendation",
        "roi_calculation",
        "roadmap_generation",
    ]

    def __init__(self, state: Optional[SessionState] = None):
        self.state = state or SessionState()
        if not self.state.session_id:
            self.state.session_id = str(uuid.uuid4())
            self.state.created_at = time.time()

    def run_task(self, task_name: str) -> Dict[str, Any]:
        """执行单个任务"""
        if task_name not in self.TASK_CLASSES:
            return {"status": "failed", "error": f"Unknown task: {task_name}"}

        task_class = self.TASK_CLASSES[task_name]
        task = task_class(self.state)
        return task.execute()

    def run_flow(self, task_names: List[str]) -> Dict[str, Any]:
        """执行一组任务（按顺序，自动处理依赖）"""
        results = {}
        for task_name in task_names:
            result = self.run_task(task_name)
            results[task_name] = result
            if result["status"] == "failed":
                break
        return {
            "session_id": self.state.session_id,
            "total_tasks": len(task_names),
            "completed": sum(1 for r in results.values() if r["status"] == "completed"),
            "failed": sum(1 for r in results.values() if r["status"] == "failed"),
            "skipped": sum(1 for r in results.values() if r["status"] == "skipped"),
            "task_results": results,
            "state_summary": self._get_state_summary(),
        }

    def _get_state_summary(self) -> Dict[str, Any]:
        return {
            "current_task": self.state.current_task,
            "task_statuses": self.state.task_statuses,
            "has_score": bool(self.state.score_result),
            "has_roi": bool(self.state.roi_result),
            "has_scenarios": bool(self.state.scenario_result),
            "validation_issues": len(self.state.validation_result.get("issue_list", [])) if self.state.validation_result else 0,
        }


# ============================================================
# 顶层 API（对应 cognee 顶层4函数设计）
# ============================================================

def run_full_diagnosis(company_info: Dict, industry_type: str = "default",
                       save_path: Optional[str] = None) -> Dict[str, Any]:
    """
    【顶层API 1/4】完整诊断流程
    输入企业信息 → 数据校验 → 评分 → 场景推荐 → ROI → 路线图
    """
    state = SessionState(
        company_info=company_info,
        industry_type=industry_type,
    )
    pipeline = DiagnosisPipeline(state)
    result = pipeline.run_flow(DiagnosisPipeline.FULL_DIAGNOSIS_FLOW)

    if save_path:
        state.save(save_path)
        result["save_path"] = save_path

    return result


def run_roi_only(company_info: Dict, industry_type: str = "default",
                 scenarios: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    【顶层API 2/4】仅ROI测算
    快速计算投资回报，不需要完整诊断
    """
    state = SessionState(
        company_info=company_info,
        industry_type=industry_type,
    )
    # 先快速跑评分和场景，再算ROI
    pipeline = DiagnosisPipeline(state)
    result = pipeline.run_flow([
        "data_validation",
        "score_calculation",
        "scenario_recommendation",
        "roi_calculation",
    ])
    return result


def run_store_diagnose(store_info: Dict) -> Dict[str, Any]:
    """
    【顶层API 3/4】门店服务诊断
    专门针对连锁门店的服务质量诊断
    """
    # 复用评分+坑点，但针对门店场景加权
    company_info = {
        **store_info,
        "store_count": store_info.get("store_count", 1),
    }
    state = SessionState(
        company_info=company_info,
        industry_type="chain_store",
    )
    pipeline = DiagnosisPipeline(state)
    result = pipeline.run_flow([
        "data_validation",
        "score_calculation",
        "scenario_recommendation",
        "pitfall_check",
    ])
    # 门店相关场景优先
    if state.scenario_result:
        store_scenarios = [s for s in state.scenario_result.get("all_sorted", [])
                          if s["id"] in ["store_monitor", "quality_control", "training_learning"]]
        result["store_focus"] = {
            "key_scenarios": store_scenarios[:3],
            "focus_areas": ["服务质量监控", "合规风控", "员工培训"],
        }
    return result


def run_pitfall_check(company_info: Dict, industry_type: str = "default",
                      top_n: int = 10) -> Dict[str, Any]:
    """
    【顶层API 4/4】坑点排查
    快速评估企业AI落地最可能踩的坑
    """
    state = SessionState(
        company_info=company_info,
        industry_type=industry_type,
    )
    pipeline = DiagnosisPipeline(state)
    result = pipeline.run_task("pitfall_check")
    return result


def resume_diagnosis(save_path: str, next_task: Optional[str] = None) -> Dict[str, Any]:
    """
    【状态恢复】从保存的会话状态继续诊断
    对应 cognee 双记忆体系中的持久化记忆
    """
    state = SessionState.load(save_path)
    pipeline = DiagnosisPipeline(state)

    if next_task:
        result = pipeline.run_task(next_task)
    else:
        # 找第一个未完成的任务继续
        pending = [t for t in DiagnosisPipeline.FULL_DIAGNOSIS_FLOW
                   if state.task_statuses.get(t, "pending") == "pending"]
        if pending:
            result = pipeline.run_flow(pending)
        else:
            result = {"status": "completed", "message": "所有任务已完成"}

    state.save(save_path)
    return result


# ============================================================
# 命令行入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="健康行业AI诊断Pipeline引擎")
    parser.add_argument("--input", "-i", help="输入JSON文件路径或JSON字符串")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    parser.add_argument("--action", choices=["full", "roi", "store", "pitfall", "resume"],
                        default="full", help="执行动作")
    parser.add_argument("--save", help="会话状态保存路径")
    parser.add_argument("--resume-from", help="从指定状态文件恢复")
    args = parser.parse_args()

    if args.self_test:
        _run_self_test()
        return

    # 解析输入
    input_data = {}
    if args.input:
        if os.path.isfile(args.input):
            with open(args.input, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        else:
            input_data = json.loads(args.input)

    company_info = input_data.get("company_info", input_data)
    industry = input_data.get("industry_type", "default")

    # 选择动作
    if args.resume_from:
        result = resume_diagnosis(args.resume_from)
    elif args.action == "full":
        result = run_full_diagnosis(company_info, industry, args.save)
    elif args.action == "roi":
        result = run_roi_only(company_info, industry)
    elif args.action == "store":
        result = run_store_diagnose(company_info)
    elif args.action == "pitfall":
        result = run_pitfall_check(company_info, industry)
    else:
        result = {"error": "Unknown action"}

    # 输出
    output_json = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"结果已保存到: {args.output}")
    else:
        print(output_json)


def _run_self_test():
    """自测 - 验证4个顶层API都能跑通"""
    print("=" * 60)
    print("健康行业AI诊断 Pipeline 引擎 - 自测")
    print("=" * 60)

    test_company = {
        "company_name": "康源健康测试公司",
        "revenue": 2000,  # 万/年
        "employee_count": 80,
        "store_count": 12,
        "customer_count": 5000,
        "it_budget": 30,  # 万/年
        "labor_cost_ratio": 0.35,
        "marketing_team": 6,
    }

    ontology_summary = get_ontology_summary()
    print(f"\n✓ 本体知识库: {ontology_summary['industries']}行业 / {ontology_summary['scenarios']}场景 / {ontology_summary['pitfalls']}坑点")

    # 测试1: 坑点排查（最快）
    print("\n[1/4] 测试 pitfall_check...")
    r1 = run_pitfall_check(test_company, "chain_store")
    assert r1["status"] == "completed"
    assert len(r1["result"]["top10"]) == 10
    print(f"  ✓ 坑点排查通过, Top1: {r1['result']['top10'][0]['title']}")

    # 测试2: ROI测算
    print("\n[2/4] 测试 roi_only...")
    r2 = run_roi_only(test_company, "chain_store")
    assert r2["completed"] >= 3
    assert "gears" in r2["task_results"]["roi_calculation"]["result"]
    baseline = next(g for g in r2["task_results"]["roi_calculation"]["result"]["gears"] if g["gear"] == "基准档")
    print(f"  ✓ ROI测算通过, 基准档回本: {baseline['payback_months']}个月")

    # 测试3: 门店诊断
    print("\n[3/4] 测试 store_diagnose...")
    r3 = run_store_diagnose(test_company)
    assert r3["completed"] >= 3
    print(f"  ✓ 门店诊断通过, 评分等级: {r3['task_results']['score_calculation']['result']['level']}")

    # 测试4: 完整诊断 + 状态持久化
    print("\n[4/4] 测试 full_diagnosis + 状态持久化...")
    save_path = "/tmp/test_diagnosis_state.json"
    r4 = run_full_diagnosis(test_company, "chain_store", save_path)
    assert r4["completed"] == 5
    assert os.path.exists(save_path)
    print(f"  ✓ 完整诊断通过, 5个任务全部完成")
    print(f"  ✓ 状态持久化通过, 保存到: {save_path}")

    # 测试5: 状态恢复
    print("\n[额外] 测试状态恢复...")
    resumed = resume_diagnosis(save_path)
    assert resumed["status"] == "completed"
    print(f"  ✓ 状态恢复通过")

    # 清理
    os.remove(save_path)

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！Pipeline 引擎运行正常")
    print("=" * 60)
    print("\n顶层API清单：")
    print("  1. run_full_diagnosis()    - 完整诊断（6步流程）")
    print("  2. run_roi_only()          - 仅ROI测算")
    print("  3. run_store_diagnose()    - 门店服务诊断")
    print("  4. run_pitfall_check()     - 坑点排查")
    print("  5. resume_diagnosis()      - 中断续答")


if __name__ == "__main__":
    main()

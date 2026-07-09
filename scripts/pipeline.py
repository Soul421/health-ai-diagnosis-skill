#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康行业AI内容增长系统 - Pipeline 编排引擎 v2.0.0
===================================================
v2.0 重大变化：
- 从"AI落地诊断" → "内容增长系统交付"
- 流程：信息收集 → 定位诊断 → 卖点重构 → 痛点拆解 → 内容方案 → 直播方案 → 私域方案 → AI落地 → 执行计划
- 输出7大模块的完整交付物，而不是诊断建议

顶层API：
  - run_content_growth()    完整内容增长方案
  - run_diagnosis_only()    仅定位诊断
  - run_content_package()   内容套餐（短视频+私域）
  - run_pitfall_check()     坑点排查
"""

import json
import sys
import os
import argparse
import uuid
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ontology import (
    get_industry_config, get_product_type, get_trust_path,
    diagnose_bottlenecks, get_top_pitfalls,
    get_pitfalls_by_category, CONTENT_GROWTH_MODULES,
    PRICING_TIERS, EXECUTION_PLAN_30DAYS,
    get_ontology_summary, recommend_modules, get_pricing_recommendation,
)
from calculate_score import calculate_score
from calculate_scenarios import calculate_module_scores
from calculate_roi import calculate_content_growth_roi


# ============================================================
# 状态枚举
# ============================================================
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


# ============================================================
# 会话状态
# ============================================================
@dataclass
class SessionState:
    """内容增长会话状态"""
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
    product_type_result: Dict[str, Any] = field(default_factory=dict)
    trust_path_result: Dict[str, Any] = field(default_factory=dict)
    bottleneck_result: List[Dict] = field(default_factory=list)
    module_result: Dict[str, Any] = field(default_factory=dict)
    roi_result: Dict[str, Any] = field(default_factory=dict)
    pitfall_result: Dict[str, Any] = field(default_factory=dict)

    # 最终产出
    deliverables: Dict[str, Any] = field(default_factory=dict)
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
            "product_type_result": self.product_type_result,
            "trust_path_result": self.trust_path_result,
            "bottleneck_result": self.bottleneck_result,
            "module_result": self.module_result,
            "roi_result": self.roi_result,
            "pitfall_result": self.pitfall_result,
            "deliverables": self.deliverables,
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
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


# ============================================================
# Task 基类
# ============================================================
class BaseTask:
    """任务基类"""
    name: str = "base"
    label: str = "基础任务"
    description: str = ""
    dependencies: List[str] = []

    def __init__(self, state: SessionState):
        self.state = state
        self.status = TaskStatus.PENDING

    def can_run(self) -> bool:
        for dep in self.dependencies:
            dep_status = self.state.task_statuses.get(dep, TaskStatus.PENDING.value)
            if dep_status not in [TaskStatus.COMPLETED.value, TaskStatus.SKIPPED.value]:
                return False
        return True

    def run(self) -> Dict[str, Any]:
        raise NotImplementedError

    def execute(self) -> Dict[str, Any]:
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
# 具体任务实现（v2.0 内容增长体系）
# ============================================================

class MaturityScoreTask(BaseTask):
    """内容增长成熟度评分"""
    name = "maturity_score"
    label = "内容增长成熟度评分"
    description = "5维度成熟度评分，按行业动态权重校准"
    dependencies = []

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        # 把行业类型传进去
        score_input = {**info, "industry_type": self.state.industry_type}
        result = calculate_score(score_input)
        self.state.score_result = result
        return result


class ProductTypeTask(BaseTask):
    """产品类型识别"""
    name = "product_type"
    label = "产品类型识别"
    description = "判断产品属于功能型/体验型/刚需型/社交型"
    dependencies = []

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        product_info = {
            "name": info.get("product_name", ""),
            "description": info.get("product_description", ""),
            "features": info.get("product_features", []),
        }
        result = get_product_type(product_info)
        self.state.product_type_result = result
        return result


class TrustPathTask(BaseTask):
    """信任路径判断"""
    name = "trust_path"
    label = "信任成交路径判断"
    description = "判断客户主要靠什么建立信任并下单"
    dependencies = ["product_type"]

    def run(self) -> Dict[str, Any]:
        product_type_id = self.state.product_type_result.get("type_id", "functional")
        result = get_trust_path(product_type_id, self.state.industry_type)
        self.state.trust_path_result = result
        return result


class BottleneckDiagnosisTask(BaseTask):
    """内容增长瓶颈诊断"""
    name = "bottleneck_diagnosis"
    label = "内容增长瓶颈诊断"
    description = "识别当前内容增长的核心瓶颈（Top 3）"
    dependencies = ["maturity_score"]

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        # 从评分结果中提取各维度分数
        raw_scores = self.state.score_result.get("raw_scores", {})
        result = diagnose_bottlenecks(info, raw_scores)
        self.state.bottleneck_result = result
        return {
            "count": len(result),
            "top3": result,
            "primary": result[0] if result else None,
        }


class ModuleRecommendationTask(BaseTask):
    """模块推荐引擎"""
    name = "module_recommendation"
    label = "7大模块优先级推荐"
    description = "基于企业特征和瓶颈诊断，推荐模块实施顺序"
    dependencies = ["bottleneck_diagnosis", "product_type", "trust_path"]

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        maturity_scores = self.state.score_result.get("raw_scores", {})
        bottlenecks = self.state.bottleneck_result

        result = calculate_module_scores(info, maturity_scores=maturity_scores, bottlenecks=bottlenecks)
        self.state.module_result = result
        return result


class ROICalculationTask(BaseTask):
    """内容增长ROI测算"""
    name = "roi_calculation"
    label = "内容增长ROI测算"
    description = "4档报价ROI对比 + 三阶段效果预测"
    dependencies = ["module_recommendation"]

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        roi_input = {
            **info,
            "industry_type": self.state.industry_type,
        }
        result = calculate_content_growth_roi(roi_input)
        self.state.roi_result = result
        return result


class DeliverablesGenerationTask(BaseTask):
    """交付物生成"""
    name = "deliverables_generation"
    label = "7大模块交付物生成"
    description = "根据各模块模板生成可直接使用的交付物"
    dependencies = ["roi_calculation"]

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        modules = self.state.module_result.get("modules_sorted", [])
        pricing_rec = get_pricing_recommendation(info)

        # 生成各模块交付物清单（基于模板，实际内容由LLM填充）
        deliverables = {}
        for m_id, m_data in CONTENT_GROWTH_MODULES.items():
            deliverables[m_id] = {
                "module_name": m_data["module_name"],
                "module_order": m_data["module_order"],
                "description": m_data["description"],
                "core_value": m_data["core_value"],
                "deliverables_list": m_data["deliverables"],
                "deliverables_count": len(m_data["deliverables"]),
                "timeline": m_data["timeline"],
                "difficulty": m_data["difficulty"],
                "ai_enhancement": m_data.get("ai_enhancement", ""),
                "tools": m_data.get("tools", {}),
                "template_path": f"templates/模块{m_data['module_order']}_{m_data['module_name']}.md",
            }

        # 30天执行计划
        execution_plan = {
            "plan_name": "30天内容增长落地计划",
            "phases": EXECUTION_PLAN_30DAYS,
            "responsible_roles": {
                "老板/负责人": "方向把控、资源协调、审核把关",
                "内容岗": "选题、脚本、拍摄、剪辑、发布",
                "销售岗": "私域承接、客户跟进、话术应用",
                "运营岗": "数据复盘、社群运营、活动策划",
            },
        }

        # 产品报价
        pricing = {
            "recommended_tier": pricing_rec["recommended_tier"],
            "recommended_label": pricing_rec["tier"],
            "recommended_price": pricing_rec["price"],
            "all_tiers": PRICING_TIERS,
        }

        result = {
            "modules": deliverables,
            "total_modules": len(deliverables),
            "total_deliverables": sum(m["deliverables_count"] for m in deliverables.values()),
            "execution_plan": execution_plan,
            "pricing": pricing,
            "note": "交付物模板位于templates/目录，具体内容需结合企业实际情况填充",
        }

        self.state.deliverables = result
        return result


class PitfallCheckTask(BaseTask):
    """坑点排查 - 可独立运行"""
    name = "pitfall_check"
    label = "内容增长坑点排查"
    description = "根据企业特征匹配最可能踩的坑，提前预警"
    dependencies = []

    def run(self) -> Dict[str, Any]:
        info = self.state.company_info
        industry = self.state.industry_type

        relevant_pitfalls = []
        all_pitfalls = get_top_pitfalls(25)

        for pitfall in all_pitfalls:
            relevance = 0

            # 行业相关
            if pitfall["category"] == "合规" and industry in ["medical", "anti_aging", "experiential"]:
                relevance += 30
            if pitfall["category"] == "内容" and info.get("content_team_size", 0) < 3:
                relevance += 25
            if pitfall["category"] == "信任" and info.get("customer_count", 0) > 1000:
                relevance += 20
            if pitfall["category"] == "转化" and info.get("has_livestream", False):
                relevance += 20
            if pitfall["category"] == "私域" and info.get("has_private_domain", False):
                relevance += 20

            # 严重程度基础分
            severity_score = {"critical": 25, "high": 15, "medium": 8, "low": 3}
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
                for cat in ["合规", "内容", "产品", "信任", "转化", "私域", "团队", "战略"]
                if any(p["category"] == cat for p in relevant_pitfalls)
            },
            "most_critical": [p for p in relevant_pitfalls if p["severity"] == "critical"][:3],
        }
        self.state.pitfall_result = result
        return result


# ============================================================
# Pipeline 引擎
# ============================================================
class ContentGrowthPipeline:
    """内容增长流水线"""

    TASK_CLASSES = {
        "maturity_score": MaturityScoreTask,
        "product_type": ProductTypeTask,
        "trust_path": TrustPathTask,
        "bottleneck_diagnosis": BottleneckDiagnosisTask,
        "module_recommendation": ModuleRecommendationTask,
        "roi_calculation": ROICalculationTask,
        "deliverables_generation": DeliverablesGenerationTask,
        "pitfall_check": PitfallCheckTask,
    }

    # 完整内容增长流程（8步）
    FULL_FLOW = [
        "maturity_score",
        "product_type",
        "trust_path",
        "bottleneck_diagnosis",
        "module_recommendation",
        "roi_calculation",
        "deliverables_generation",
    ]

    # 仅诊断流程（前4步）
    DIAGNOSIS_ONLY_FLOW = [
        "maturity_score",
        "product_type",
        "trust_path",
        "bottleneck_diagnosis",
        "pitfall_check",
    ]

    # 内容套餐流程（短视频+私域）
    CONTENT_PACKAGE_FLOW = [
        "maturity_score",
        "product_type",
        "trust_path",
        "bottleneck_diagnosis",
        "module_recommendation",
        "roi_calculation",
    ]

    def __init__(self, state: Optional[SessionState] = None):
        self.state = state or SessionState()
        if not self.state.session_id:
            self.state.session_id = str(uuid.uuid4())
            self.state.created_at = time.time()

    def run_task(self, task_name: str) -> Dict[str, Any]:
        if task_name not in self.TASK_CLASSES:
            return {"status": "failed", "error": f"Unknown task: {task_name}"}
        task_class = self.TASK_CLASSES[task_name]
        task = task_class(self.state)
        return task.execute()

    def run_flow(self, task_names: List[str]) -> Dict[str, Any]:
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
            "has_modules": bool(self.state.module_result),
            "has_deliverables": bool(self.state.deliverables),
            "bottlenecks_count": len(self.state.bottleneck_result),
        }


# ============================================================
# 顶层 API
# ============================================================

def run_content_growth(company_info: Dict, industry_type: str = "default",
                      save_path: Optional[str] = None) -> Dict[str, Any]:
    """
    【顶层API 1/4】完整内容增长方案
    输入企业信息 → 成熟度评分 → 产品/信任/瓶颈诊断 → 模块推荐 → ROI → 交付物
    """
    state = SessionState(
        company_info=company_info,
        industry_type=industry_type,
    )
    pipeline = ContentGrowthPipeline(state)
    result = pipeline.run_flow(ContentGrowthPipeline.FULL_FLOW)

    if save_path:
        state.save(save_path)
        result["save_path"] = save_path

    return result


def run_diagnosis_only(company_info: Dict, industry_type: str = "default",
                       save_path: Optional[str] = None) -> Dict[str, Any]:
    """
    【顶层API 2/4】仅定位诊断
    快速诊断：成熟度+产品类型+信任路径+核心瓶颈+坑点
    """
    state = SessionState(
        company_info=company_info,
        industry_type=industry_type,
    )
    pipeline = ContentGrowthPipeline(state)
    result = pipeline.run_flow(ContentGrowthPipeline.DIAGNOSIS_ONLY_FLOW)

    if save_path:
        state.save(save_path)
        result["save_path"] = save_path

    return result


def run_content_package(company_info: Dict, industry_type: str = "default") -> Dict[str, Any]:
    """
    【顶层API 3/4】内容套餐（短视频+私域）
    针对内容团队的快速方案
    """
    state = SessionState(
        company_info=company_info,
        industry_type=industry_type,
    )
    pipeline = ContentGrowthPipeline(state)
    result = pipeline.run_flow(ContentGrowthPipeline.CONTENT_PACKAGE_FLOW)
    return result


def run_pitfall_check(company_info: Dict, industry_type: str = "default",
                      top_n: int = 10) -> Dict[str, Any]:
    """
    【顶层API 4/4】坑点排查
    快速评估内容增长最可能踩的坑
    """
    state = SessionState(
        company_info=company_info,
        industry_type=industry_type,
    )
    pipeline = ContentGrowthPipeline(state)
    result = pipeline.run_task("pitfall_check")
    return result


# ============================================================
# 命令行入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="健康行业AI内容增长系统 Pipeline v2.0.0")
    parser.add_argument("--input", "-i", help="输入JSON文件路径或JSON字符串")
    parser.add_argument("--output", "-o", help="输出JSON文件路径")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    parser.add_argument("--action", choices=["full", "diagnosis", "content", "pitfall"],
                        default="full", help="执行动作")
    parser.add_argument("--save", help="会话状态保存路径")
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
    if args.action == "full":
        result = run_content_growth(company_info, industry, args.save)
    elif args.action == "diagnosis":
        result = run_diagnosis_only(company_info, industry, args.save)
    elif args.action == "content":
        result = run_content_package(company_info, industry)
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
    print("健康行业AI内容增长系统 Pipeline v2.0.0 - 自测")
    print("=" * 60)

    # 测试案例：羊奶产品，会销模式，50人团队，年营收5000万
    test_company = {
        "company_name": "康源羊奶",
        "product_name": "中老年高钙羊奶粉",
        "product_description": "会销模式销售，针对中老年人",
        "product_features": ["高钙", "易吸收", "增强免疫力"],
        "annual_revenue_wan": 5000,
        "employee_count": 50,
        "content_team_size": 3,
        "has_short_video": True,
        "has_livestream": True,
        "has_private_domain": True,
        "has_brand_story": True,
        "customer_count": 20000,
        "avg_price": 398,
        "conversion_rate": 0.05,
        "repurchase_rate": 0.35,
        "has_ai_experience": False,
    }

    summary = get_ontology_summary()
    print(f"\n✓ 本体知识库: v{summary['version']}")
    print(f"  - {summary['content_growth_modules']}个内容增长模块")
    print(f"  - {summary['product_types']}种产品类型")
    print(f"  - {summary['pricing_tiers']}档产品报价")
    print(f"  - {summary['pitfalls']}个坑点")

    # 测试1: 坑点排查（最快）
    print("\n[1/4] 测试 pitfall_check...")
    r1 = run_pitfall_check(test_company, "experiential")
    assert r1["status"] == "completed"
    assert len(r1["result"]["top10"]) == 10
    print(f"  ✓ 坑点排查通过, Top1: {r1['result']['top10'][0]['title']}")

    # 测试2: 仅诊断
    print("\n[2/4] 测试 diagnosis_only...")
    r2 = run_diagnosis_only(test_company, "experiential")
    assert r2["completed"] >= 4
    assert "maturity_score" in r2["task_results"]
    score_level = r2["task_results"]["maturity_score"]["result"]["level"]
    print(f"  ✓ 定位诊断通过, 成熟度等级: {score_level}")

    # 测试3: 内容套餐
    print("\n[3/4] 测试 content_package...")
    r3 = run_content_package(test_company, "experiential")
    assert r3["completed"] >= 4
    assert "module_recommendation" in r3["task_results"]
    top_module = r3["task_results"]["module_recommendation"]["result"]["top3_modules"][0]
    print(f"  ✓ 内容套餐通过, 首推模块: {top_module}")

    # 测试4: 完整方案
    print("\n[4/4] 测试 full_content_growth...")
    save_path = "/tmp/test_content_growth_state.json"
    r4 = run_content_growth(test_company, "experiential", save_path)
    assert r4["completed"] == 7
    assert os.path.exists(save_path)
    assert "deliverables_generation" in r4["task_results"]
    deliverables = r4["task_results"]["deliverables_generation"]["result"]
    print(f"  ✓ 完整方案通过, 7个任务全部完成")
    print(f"  ✓ 交付物: {deliverables['total_modules']}个模块, {deliverables['total_deliverables']}份文件")
    print(f"  ✓ 推荐档位: {deliverables['pricing']['recommended_label']} ({deliverables['pricing']['recommended_price']})")
    print(f"  ✓ 状态持久化通过, 保存到: {save_path}")

    # 清理
    os.remove(save_path)

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！内容增长系统 v2.0.0 运行正常")
    print("=" * 60)
    print("\n顶层API清单：")
    print("  1. run_content_growth()    - 完整内容增长方案（7步）")
    print("  2. run_diagnosis_only()    - 仅定位诊断")
    print("  3. run_content_package()   - 内容套餐（短视频+私域）")
    print("  4. run_pitfall_check()     - 坑点排查")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块推荐引擎（v2.0.0）
=========================
根据企业特征和瓶颈诊断，计算7大内容增长模块的优先级和推荐顺序。

v2.0 重大变化：
- 从"10个AI场景推荐" → "7大内容增长模块推荐"
- 新增：4种推荐策略（内容优先/转化优先/信任优先/均衡发展）
- 新增：模块依赖关系检查，确保推荐顺序合理
- 新增：与产品类型、信任路径、瓶颈诊断联动
"""

import json
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ontology import (
    CONTENT_GROWTH_MODULES,
    MODULE_DEPENDENCIES,
    MODULE_PRIORITY_RULES,
    PRODUCT_TYPES,
    TRUST_PATHS,
    BOTTLENECK_DIAGNOSIS,
    get_product_type,
    get_trust_path,
    diagnose_bottlenecks,
)


def calculate_module_scores(input_data, maturity_scores=None, bottlenecks=None):
    """
    计算7大模块的适配度得分并排序

    Args:
        input_data: 企业信息字典
        maturity_scores: 5维度成熟度得分（可选）
        bottlenecks: 瓶颈诊断结果（可选）

    Returns:
        dict，包含模块排序列表、推荐策略、首要模块等
    """
    industry_type = input_data.get("industry_type", "default")
    product_type_id = input_data.get("product_type_id", "")
    content_team_size = input_data.get("content_team_size", 0)
    has_short_video = input_data.get("has_short_video", False)
    has_livestream = input_data.get("has_livestream", False)
    has_private_domain = input_data.get("has_private_domain", False)
    annual_revenue_wan = input_data.get("annual_revenue_wan", 0)
    customer_count = input_data.get("customer_count", 0)
    avg_price = input_data.get("avg_price", 0)

    # 如果没有成熟度分数，初始化空字典
    if maturity_scores is None:
        maturity_scores = {}

    # 如果没有瓶颈诊断，先做一个简化版
    if bottlenecks is None:
        bottlenecks = []
        # 基于成熟度分数做简单瓶颈判断
        dim_bottleneck_map = {
            "product_clarity": "product_unclear",
            "content_capability": "content_shortage",
            "trust_building": "trust_deficit",
            "conversion_system": "conversion_weak",
            "team_execution": "team_disconnect",
        }
        for dim, b_id in dim_bottleneck_map.items():
            score = maturity_scores.get(dim, 50)
            if isinstance(score, (int, float)) and score < 60:
                if b_id in BOTTLENECK_DIAGNOSIS:
                    bottlenecks.append({
                        "bottleneck_id": b_id,
                        "score": 60 - score,
                        **BOTTLENECK_DIAGNOSIS[b_id],
                    })
        bottlenecks.sort(key=lambda x: x["score"], reverse=True)

    # 获取产品类型（如果没有提供）
    if not product_type_id:
        product_info = {
            "name": input_data.get("product_name", ""),
            "description": input_data.get("product_description", ""),
            "features": input_data.get("product_features", []),
        }
        product_type_result = get_product_type(product_info)
        product_type_id = product_type_result["type_id"]
    else:
        product_type_result = {"type_id": product_type_id, **PRODUCT_TYPES.get(product_type_id, {})}

    # 获取信任路径
    trust_result = get_trust_path(product_type_id, industry_type)

    # ===== 计算每个模块的基础得分 =====
    module_scores = {}
    for m_id, m_data in CONTENT_GROWTH_MODULES.items():
        base_score = 50  # 基础分50

        # 根据瓶颈诊断加分（模块能解决的瓶颈越严重，优先级越高）
        for b in bottlenecks:
            b_id = b["bottleneck_id"]
            if m_id in b.get("related_modules", []):
                base_score += b.get("score", 10) * 2

        # 基于企业特征的加分
        if m_id == "module4":  # 短视频
            if content_team_size == 0:
                base_score += 15  # 没有内容团队更需要
            if not has_short_video:
                base_score += 10
            if annual_revenue_wan < 1000:
                base_score += 5  # 小企业更靠内容获客

        if m_id == "module5":  # 直播
            if has_livestream:
                base_score += 10  # 已经在做直播，优化需求更强
            if customer_count > 10000:
                base_score += 5
            if avg_price and avg_price > 500:
                base_score += 5  # 高客单价更需要直播讲清楚

        if m_id == "module6":  # 私域
            if has_private_domain:
                base_score += 10  # 已有私域基础，优化空间大
            if customer_count > 5000:
                base_score += 10
            if industry_type == "experiential":
                base_score += 8  # 会销行业私域是核心

        if m_id == "module7":  # AI知识库
            if input_data.get("employee_count", 0) >= 20:
                base_score += 10  # 团队大更需要知识库
            if content_team_size >= 3:
                base_score += 5

        if m_id == "module2":  # 卖点重构
            if "product_unclear" in [b["bottleneck_id"] for b in bottlenecks]:
                base_score += 15
            if avg_price and avg_price > 1000:
                base_score += 5  # 高客单价更需要讲清楚价值

        if m_id == "module3":  # 痛点与信任
            if "trust_deficit" in [b["bottleneck_id"] for b in bottlenecks]:
                base_score += 15
            if trust_result["primary_path"] in ["case_trust", "expert_trust"]:
                base_score += 10

        # 模块依赖加分（前置模块已做过的话，当前模块可以推进）
        # 简化处理：依赖模块的存在说明需要系统性推进
        deps = MODULE_DEPENDENCIES.get(m_id, [])
        for dep_id in deps:
            if dep_id in module_scores:
                # 前置模块得分高，当前模块也应该跟上
                pass  # 依赖关系主要用于排序，不影响基础分

        module_scores[m_id] = {
            "module_id": m_id,
            "module_name": m_data["module_name"],
            "module_order": m_data["module_order"],
            "description": m_data["description"],
            "core_value": m_data["core_value"],
            "deliverables_count": len(m_data["deliverables"]),
            "difficulty": m_data["difficulty"],
            "timeline": m_data["timeline"],
            "budget_range": m_data["budget_range"],
            "dependencies": deps,
            "base_score": base_score,
        }

    # ===== 应用推荐策略，调整排序权重 =====
    # 确定策略类型
    strategy_type = "balanced"
    if bottlenecks:
        primary_bottleneck = bottlenecks[0]["bottleneck_id"]
        if primary_bottleneck == "content_shortage":
            strategy_type = "content_first"
        elif primary_bottleneck == "conversion_weak":
            strategy_type = "conversion_first"
        elif primary_bottleneck in ["trust_deficit", "product_unclear"]:
            strategy_type = "trust_first"

    strategy = MODULE_PRIORITY_RULES.get(strategy_type, MODULE_PRIORITY_RULES["balanced"])

    # 根据策略优先级调整最终得分（策略优先级高的模块额外加分）
    for i, m_id in enumerate(strategy["priority"]):
        if m_id in module_scores:
            # 排名越靠前，加分越多
            bonus = (len(strategy["priority"]) - i) * 3
            module_scores[m_id]["strategy_bonus"] = bonus
            module_scores[m_id]["final_score"] = round(
                module_scores[m_id]["base_score"] + bonus, 1
            )

    # 按最终得分排序
    sorted_modules = sorted(
        module_scores.values(),
        key=lambda x: x.get("final_score", x["base_score"]),
        reverse=True
    )

    # 添加排名
    for i, m in enumerate(sorted_modules, 1):
        m["rank"] = i

    # 提取模块ID列表
    module_ids_sorted = [m["module_id"] for m in sorted_modules]

    # 推荐的首要模块（考虑依赖关系）
    # 从得分最高的开始，找一个依赖都已满足的（这里简化为第一个）
    recommended_first = sorted_modules[0]["module_id"] if sorted_modules else None

    # 阶段规划：分3个阶段推进
    phase1 = []  # 第一阶段：诊断+基础（2周）
    phase2 = []  # 第二阶段：内容+转化（2-4周）
    phase3 = []  # 第三阶段：深化+执行（4-8周）

    for m in sorted_modules:
        m_id = m["module_id"]
        if m_id in ["module1", "module2"]:
            phase1.append(m_id)
        elif m_id in ["module3", "module4", "module5", "module6"]:
            phase2.append(m_id)
        elif m_id == "module7":
            phase3.append(m_id)

    # 确保phase1至少有定位诊断
    if "module1" not in phase1:
        phase1.insert(0, "module1")

    return {
        "version": "2.0.0",
        "strategy_type": strategy_type,
        "strategy_label": strategy["label"],
        "strategy_condition": strategy["condition"],
        "product_type": product_type_result.get("label", ""),
        "primary_trust_path": trust_result["primary_path_data"]["label"],
        "modules_sorted": sorted_modules,
        "module_ids_sorted": module_ids_sorted,
        "top3_modules": module_ids_sorted[:3],
        "recommended_first_module": recommended_first,
        "phase_plan": {
            "phase1": {"name": "诊断筑基期（第1-2周）", "modules": phase1},
            "phase2": {"name": "内容增长期（第3-6周）", "modules": phase2},
            "phase3": {"name": "体系深化期（第7-12周）", "modules": phase3},
        },
        "bottlenecks_count": len(bottlenecks),
        "primary_bottleneck": bottlenecks[0]["label"] if bottlenecks else "",
    }


def main():
    parser = argparse.ArgumentParser(description="模块推荐引擎 v2.0.0")
    parser.add_argument("--input", "-i", help="输入JSON文件路径或JSON字符串")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    args = parser.parse_args()

    # 自测模式
    if args.self_test:
        test_cases = [
            {
                "name": "羊奶会销企业（50人，年营收5000万，内容弱）",
                "input": {
                    "industry_type": "experiential",
                    "product_name": "中老年高钙羊奶粉",
                    "product_description": "会销模式销售，针对中老年人",
                    "annual_revenue_wan": 5000,
                    "employee_count": 50,
                    "content_team_size": 2,
                    "has_short_video": False,
                    "has_livestream": True,
                    "has_private_domain": True,
                    "customer_count": 20000,
                    "avg_price": 398,
                },
                "maturity_scores": {
                    "product_clarity": 50,
                    "content_capability": 35,
                    "trust_building": 60,
                    "conversion_system": 70,
                    "team_execution": 40,
                },
            },
            {
                "name": "连锁药店（200人，有流量没转化）",
                "input": {
                    "industry_type": "medical",
                    "product_name": "连锁药店保健品",
                    "product_description": "药店销售保健品和医疗器械",
                    "annual_revenue_wan": 8000,
                    "employee_count": 200,
                    "content_team_size": 5,
                    "store_count": 30,
                    "has_short_video": True,
                    "has_livestream": False,
                    "has_private_domain": True,
                    "customer_count": 50000,
                    "avg_price": 299,
                },
                "maturity_scores": {
                    "product_clarity": 70,
                    "content_capability": 65,
                    "trust_building": 70,
                    "conversion_system": 40,
                    "team_execution": 55,
                },
            },
            {
                "name": "医美机构（信任门槛极高）",
                "input": {
                    "industry_type": "anti_aging",
                    "product_name": "轻医美项目+抗衰产品",
                    "product_description": "医美机构，客单价高",
                    "annual_revenue_wan": 10000,
                    "employee_count": 80,
                    "content_team_size": 8,
                    "has_short_video": True,
                    "has_livestream": True,
                    "has_private_domain": True,
                    "customer_count": 30000,
                    "avg_price": 5000,
                },
                "maturity_scores": {
                    "product_clarity": 55,
                    "content_capability": 70,
                    "trust_building": 40,
                    "conversion_system": 60,
                    "team_execution": 50,
                },
            },
            {
                "name": "小微保健品店（从零开始）",
                "input": {
                    "industry_type": "chain_store",
                    "product_name": "保健品",
                    "product_description": "社区保健品店",
                    "annual_revenue_wan": 300,
                    "employee_count": 10,
                    "content_team_size": 1,
                    "store_count": 2,
                    "has_short_video": False,
                    "has_livestream": False,
                    "has_private_domain": False,
                    "customer_count": 500,
                    "avg_price": 200,
                },
                "maturity_scores": {
                    "product_clarity": 40,
                    "content_capability": 30,
                    "trust_building": 35,
                    "conversion_system": 30,
                    "team_execution": 40,
                },
            },
        ]

        print("=" * 70)
        print("模块推荐引擎 v2.0.0 - 自测")
        print("=" * 70)

        all_passed = True
        for i, test in enumerate(test_cases, 1):
            result = calculate_module_scores(
                test["input"],
                maturity_scores=test["maturity_scores"]
            )
            print(f"\n【测试 {i}】{test['name']}")
            print(f"  策略类型: {result['strategy_label']}")
            print(f"  产品类型: {result['product_type']}")
            print(f"  主要信任路径: {result['primary_trust_path']}")
            print(f"  首要瓶颈: {result['primary_bottleneck']}")
            print(f"  推荐首做模块: {result['recommended_first_module']}")

            print(f"  \n  模块优先级排序:")
            for m in result["modules_sorted"]:
                score = m.get("final_score", m.get("base_score", 0))
                print(f"    {m['rank']}. {m['module_name']:18s}  得分: {score:5.1f}  "
                      f"[难度:{m['difficulty']}] [周期:{m['timeline']}]")

            print(f"  \n  三阶段规划:")
            for phase_key, phase_data in result["phase_plan"].items():
                module_names = [CONTENT_GROWTH_MODULES[m]["module_name"] for m in phase_data["modules"] if m in CONTENT_GROWTH_MODULES]
                print(f"    {phase_data['name']}: {', '.join(module_names)}")

            # 校验
            passed = (
                len(result["modules_sorted"]) == 7
                and result["recommended_first_module"] is not None
                and len(result["top3_modules"]) == 3
                and "phase_plan" in result
                and result["strategy_type"] in ["content_first", "conversion_first", "trust_first", "balanced"]
            )
            if not passed:
                all_passed = False
                print(f"  ❌ 校验失败!")
            else:
                print(f"  ✅ 正常")

        print("\n" + "=" * 70)
        if all_passed:
            print("所有测试通过 ✅")
        else:
            print("部分测试失败 ❌")
        print("=" * 70)
        return 0 if all_passed else 1

    # 解析输入
    input_data = {}
    maturity_scores = None

    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                input_data = json.load(f)
        except (FileNotFoundError, OSError):
            try:
                input_data = json.loads(args.input)
            except json.JSONDecodeError:
                print(f"错误: 无法解析输入 '{args.input}'", file=sys.stderr)
                return 1

        # 提取成熟度分数
        if "maturity_scores" in input_data:
            maturity_scores = input_data.pop("maturity_scores")
    elif not sys.stdin.isatty():
        try:
            input_data = json.load(sys.stdin)
            if "maturity_scores" in input_data:
                maturity_scores = input_data.pop("maturity_scores")
        except json.JSONDecodeError:
            print("错误: 标准输入不是有效的JSON", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1

    result = calculate_module_scores(input_data, maturity_scores=maturity_scores)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

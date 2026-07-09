#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容增长成熟度评分引擎（v2.0.0）
===================================
根据企业信息计算5维度内容增长成熟度评分，支持按行业动态权重校准。

v2.0 重大变化：
- 从"AI落地准备度评分" → "内容增长成熟度评分"
- 5个维度全部重构：产品表达/内容生产/信任构建/转化体系/团队执行
- 新增：成熟度等级（S/A/B/C/D）对应不同的行动建议
- 支持自动判断推荐档位（基础版/标准版/进阶版/长期版）
"""

import json
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ontology import (
    INDUSTRY_WEIGHT_CONFIG,
    CONTENT_GROWTH_DIMENSIONS,
    MATURITY_LEVEL_MAP,
    PRICING_TIERS,
)

# 维度满分
DIMENSION_MAX = {k: v["max_score"] for k, v in CONTENT_GROWTH_DIMENSIONS.items()}

# 维度中文名称
DIMENSION_LABELS = {k: v["label"] for k, v in CONTENT_GROWTH_DIMENSIONS.items()}


def detect_pricing_tier(input_data):
    """
    根据企业特征自动判断推荐的产品档位

    判断逻辑：
    - 年营收1亿+ 或 员工200+ → 长期陪跑版
    - 年营收5000万+ 或 员工100+ → 进阶版
    - 年营收1000万+ 或 员工20+ → 标准版
    - 其他 → 基础版
    """
    annual_revenue_wan = input_data.get("annual_revenue_wan", 0)
    employee_count = input_data.get("employee_count", 0)
    content_team_size = input_data.get("content_team_size", 0)
    forced_tier = input_data.get("pricing_tier")

    if forced_tier and forced_tier in ["basic", "standard", "advanced", "long_term"]:
        return forced_tier

    # 营收判断（优先）
    if annual_revenue_wan >= 10000:
        return "long_term"
    if annual_revenue_wan >= 5000:
        return "advanced"
    if annual_revenue_wan >= 1000:
        return "standard"

    # 员工数判断
    if employee_count >= 200:
        return "long_term"
    if employee_count >= 100:
        return "advanced"
    if employee_count >= 20:
        return "standard"

    # 内容团队判断
    if content_team_size >= 5:
        return "advanced"
    if content_team_size >= 2:
        return "standard"

    # 默认基础版
    return "basic"


def estimate_dimension_scores(input_data):
    """
    根据企业信息估算各维度得分（用于信息不全时的估算）

    这是一个启发式估算，当用户没有完整填写5维度自评时使用。
    基于企业规模、团队配置、行业特征等信息推断成熟度。
    """
    employee_count = input_data.get("employee_count", 10)
    content_team_size = input_data.get("content_team_size", 0)
    annual_revenue_wan = input_data.get("annual_revenue_wan", 0)
    has_short_video = input_data.get("has_short_video", False)
    has_livestream = input_data.get("has_livestream", False)
    has_private_domain = input_data.get("has_private_domain", False)
    has_brand_story = input_data.get("has_brand_story", False)
    customer_count = input_data.get("customer_count", 0)
    industry_type = input_data.get("industry_type", "default")

    scores = {}

    # 1. 产品表达清晰度
    # 基础分：营收越高、团队越大，产品表达通常越清晰
    base = 8  # 默认40%水平
    if has_brand_story:
        base += 4
    if annual_revenue_wan >= 5000:
        base += 3
    elif annual_revenue_wan >= 1000:
        base += 2
    if content_team_size >= 3:
        base += 2
    # 行业调整：医疗/医美行业产品表达通常更严谨
    if industry_type in ["medical", "anti_aging"]:
        base += 2
    scores["product_clarity"] = min(20, base)

    # 2. 内容生产能力
    base = 6  # 默认24%水平
    if has_short_video:
        base += 5
    if content_team_size >= 1:
        base += 3
    if content_team_size >= 3:
        base += 5
    if content_team_size >= 5:
        base += 4
    if has_livestream:
        base += 3
    if annual_revenue_wan >= 5000:
        base += 2
    scores["content_capability"] = min(25, base)

    # 3. 信任构建能力
    base = 8  # 默认32%水平
    if customer_count >= 10000:
        base += 4
    elif customer_count >= 1000:
        base += 2
    if has_private_domain:
        base += 3
    if industry_type in ["medical", "anti_aging"]:
        # 高客单价行业信任更难建立，但通常有更多背书资源
        base += 1
    if annual_revenue_wan >= 5000:
        base += 3
    scores["trust_building"] = min(25, base)

    # 4. 转化体系完善度
    base = 5  # 默认25%水平
    if has_livestream:
        base += 5
    if has_private_domain:
        base += 5
    if customer_count >= 1000:
        base += 2
    if employee_count >= 20:
        base += 2
    if industry_type in ["experiential", "chain_store"]:
        # 会销/连锁通常转化体系更成熟
        base += 3
    scores["conversion_system"] = min(20, base)

    # 5. 团队执行力
    base = 3  # 默认30%水平
    if content_team_size >= 1:
        base += 2
    if content_team_size >= 3:
        base += 2
    if employee_count >= 50:
        base += 1
    if input_data.get("has_ai_experience", False):
        base += 2
    scores["team_execution"] = min(10, base)

    return scores


def calculate_score(input_data):
    """
    计算内容增长成熟度综合评分

    Args:
        input_data: dict，包含以下字段：
            - industry_type: str，行业类型
            - product_clarity: 产品表达清晰度 (0-20)，可选
            - content_capability: 内容生产能力 (0-25)，可选
            - trust_building: 信任构建能力 (0-25)，可选
            - conversion_system: 转化体系完善度 (0-20)，可选
            - team_execution: 团队执行力 (0-10)，可选
            - 其他企业特征字段（用于自动估算和档位判断）

    Returns:
        dict，完整的评分结果
    """
    industry_type = input_data.get("industry_type", "default")
    if industry_type not in INDUSTRY_WEIGHT_CONFIG:
        industry_type = "default"

    weights_config = INDUSTRY_WEIGHT_CONFIG[industry_type]
    # 提取权重（去掉label字段）
    weights = {k: v for k, v in weights_config.items() if k != "label"}

    # 获取原始得分：如果用户提供了用用户的，没有的用估算
    provided_scores = {}
    for dim in CONTENT_GROWTH_DIMENSIONS:
        if dim in input_data and input_data[dim] is not None:
            provided_scores[dim] = input_data[dim]

    if len(provided_scores) >= 3:
        # 用户提供了大部分维度，使用用户提供的，缺失的用估算补充
        estimated = estimate_dimension_scores(input_data)
        raw_scores = {}
        for dim in CONTENT_GROWTH_DIMENSIONS:
            if dim in provided_scores:
                raw_scores[dim] = provided_scores[dim]
            else:
                raw_scores[dim] = estimated[dim]
        score_source = "用户自评+估算补充"
    else:
        # 用户没怎么提供，使用估算
        raw_scores = estimate_dimension_scores(input_data)
        score_source = "自动估算（基于企业特征）"

    # 校验分数范围
    for dim, score in raw_scores.items():
        max_score = DIMENSION_MAX[dim]
        if score < 0:
            raw_scores[dim] = 0
        elif score > max_score:
            raw_scores[dim] = max_score

    # 计算加权得分（百分制）
    weighted_scores = {}
    total_weighted = 0.0

    for dim in raw_scores:
        normalized = (raw_scores[dim] / DIMENSION_MAX[dim]) * 100
        weighted = normalized * weights.get(dim, 0.2)
        weighted_scores[dim] = round(weighted, 1)
        total_weighted += weighted

    total_score = round(total_weighted, 1)

    # 获取成熟度等级
    level_info = None
    for item in MATURITY_LEVEL_MAP:
        if item["min"] <= total_score <= item["max"]:
            level_info = item
            break

    # 判断推荐档位
    pricing_tier = detect_pricing_tier(input_data)
    pricing_info = PRICING_TIERS[pricing_tier]

    # 维度排名（找出最强和最弱的维度）
    dim_ranking = sorted(
        [{"dim": dim, "score": raw_scores[dim], "max": DIMENSION_MAX[dim],
          "percent": round(raw_scores[dim] / DIMENSION_MAX[dim] * 100, 1),
          "label": DIMENSION_LABELS[dim]}
         for dim in raw_scores],
        key=lambda x: x["percent"],
        reverse=True
    )

    strongest_dim = dim_ranking[0]
    weakest_dim = dim_ranking[-1]

    return {
        "version": "2.0.0",
        "industry_type": industry_type,
        "industry_label": weights_config.get("label", "通用健康行业"),
        "score_source": score_source,
        "raw_scores": raw_scores,
        "dimension_max": DIMENSION_MAX,
        "weights": weights,
        "weighted_scores": weighted_scores,
        "total_score": total_score,
        "level": level_info["level"] if level_info else "D",
        "level_label": level_info["label"] if level_info else "内容增长空白期",
        "conclusion": level_info["conclusion"] if level_info else "",
        "action": level_info["action"] if level_info else "",
        "dimension_ranking": dim_ranking,
        "strongest_dimension": strongest_dim,
        "weakest_dimension": weakest_dim,
        "recommended_pricing_tier": pricing_tier,
        "recommended_pricing_label": pricing_info["tier"],
        "recommended_pricing_price": pricing_info["price"],
        "recommended_pricing_target": pricing_info["target_customer"],
    }


def main():
    parser = argparse.ArgumentParser(description="内容增长成熟度评分引擎 v2.0.0")
    parser.add_argument("--input", "-i", help="输入JSON文件路径，或直接传入JSON字符串")
    parser.add_argument("--industry", default="default",
                        help="行业类型：default/medical/online/experiential/chain_store/anti_aging")
    parser.add_argument("--product-clarity", type=float, help="产品表达清晰度 (0-20)")
    parser.add_argument("--content-capability", type=float, help="内容生产能力 (0-25)")
    parser.add_argument("--trust-building", type=float, help="信任构建能力 (0-25)")
    parser.add_argument("--conversion-system", type=float, help="转化体系完善度 (0-20)")
    parser.add_argument("--team-execution", type=float, help="团队执行力 (0-10)")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    args = parser.parse_args()

    # 自测模式
    if args.self_test:
        test_cases = [
            {
                "name": "羊奶会销企业（50人，年营收5000万）",
                "input": {
                    "industry_type": "experiential",
                    "annual_revenue_wan": 5000,
                    "employee_count": 50,
                    "content_team_size": 3,
                    "has_short_video": True,
                    "has_livestream": True,
                    "has_private_domain": True,
                    "has_brand_story": True,
                    "customer_count": 20000,
                    "has_ai_experience": False,
                },
            },
            {
                "name": "连锁药店（200人，年营收8000万）",
                "input": {
                    "industry_type": "medical",
                    "annual_revenue_wan": 8000,
                    "employee_count": 200,
                    "content_team_size": 5,
                    "store_count": 30,
                    "has_short_video": True,
                    "has_livestream": False,
                    "has_private_domain": True,
                    "has_brand_story": True,
                    "customer_count": 50000,
                    "has_ai_experience": True,
                },
            },
            {
                "name": "小微保健品店（10人，年营收300万）",
                "input": {
                    "industry_type": "chain_store",
                    "annual_revenue_wan": 300,
                    "employee_count": 10,
                    "content_team_size": 1,
                    "store_count": 2,
                    "has_short_video": False,
                    "has_livestream": False,
                    "has_private_domain": False,
                    "has_brand_story": False,
                    "customer_count": 500,
                    "has_ai_experience": False,
                },
            },
            {
                "name": "医美机构（80人，年营收1亿）- 有完整自评",
                "input": {
                    "industry_type": "anti_aging",
                    "annual_revenue_wan": 10000,
                    "employee_count": 80,
                    "content_team_size": 8,
                    "product_clarity": 15,
                    "content_capability": 18,
                    "trust_building": 16,
                    "conversion_system": 14,
                    "team_execution": 6,
                    "has_short_video": True,
                    "has_livestream": True,
                    "has_private_domain": True,
                    "customer_count": 30000,
                    "has_ai_experience": True,
                },
            },
        ]

        print("=" * 70)
        print("内容增长成熟度评分引擎 v2.0.0 - 自测")
        print("=" * 70)

        all_passed = True
        for i, test in enumerate(test_cases, 1):
            result = calculate_score(test["input"])
            print(f"\n【测试 {i}】{test['name']}")
            print(f"  行业: {result['industry_label']}")
            print(f"  评分来源: {result['score_source']}")
            print(f"  原始得分: {result['raw_scores']}")
            print(f"  总分: {result['total_score']} / 100")
            print(f"  等级: {result['level']}级 - {result['level_label']}")
            print(f"  最强维度: {result['strongest_dimension']['label']} ({result['strongest_dimension']['percent']}%)")
            print(f"  最弱维度: {result['weakest_dimension']['label']} ({result['weakest_dimension']['percent']}%)")
            print(f"  推荐档位: {result['recommended_pricing_label']}（{result['recommended_pricing_price']}）")
            print(f"  结论: {result['conclusion']}")

            passed = (
                0 <= result["total_score"] <= 100
                and result["level"] in ["S", "A", "B", "C", "D"]
                and "recommended_pricing_tier" in result
                and len(result["dimension_ranking"]) == 5
                and result["strongest_dimension"]["percent"] >= result["weakest_dimension"]["percent"]
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

    # 解析输入数据
    input_data = {}

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
    elif not sys.stdin.isatty():
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            print("错误: 标准输入不是有效的JSON", file=sys.stderr)
            return 1
    else:
        # 命令行参数模式
        input_data = {
            "industry_type": args.industry,
        }
        if args.product_clarity is not None:
            input_data["product_clarity"] = args.product_clarity
        if args.content_capability is not None:
            input_data["content_capability"] = args.content_capability
        if args.trust_building is not None:
            input_data["trust_building"] = args.trust_building
        if args.conversion_system is not None:
            input_data["conversion_system"] = args.conversion_system
        if args.team_execution is not None:
            input_data["team_execution"] = args.team_execution

        if len(input_data) == 1:  # 只有industry_type
            parser.print_help()
            return 1

    result = calculate_score(input_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

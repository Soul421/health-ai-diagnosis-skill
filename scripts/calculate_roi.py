#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容增长ROI测算引擎（v2.0.0）
================================
测算内容增长投入带来的转化提升和收益增长，
不再是"省了多少人力成本"，而是"内容带来了多少增量收入"。

v2.0 重大变化：
- 从"人力成本节省ROI" → "内容增长带来的增量收入ROI"
- 新增：内容投入vs转化提升的测算模型
- 新增：4档产品报价的ROI对比
- 新增：30天/90天/180天三阶段ROI预测
"""

import json
import sys
import argparse

# ===== 内容增长 ROI 参数 =====

# 不同模块的预期效果参数
# 注意：这些是"理想状态下12个月稳态效果"的基准值
# 实际效果受执行力度、行业、基础水平影响很大
MODULE_EFFECT_PARAMS = {
    "module1": {  # 定位诊断
        "effect_on_conversion": 0.01,    # 转化率提升1%
        "effect_on_traffic": 0.0,
        "effect_on_repurchase": 0.01,    # 复购率提升1%
        "effect_lag_weeks": 2,
    },
    "module2": {  # 卖点重构
        "effect_on_conversion": 0.05,    # 转化率提升5%（核心）
        "effect_on_traffic": 0.01,       # 流量提升1%
        "effect_on_repurchase": 0.03,    # 复购率提升3%
        "effect_lag_weeks": 2,
    },
    "module3": {  # 痛点与信任
        "effect_on_conversion": 0.06,    # 转化率提升6%
        "effect_on_traffic": 0.01,
        "effect_on_repurchase": 0.05,    # 复购率提升5%
        "effect_lag_weeks": 4,
    },
    "module4": {  # 短视频
        "effect_on_conversion": 0.01,
        "effect_on_traffic": 0.15,       # 流量提升15%（核心价值）
        "effect_on_repurchase": 0.01,
        "effect_lag_weeks": 8,           # 起号慢
    },
    "module5": {  # 直播
        "effect_on_conversion": 0.08,    # 转化率提升8%
        "effect_on_traffic": 0.05,       # 流量提升5%
        "effect_on_repurchase": 0.02,
        "effect_lag_weeks": 4,
    },
    "module6": {  # 私域
        "effect_on_conversion": 0.05,    # 转化率提升5%
        "effect_on_traffic": 0.0,
        "effect_on_repurchase": 0.08,    # 复购率提升8%（核心价值）
        "effect_lag_weeks": 6,
    },
    "module7": {  # AI知识库与执行
        "effect_on_conversion": 0.02,
        "effect_on_traffic": 0.03,       # 流量提升3%（产能提升）
        "effect_on_repurchase": 0.02,
        "effect_lag_weeks": 3,
    },
}

# 总效果上限（避免不切实际的ROI）
MAX_TOTAL_EFFECT = {
    "conversion": 0.20,   # 转化率最多提升20%
    "traffic": 0.35,      # 流量最多提升35%
    "repurchase": 0.15,   # 复购率最多提升15%
}

# 内容可影响营收比例（内容营销能影响的营收占总营收的比例）
# 不是所有营收都靠内容，还有线下、渠道、老客复购等
CONTENT_INFLUENCE_RATIO = {
    "default": 0.40,       # 默认40%的营收受内容影响
    "medical": 0.25,       # 医疗行业更多靠线下和口碑
    "online": 0.60,        # 纯线上品牌，内容影响更大
    "experiential": 0.45,  # 会销行业，内容+私域影响约45%
    "chain_store": 0.30,   # 连锁门店更多靠线下流量
    "anti_aging": 0.55,    # 医美抗衰，内容种草影响大
}

# 4档产品的模块覆盖和效果系数
TIER_EFFECT_MULTIPLIER = {
    "basic": {
        "multiplier": 0.35,   # 基础版效果35%（模板为主，执行靠自己）
        "modules": ["module1", "module2", "module4"],
    },
    "standard": {
        "multiplier": 0.6,    # 标准版效果60%（有专家诊断+定制调整+陪跑）
        "modules": ["module1", "module2", "module3", "module4", "module6", "module7"],
    },
    "advanced": {
        "multiplier": 0.85,   # 进阶版效果85%（深度定制+陪跑+操盘）
        "modules": ["module1", "module2", "module3", "module4", "module5", "module6", "module7"],
    },
    "long_term": {
        "multiplier": 1.0,    # 长期版效果100%（全年陪跑+持续优化）
        "modules": ["module1", "module2", "module3", "module4", "module5", "module6", "module7"],
    },
}

# 档位价格（元）
TIER_PRICES = {
    "basic": 3980,
    "standard": 19800,
    "advanced": 98000,
    "long_term": 298000,  # 年费
}

# 档位名称
TIER_NAMES = {
    "basic": "基础版",
    "standard": "标准版",
    "advanced": "进阶版",
    "long_term": "长期陪跑版",
}

# 执行周期（天）
TIER_DURATION_DAYS = {
    "basic": 30,
    "standard": 90,
    "advanced": 90,
    "long_term": 365,
}


def calculate_tier_effect(tier: str, current_monthly_revenue: float,
                         current_conversion_rate: float,
                         current_repurchase_rate: float,
                         current_traffic: float,
                         content_influence_ratio: float = 0.4) -> dict:
    """
    计算某一档位的预期效果

    Args:
        tier: 档位 key
        current_monthly_revenue: 当前月营收（万元）
        current_conversion_rate: 当前转化率（小数，如0.02=2%）
        current_repurchase_rate: 当前复购率（小数）
        current_traffic: 当前月流量（人次）
        content_influence_ratio: 内容可影响营收比例（0-1）

    Returns:
        dict，包含各项指标提升和增量收入
    """
    if tier not in TIER_EFFECT_MULTIPLIER:
        tier = "standard"

    tier_data = TIER_EFFECT_MULTIPLIER[tier]
    modules = tier_data["modules"]
    multiplier = tier_data["multiplier"]

    # 累加各模块的效果（考虑边际递减，用1-乘积的方式计算总提升）
    # 即：总提升 = 1 - (1-提升1) × (1-提升2) × ...
    total_conversion_effect = 1.0
    total_traffic_effect = 1.0
    total_repurchase_effect = 1.0

    for m_id in modules:
        params = MODULE_EFFECT_PARAMS.get(m_id, {})
        total_conversion_effect *= (1 - params.get("effect_on_conversion", 0) * multiplier)
        total_traffic_effect *= (1 - params.get("effect_on_traffic", 0) * multiplier)
        total_repurchase_effect *= (1 - params.get("effect_on_repurchase", 0) * multiplier)

    conversion_lift = 1 - total_conversion_effect
    traffic_lift = 1 - total_traffic_effect
    repurchase_lift = 1 - total_repurchase_effect

    # 应用总效果上限（避免不切实际的ROI）
    conversion_lift = min(conversion_lift, MAX_TOTAL_EFFECT["conversion"])
    traffic_lift = min(traffic_lift, MAX_TOTAL_EFFECT["traffic"])
    repurchase_lift = min(repurchase_lift, MAX_TOTAL_EFFECT["repurchase"])

    # 计算增量收入
    # 简化模型：收入 = 流量 × 转化率 × 客单价 × (1 + 复购贡献)
    # 内容增长只影响"内容可影响"的那部分营收
    # 增量收入 ≈ 当前营收 × 内容影响比例 × [(1+流量提升) × (1+转化提升) × (1+复购提升系数) - 1]

    # 复购对收入的贡献系数（复购率提升带来的收入增长约为复购率提升的一半）
    repurchase_revenue_factor = repurchase_lift * 0.5

    # 月度增量收入估算（只计算内容影响部分的增长）
    affected_revenue = current_monthly_revenue * content_influence_ratio
    monthly_incremental = affected_revenue * (
        (1 + traffic_lift) * (1 + conversion_lift) * (1 + repurchase_revenue_factor) - 1
    )

    # 年化增量收入
    annual_incremental = monthly_incremental * 12

    # ROI计算
    cost = TIER_PRICES[tier]
    cost_wan = cost / 10000  # 转为万元

    # 回本周期（月）
    if monthly_incremental > 0:
        payback_months = round(cost_wan / monthly_incremental, 1)
    else:
        payback_months = float("inf")

    # 首年ROI
    first_year_roi = round((annual_incremental - cost_wan) / cost_wan * 100, 1) if cost_wan > 0 else 0

    return {
        "tier": tier,
        "tier_name": TIER_NAMES[tier],
        "price": cost,
        "price_wan": cost_wan,
        "duration_days": TIER_DURATION_DAYS[tier],
        "modules_covered": modules,
        "modules_count": len(modules),
        "effect_multiplier": multiplier,
        "conversion_lift": round(conversion_lift * 100, 1),  # 转为百分比
        "traffic_lift": round(traffic_lift * 100, 1),
        "repurchase_lift": round(repurchase_lift * 100, 1),
        "monthly_incremental_revenue_wan": round(monthly_incremental, 1),
        "annual_incremental_revenue_wan": round(annual_incremental, 1),
        "payback_months": payback_months,
        "first_year_roi_percent": first_year_roi,
        "roi_description": _describe_roi(first_year_roi, payback_months),
    }


def _describe_roi(roi_percent: float, payback_months: float) -> str:
    """ROI描述"""
    if payback_months <= 1:
        return "回报极快，当月即可回本，强烈推荐"
    elif payback_months <= 3:
        return "回报很快，3个月内回本，非常值得投入"
    elif payback_months <= 6:
        return "回报合理，半年内回本，建议尽快启动"
    elif payback_months <= 12:
        return "回报正常，1年内回本，可以考虑"
    else:
        return "回报周期较长，建议先从低档位试水"


def calculate_content_growth_roi(input_data: dict) -> dict:
    """
    计算内容增长ROI完整分析

    Args:
        input_data: dict，包含：
            - annual_revenue_wan: 年营收（万元）
            - monthly_revenue_wan: 月营收（万元，可选，未提供取年营收/12）
            - conversion_rate: 当前转化率（小数，如0.02）
            - repurchase_rate: 当前复购率（小数）
            - monthly_traffic: 月流量（人次，可选）
            - customer_count: 客户数（可选）
            - avg_price: 客单价（元，可选）
            - industry_type: 行业类型
            - 其他企业特征字段

    Returns:
        dict，完整ROI分析结果
    """
    annual_revenue_wan = input_data.get("annual_revenue_wan", 0)
    monthly_revenue_wan = input_data.get("monthly_revenue_wan", 0) or (annual_revenue_wan / 12)
    conversion_rate = input_data.get("conversion_rate", 0.02)  # 默认2%
    repurchase_rate = input_data.get("repurchase_rate", 0.2)   # 默认20%
    monthly_traffic = input_data.get("monthly_traffic", 0)
    industry_type = input_data.get("industry_type", "default")

    # 如果没有月流量，根据月营收和转化率+客单价反推
    if monthly_traffic == 0:
        avg_price = input_data.get("avg_price", 300)  # 默认客单价300
        if conversion_rate > 0 and avg_price > 0:
            # 月营收 = 流量 × 转化率 × 客单价 / 10000（万元）
            monthly_traffic = (monthly_revenue_wan * 10000) / (conversion_rate * avg_price) if conversion_rate > 0 else 0
        else:
            monthly_traffic = 10000  # 默认值

    # 行业调整系数
    industry_adjust = {
        "default": 1.0,
        "medical": 0.8,      # 医疗行业合规限制多，内容效果打8折
        "online": 1.2,       # 纯线上电商，内容效果更好
        "experiential": 1.1,  # 会销行业，内容+私域效果好
        "chain_store": 0.9,  # 连锁门店，内容效果中等
        "anti_aging": 1.15,  # 医美抗衰，高客单价，内容ROI高
    }
    adjust = industry_adjust.get(industry_type, 1.0)

    # 内容可影响营收比例（按行业）
    content_influence_ratio = CONTENT_INFLUENCE_RATIO.get(industry_type, 0.4)

    # 计算4个档位的ROI
    tier_results = {}
    for tier in ["basic", "standard", "advanced", "long_term"]:
        result = calculate_tier_effect(
            tier=tier,
            current_monthly_revenue=monthly_revenue_wan,
            current_conversion_rate=conversion_rate,
            current_repurchase_rate=repurchase_rate,
            current_traffic=monthly_traffic,
            content_influence_ratio=content_influence_ratio,
        )
        # 应用行业调整
        result["conversion_lift"] = round(result["conversion_lift"] * adjust, 1)
        result["traffic_lift"] = round(result["traffic_lift"] * adjust, 1)
        result["repurchase_lift"] = round(result["repurchase_lift"] * adjust, 1)
        result["monthly_incremental_revenue_wan"] = round(result["monthly_incremental_revenue_wan"] * adjust, 1)
        result["annual_incremental_revenue_wan"] = round(result["annual_incremental_revenue_wan"] * adjust, 1)

        # 重新计算ROI
        cost_wan = result["price_wan"]
        monthly_inc = result["monthly_incremental_revenue_wan"]
        annual_inc = result["annual_incremental_revenue_wan"]

        if monthly_inc > 0:
            result["payback_months"] = round(cost_wan / monthly_inc, 1)
        else:
            result["payback_months"] = float("inf")

        result["first_year_roi_percent"] = round((annual_inc - cost_wan) / cost_wan * 100, 1) if cost_wan > 0 else 0
        result["roi_description"] = _describe_roi(result["first_year_roi_percent"], result["payback_months"])

        tier_results[tier] = result

    # 推荐档位（基于回本周期和企业规模）
    recommended_tier = "standard"  # 默认标准版
    if annual_revenue_wan < 500:
        recommended_tier = "basic"
    elif annual_revenue_wan >= 10000:
        recommended_tier = "long_term"
    elif annual_revenue_wan >= 5000:
        recommended_tier = "advanced"

    # 三阶段效果预测（以推荐档位为准）
    rec_tier = tier_results[recommended_tier]
    effect_multiplier = rec_tier["effect_multiplier"]

    # 30天/90天/180天的效果渐进
    phase_effects = {
        "day30": {
            "effect_percentage": 30,  # 30天时达到总效果的30%
            "cumulative_revenue_wan": round(rec_tier["monthly_incremental_revenue_wan"] * 0.3, 1),
        },
        "day90": {
            "effect_percentage": 70,  # 90天时达到70%
            "cumulative_revenue_wan": round(
                rec_tier["monthly_incremental_revenue_wan"] * (0.3 + 0.5 + 0.7), 1
            ),
        },
        "day180": {
            "effect_percentage": 95,  # 180天时达到95%
            "cumulative_revenue_wan": round(
                rec_tier["monthly_incremental_revenue_wan"] * (0.3 + 0.5 + 0.7 + 0.9 + 0.95 + 0.95), 1
            ),
        },
    }

    return {
        "version": "2.0.0",
        "base_assumptions": {
            "monthly_revenue_wan": round(monthly_revenue_wan, 1),
            "annual_revenue_wan": annual_revenue_wan,
            "conversion_rate": round(conversion_rate * 100, 1),
            "repurchase_rate": round(repurchase_rate * 100, 1),
            "monthly_traffic": round(monthly_traffic, 0),
            "industry_type": industry_type,
            "industry_adjust": adjust,
            "content_influence_ratio": round(content_influence_ratio * 100, 0),
        },
        "tier_results": tier_results,
        "recommended_tier": recommended_tier,
        "recommended_tier_name": TIER_NAMES[recommended_tier],
        "recommended_tier_data": rec_tier,
        "phase_predictions": phase_effects,
        "roi_summary": {
            "recommended_price": TIER_PRICES[recommended_tier],
            "recommended_price_wan": TIER_PRICES[recommended_tier] / 10000,
            "expected_monthly_incremental": rec_tier["monthly_incremental_revenue_wan"],
            "expected_annual_incremental": rec_tier["annual_incremental_revenue_wan"],
            "payback_months": rec_tier["payback_months"],
            "first_year_roi": rec_tier["first_year_roi_percent"],
        },
    }


def main():
    parser = argparse.ArgumentParser(description="内容增长ROI测算引擎 v2.0.0")
    parser.add_argument("--input", "-i", help="输入JSON文件路径或JSON字符串")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    args = parser.parse_args()

    # 自测模式
    if args.self_test:
        test_cases = [
            {
                "name": "羊奶会销企业（年营收5000万，会销模式）",
                "input": {
                    "annual_revenue_wan": 5000,
                    "conversion_rate": 0.05,
                    "repurchase_rate": 0.35,
                    "avg_price": 398,
                    "industry_type": "experiential",
                    "customer_count": 20000,
                },
            },
            {
                "name": "连锁药店（年营收8000万）",
                "input": {
                    "annual_revenue_wan": 8000,
                    "conversion_rate": 0.08,
                    "repurchase_rate": 0.40,
                    "avg_price": 150,
                    "industry_type": "medical",
                    "customer_count": 50000,
                },
            },
            {
                "name": "医美机构（年营收1亿，高客单价）",
                "input": {
                    "annual_revenue_wan": 10000,
                    "conversion_rate": 0.03,
                    "repurchase_rate": 0.25,
                    "avg_price": 5000,
                    "industry_type": "anti_aging",
                    "customer_count": 30000,
                },
            },
            {
                "name": "小微保健品店（年营收300万）",
                "input": {
                    "annual_revenue_wan": 300,
                    "conversion_rate": 0.04,
                    "repurchase_rate": 0.30,
                    "avg_price": 200,
                    "industry_type": "chain_store",
                    "customer_count": 500,
                },
            },
        ]

        print("=" * 70)
        print("内容增长ROI测算引擎 v2.0.0 - 自测")
        print("=" * 70)

        all_passed = True
        for i, test in enumerate(test_cases, 1):
            result = calculate_content_growth_roi(test["input"])
            base = result["base_assumptions"]
            summary = result["roi_summary"]

            print(f"\n【测试 {i}】{test['name']}")
            print(f"  月营收: {base['monthly_revenue_wan']}万, 转化率: {base['conversion_rate']}%, 复购率: {base['repurchase_rate']}%")
            print(f"  月流量: {base['monthly_traffic']:.0f}人次, 行业调整: {base['industry_adjust']}")
            print(f"  推荐档位: {result['recommended_tier_name']}")
            print(f"  投入: {summary['recommended_price_wan']}万")
            print(f"  预期月增收: {summary['expected_monthly_incremental']}万")
            print(f"  预期年增收: {summary['expected_annual_incremental']}万")
            print(f"  回本周期: {summary['payback_months']}个月")
            print(f"  首年ROI: {summary['first_year_roi']}%")

            print(f"\n  4档位对比:")
            for tier_key, tier_data in result["tier_results"].items():
                rec_mark = " ⭐推荐" if tier_key == result["recommended_tier"] else ""
                print(f"    {tier_data['tier_name']:6s} ({tier_data['price_wan']:>4.1f}万): "
                      f"流量+{tier_data['traffic_lift']:>4.1f}% "
                      f"转化+{tier_data['conversion_lift']:>4.1f}% "
                      f"复购+{tier_data['repurchase_lift']:>4.1f}% "
                      f"月增收{tier_data['monthly_incremental_revenue_wan']:>6.1f}万 "
                      f"回本{tier_data['payback_months']:>4.1f}月"
                      f"{rec_mark}")

            print(f"\n  三阶段效果预测（{result['recommended_tier_name']}）:")
            for phase, data in result["phase_predictions"].items():
                print(f"    {phase}: 达到效果的{data['effect_percentage']}%, 累计增收{data['cumulative_revenue_wan']}万")

            # 校验
            passed = (
                len(result["tier_results"]) == 4
                and result["recommended_tier"] in result["tier_results"]
                and "phase_predictions" in result
                and len(result["phase_predictions"]) == 3
                and summary["expected_monthly_incremental"] > 0
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
        parser.print_help()
        return 1

    result = calculate_content_growth_roi(input_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

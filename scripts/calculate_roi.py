#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROI五档测算引擎（v1.9.0升级）
根据团队结构和预算，计算五档回本周期和隐性成本。
支持轻量模式（前3档）和完整模式（全部5档）。
新增MVP验证ROI计算。
"""

import json
import sys
import argparse

# ===== 各岗位AI替代比例参考（6个月/2年两档） =====
# 格式: {岗位类型: {"6个月": (最低, 最高), "2年": (最低, 最高)}}
SUBSTITUTION_RATIO = {
    "customer_service": {  # 客服售后
        "6months": (0.40, 0.50),
        "2years": (0.70, 0.80),
    },
    "content": {  # 内容创作
        "6months": (0.30, 0.40),
        "2years": (0.50, 0.60),
    },
    "operations": {  # 运营/数据录入（取数据录入比例）
        "6months": (0.50, 0.60),
        "2years": (0.80, 0.90),
    },
    "sales": {  # 销售支持
        "6months": (0.10, 0.20),
        "2years": (0.30, 0.40),
    },
    "admin_hr": {  # 行政支持
        "6months": (0.20, 0.30),
        "2years": (0.40, 0.50),
    },
}

# 岗位中文名称
ROLE_NAMES = {
    "customer_service": "客服售后",
    "content": "内容创作",
    "operations": "运营/数据",
    "sales": "销售支持",
    "admin_hr": "行政人力",
}

# ===== 五档参数（v1.9.0 新增） =====
# 前3档为轻量模式（试水/入门/标准），后2档为完整版（进阶/全面）
BUDGET_TIERS = {
    "exploratory": {
        "name": "试水档",
        "budget_range": "1-3万",
        "budget_min": 10000,
        "budget_max": 30000,
        "mode": "light",  # 轻量模式
        "effect_factor": 0.6,
        "hidden_cost_pct": 0.20,
        "implementation_period": "2周",
        "description": "试水档：MVP验证，选1个痛点快速见效，风险最低",
        "scenarios": ["智能客服", "AI内容生成"],
    },
    "starter": {
        "name": "入门档",
        "budget_range": "5-8万",
        "budget_min": 50000,
        "budget_max": 80000,
        "mode": "light",
        "effect_factor": 0.8,
        "hidden_cost_pct": 0.25,
        "implementation_period": "1个月",
        "description": "入门档：单场景闭环，跑通一个完整业务场景",
        "scenarios": ["智能客服", "AI内容生成", "AI培训助手"],
    },
    "standard": {
        "name": "标准档",
        "budget_range": "15-20万",
        "budget_min": 150000,
        "budget_max": 200000,
        "mode": "light",
        "effect_factor": 1.0,
        "hidden_cost_pct": 0.25,
        "implementation_period": "3个月",
        "description": "标准档：小范围复制，扩展到3个场景+门店复制",
        "scenarios": ["智能客服", "AI内容生成", "私域运营AI", "门店服务诊断"],
    },
    "advanced": {
        "name": "进阶档",
        "budget_range": "40-50万",
        "budget_min": 400000,
        "budget_max": 500000,
        "mode": "full",  # 完整模式
        "effect_factor": 1.1,
        "hidden_cost_pct": 0.25,
        "implementation_period": "6个月",
        "description": "进阶档：全面铺开，多场景协同+数据打通",
        "scenarios": ["智能客服", "AI内容生成", "私域运营AI", "数据分析AI", "门店服务诊断"],
    },
    "comprehensive": {
        "name": "全面档",
        "budget_range": "100-120万",
        "budget_min": 1000000,
        "budget_max": 1200000,
        "mode": "full",
        "effect_factor": 1.3,
        "hidden_cost_pct": 0.15,
        "implementation_period": "12个月",
        "description": "全面档：深度融合，全链路AI改造+智能化决策",
        "scenarios": ["全部场景"],
    },
}

# 档位顺序（用于排序输出）
TIER_ORDER = ["exploratory", "starter", "standard", "advanced", "comprehensive"]

# 接受度整体调整系数（影响所有档位的实际效果）
TEAM_ACCEPTANCE_ADJUST = {
    "low": 0.7,     # 接受度低，整体效果打7折
    "medium": 1.0,  # 正常
    "high": 1.1,    # 接受度高，效果超预期10%
}

# 数字化基础整体调整系数
DIGITAL_BASE_ADJUST = {
    "weak": 0.75,    # 基础弱，整体打75折
    "medium": 1.0,   # 正常
    "strong": 1.1,   # 基础好，效果超预期10%
}

# ===== MVP验证 ROI 计算参数 =====
# 针对单个场景的快速验证ROI
MVP_SCENARIO_ROI = {
    "智能客服": {
        "mvp_cost": 15000,          # MVP投入（元）
        "mvp_period_months": 0.5,    # 验证周期（月）
        "expected_saving_monthly": 8000,  # 预期月节省（元）
        "success_rate": 0.85,        # 成功率
        "kpi": "响应时间缩短60%，夜间咨询覆盖100%",
    },
    "AI内容生成": {
        "mvp_cost": 10000,
        "mvp_period_months": 0.5,
        "expected_saving_monthly": 6000,
        "success_rate": 0.90,
        "kpi": "内容产出提升3-5倍，外包成本降低50%",
    },
    "AI培训助手": {
        "mvp_cost": 12000,
        "mvp_period_months": 0.5,
        "expected_saving_monthly": 5000,
        "success_rate": 0.80,
        "kpi": "培训周期缩短50%，新人上手速度提升1倍",
    },
    "私域运营AI": {
        "mvp_cost": 20000,
        "mvp_period_months": 1,
        "expected_saving_monthly": 7000,
        "success_rate": 0.75,
        "kpi": "私域转化率提升20%，复购率提升15%",
    },
    "门店服务诊断": {
        "mvp_cost": 18000,
        "mvp_period_months": 1,
        "expected_saving_monthly": 6000,
        "success_rate": 0.70,
        "kpi": "门店服务标准化率提升80%，督导成本降低40%",
    },
    "数据分析AI": {
        "mvp_cost": 25000,
        "mvp_period_months": 1,
        "expected_saving_monthly": 8000,
        "success_rate": 0.75,
        "kpi": "报表生成效率提升10倍，决策速度提升3倍",
    },
}


def determine_mode(budget=None, employee_count=None, annual_revenue_wan=None):
    """
    根据企业规模和预算自动判断模式

    Args:
        budget: 预算（元）
        employee_count: 员工总数
        annual_revenue_wan: 年营收（万元）

    Returns:
        str: "light"（轻量模式）或 "full"（完整模式）
    """
    # 预算明确低于20万 → 轻量模式
    if budget and budget <= 200000:
        return "light"
    # 预算明确高于50万 → 完整模式
    if budget and budget >= 500000:
        return "full"
    # 员工少于50人 → 轻量模式
    if employee_count and employee_count < 50:
        return "light"
    # 年营收低于3000万 → 轻量模式
    if annual_revenue_wan and annual_revenue_wan < 3000:
        return "light"
    # 默认：根据预算判断，没有明确信息时返回 "auto"
    return "auto"


def determine_recommended_tier(budget=None, mode="auto"):
    """
    根据预算和模式确定推荐档位

    Args:
        budget: 预算（元）
        mode: "light" / "full" / "auto"

    Returns:
        str: 推荐的档位key
    """
    if budget:
        # 根据预算金额匹配最接近的档位
        if budget <= 30000:
            return "exploratory"
        elif budget <= 80000:
            return "starter"
        elif budget <= 200000:
            return "standard"
        elif budget <= 500000:
            return "advanced"
        else:
            return "comprehensive"
    # 没有预算时，根据模式给默认推荐
    if mode == "light":
        return "starter"
    return "standard"


def calculate_roi(input_data):
    """
    计算ROI五档测算

    Args:
        input_data: dict，包含：
            - team_structure: 各团队人数和薪资
            - budget: 预算（元），可选
            - team_acceptance: low/medium/high
            - digital_base: weak/medium/strong
            - mode: light/full/auto（可选，自动判断）
            - employee_count: 员工总数（可选，用于模式判断）
            - annual_revenue_wan: 年营收万元（可选，用于模式判断）
            - top_scenario: 首选场景名称（可选，用于MVP ROI计算）

    Returns:
        dict，完整ROI分析结果
    """
    team_structure = input_data.get("team_structure", {})
    budget = input_data.get("budget", 0)
    team_acceptance = input_data.get("team_acceptance", "medium")
    digital_base = input_data.get("digital_base", "medium")
    top_scenario = input_data.get("top_scenario", "")
    employee_count = input_data.get("employee_count")
    annual_revenue_wan = input_data.get("annual_revenue_wan")

    if team_acceptance not in TEAM_ACCEPTANCE_ADJUST:
        team_acceptance = "medium"
    if digital_base not in DIGITAL_BASE_ADJUST:
        digital_base = "medium"

    # ===== 自动判断模式 =====
    requested_mode = input_data.get("mode", "auto")
    if requested_mode == "auto":
        actual_mode = determine_mode(budget=budget, employee_count=employee_count,
                                     annual_revenue_wan=annual_revenue_wan)
    else:
        actual_mode = requested_mode

    # ===== 计算年人力成本 =====
    annual_labor_cost = 0
    team_detail = {}
    for role_key, role_data in team_structure.items():
        count = role_data.get("count", 0)
        avg_salary = role_data.get("avg_salary", 0)
        annual = count * avg_salary * 12
        annual_labor_cost += annual
        team_detail[role_key] = {
            "count": count,
            "avg_salary": avg_salary,
            "annual_cost": annual,
            "role_name": ROLE_NAMES.get(role_key, role_key),
        }

    # ===== 计算年节省（6个月/2年两档，取中值） =====
    annual_savings_6months = 0
    annual_savings_2years = 0
    savings_detail = {}

    for role_key, role_data in team_structure.items():
        if role_key not in SUBSTITUTION_RATIO:
            continue
        count = role_data.get("count", 0)
        avg_salary = role_data.get("avg_salary", 0)
        annual_role_cost = count * avg_salary * 12

        ratio_6m = sum(SUBSTITUTION_RATIO[role_key]["6months"]) / 2
        ratio_2y = sum(SUBSTITUTION_RATIO[role_key]["2years"]) / 2

        saving_6m = annual_role_cost * ratio_6m
        saving_2y = annual_role_cost * ratio_2y

        annual_savings_6months += saving_6m
        annual_savings_2years += saving_2y

        savings_detail[role_key] = {
            "role_name": ROLE_NAMES.get(role_key, role_key),
            "annual_cost": annual_role_cost,
            "ratio_6months": round(ratio_6m, 3),
            "ratio_2years": round(ratio_2y, 3),
            "saving_6months": round(saving_6m),
            "saving_2years": round(saving_2y),
        }

    annual_savings_6months = round(annual_savings_6months)
    annual_savings_2years = round(annual_savings_2years)

    # ===== 整体调整系数 =====
    overall_adjust = TEAM_ACCEPTANCE_ADJUST[team_acceptance] * DIGITAL_BASE_ADJUST[digital_base]

    # ===== 计算五档回本周期 =====
    # 使用2年时的年节省作为稳态基准
    baseline_saving = annual_savings_2years

    recommended_tier = determine_recommended_tier(budget=budget, mode=actual_mode)

    payback_period = {}
    for tier_key in TIER_ORDER:
        tier = BUDGET_TIERS[tier_key]
        tier_budget = tier["budget_max"]  # 用该档的上限预算计算

        # 实际投入 = 预算 × (1 + 隐性成本比例)
        total_investment = tier_budget * (1 + tier["hidden_cost_pct"])
        # 实际年节省 = 基准年节省 × 效果系数 × 整体调整系数
        actual_saving = baseline_saving * tier["effect_factor"] * overall_adjust

        if actual_saving > 0:
            payback_months = round(total_investment / actual_saving * 12, 1)
        else:
            payback_months = float("inf")

        payback_period[tier_key] = {
            "tier_name": tier["name"],
            "budget_range": tier["budget_range"],
            "mode": tier["mode"],
            "months": payback_months,
            "total_investment": round(total_investment),
            "actual_annual_saving": round(actual_saving),
            "effect_factor": tier["effect_factor"],
            "hidden_cost_pct": f"{int(tier['hidden_cost_pct'] * 100)}%",
            "implementation_period": tier["implementation_period"],
            "adjustment_factor": round(overall_adjust, 2),
            "description": tier["description"],
            "scenarios": tier["scenarios"],
            "is_recommended": tier_key == recommended_tier,
        }

    # ===== 轻量模式下的档位列表 =====
    if actual_mode == "light":
        visible_tiers = ["exploratory", "starter", "standard"]
    else:
        visible_tiers = TIER_ORDER[:]

    # ===== MVP验证ROI计算 =====
    mvp_roi = None
    if top_scenario and top_scenario in MVP_SCENARIO_ROI:
        mvp_data = MVP_SCENARIO_ROI[top_scenario]
        mvp_cost = mvp_data["mvp_cost"]
        mvp_saving_monthly = mvp_data["expected_saving_monthly"] * overall_adjust
        mvp_period = mvp_data["mvp_period_months"]
        success_rate = mvp_data["success_rate"]

        # 预期月节省 × 成功率
        expected_monthly_saving = mvp_saving_monthly * success_rate
        # 回本周期（月）
        if expected_monthly_saving > 0:
            mvp_payback_months = round(mvp_cost / expected_monthly_saving, 1)
        else:
            mvp_payback_months = float("inf")

        # 首年净收益 = (12 - mvp_period) × 月节省 - MVP成本
        first_year_net = round((12 - mvp_period) * expected_monthly_saving - mvp_cost)

        mvp_roi = {
            "scenario": top_scenario,
            "mvp_cost": mvp_cost,
            "mvp_period_months": mvp_period,
            "expected_monthly_saving": round(expected_monthly_saving),
            "success_rate": success_rate,
            "payback_months": mvp_payback_months,
            "first_year_net_saving": first_year_net,
            "roi_ratio": round(first_year_net / mvp_cost * 100, 1) if mvp_cost > 0 else 0,
            "kpi": mvp_data["kpi"],
        }

    # ===== 隐性成本明细 =====
    # 基于推荐档位的预算计算
    rec_budget = BUDGET_TIERS[recommended_tier]["budget_max"]
    hidden_costs = {
        "one_time": {
            "系统部署与集成": round(rec_budget * 0.10),
            "数据治理与迁移": round(rec_budget * 0.08),
            "人员培训": round(rec_budget * 0.05),
            "流程改造咨询": round(rec_budget * 0.05),
        },
        "recurring": {
            "年订阅/维护费": f"约{round(rec_budget * 0.15)}/年",
            "持续优化人力": "需1-2人兼职维护",
        },
    }
    one_time_total = sum(hidden_costs["one_time"].values())
    hidden_costs["one_time"]["小计"] = one_time_total

    # ===== 两种策略对比 =====
    if annual_savings_6months > 0:
        cut_staff_payback_months = round(rec_budget / annual_savings_6months * 12, 1)
        cut_staff_saving = annual_savings_6months
    else:
        cut_staff_payback_months = float("inf")
        cut_staff_saving = 0

    two_strategies = {
        "cut_staff": {
            "name": "老板A式：消灭岗位",
            "annual_saving": cut_staff_saving,
            "payback_months": cut_staff_payback_months,
            "payback": f"{cut_staff_payback_months}个月",
            "description": "用AI直接替代人力，砍掉重复岗位，成本下降立竿见影。适合利润薄、需要快速降本的企业。",
            "pros": ["人力成本立竿见影", "管理复杂度下降", "ROI计算清晰"],
            "cons": ["团队士气受影响", "核心人才可能流失", "客户体验可能下降", "舆论风险（健康行业敏感）"],
        },
        "boost_efficiency": {
            "name": "老板B式：优化流程",
            "efficiency_gain": "30-50%",
            "payback": "即时回本（产能提升）",
            "description": "用AI增强人的能力，让人做更有价值的事。节省的不是人头，而是招聘成本+外包成本+机会成本。",
            "pros": ["团队稳定士气高", "客户体验不降反升", "承接更大业务量", "无裁员舆论风险"],
            "cons": ["短期成本下降不明显", "需要重新设计工作流程", "效果量化较难"],
        },
    }

    return {
        "version": "1.9.0",
        "mode": actual_mode,
        "mode_label": "轻量模式" if actual_mode == "light" else "完整模式",
        "recommended_tier": recommended_tier,
        "recommended_tier_name": BUDGET_TIERS[recommended_tier]["name"],
        "team_detail": team_detail,
        "savings_detail": savings_detail,
        "annual_labor_cost": annual_labor_cost,
        "annual_savings_6months": annual_savings_6months,
        "annual_savings_2years": annual_savings_2years,
        "saving_ratio_6months": round(annual_savings_6months / annual_labor_cost * 100, 1) if annual_labor_cost > 0 else 0,
        "saving_ratio_2years": round(annual_savings_2years / annual_labor_cost * 100, 1) if annual_labor_cost > 0 else 0,
        "budget": budget,
        "payback_period": payback_period,
        "visible_tiers": visible_tiers,
        "hidden_costs": hidden_costs,
        "two_strategies": two_strategies,
        "mvp_roi": mvp_roi,
        "team_acceptance": team_acceptance,
        "digital_base": digital_base,
        "overall_adjustment": round(overall_adjust, 2),
    }


def format_currency(value):
    """格式化金额为万元或元"""
    if value >= 10000:
        return f"{value / 10000:.1f}万"
    return f"{value}元"


def main():
    parser = argparse.ArgumentParser(description="ROI五档测算引擎（v1.9.0）")
    parser.add_argument("--input", "-i", help="输入JSON文件路径或JSON字符串")
    parser.add_argument("--mode", choices=["light", "full", "auto"], default="auto",
                        help="强制指定模式：light(轻量)/full(完整)/auto(自动判断)")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    args = parser.parse_args()

    # 自测模式
    if args.self_test:
        test_cases = [
            {
                "name": "康源健康（30家门店连锁药店）- 完整模式",
                "input": {
                    "team_structure": {
                        "customer_service": {"count": 15, "avg_salary": 5000},
                        "content": {"count": 5, "avg_salary": 6000},
                        "operations": {"count": 8, "avg_salary": 7000},
                        "sales": {"count": 12, "avg_salary": 6000},
                        "admin_hr": {"count": 4, "avg_salary": 5000},
                    },
                    "budget": 300000,
                    "team_acceptance": "medium",
                    "digital_base": "medium",
                    "top_scenario": "智能客服",
                    "employee_count": 200,
                    "annual_revenue_wan": 8000,
                },
            },
            {
                "name": "小型会销企业（5家店，50人）- 轻量模式",
                "input": {
                    "team_structure": {
                        "customer_service": {"count": 5, "avg_salary": 4500},
                        "content": {"count": 3, "avg_salary": 5000},
                        "operations": {"count": 4, "avg_salary": 5500},
                        "sales": {"count": 30, "avg_salary": 5000},
                        "admin_hr": {"count": 3, "avg_salary": 4500},
                    },
                    "budget": 60000,
                    "team_acceptance": "low",
                    "digital_base": "weak",
                    "top_scenario": "AI内容生成",
                    "employee_count": 50,
                    "annual_revenue_wan": 2000,
                },
            },
            {
                "name": "微型企业（试水档）- 轻量模式",
                "input": {
                    "team_structure": {
                        "customer_service": {"count": 2, "avg_salary": 4000},
                        "content": {"count": 1, "avg_salary": 4500},
                        "operations": {"count": 1, "avg_salary": 5000},
                        "sales": {"count": 5, "avg_salary": 4500},
                        "admin_hr": {"count": 1, "avg_salary": 4000},
                    },
                    "budget": 20000,
                    "team_acceptance": "low",
                    "digital_base": "weak",
                    "top_scenario": "智能客服",
                    "employee_count": 10,
                    "annual_revenue_wan": 300,
                },
            },
        ]

        print("=" * 70)
        print("ROI五档测算引擎 v1.9.0 - 自测")
        print("=" * 70)

        all_passed = True
        for i, test in enumerate(test_cases, 1):
            result = calculate_roi(test["input"])
            print(f"\n【测试 {i}】{test['name']}")
            print(f"  模式: {result['mode_label']} (mode={result['mode']})")
            print(f"  推荐档位: {result['recommended_tier_name']}")
            print(f"  年人力成本: {format_currency(result['annual_labor_cost'])}")
            print(f"  预算: {format_currency(result['budget']) if result['budget'] else '未指定'}")
            print(f"  团队接受度: {result['team_acceptance']}, 数字化基础: {result['digital_base']}")
            print(f"  整体调整系数: {result['overall_adjustment']}")
            print(f"\n  年节省预估:")
            print(f"    6个月时: {format_currency(result['annual_savings_6months'])}/年 "
                  f"({result['saving_ratio_6months']}%人力成本)")
            print(f"    2年成熟时: {format_currency(result['annual_savings_2years'])}/年 "
                  f"({result['saving_ratio_2years']}%人力成本)")

            print(f"\n  五档回本周期（可见 {len(result['visible_tiers'])} 档）:")
            for tier_key in result["visible_tiers"]:
                pp = result["payback_period"][tier_key]
                rec_mark = " ⭐推荐" if pp["is_recommended"] else ""
                print(f"    {pp['tier_name']:6s} ({pp['budget_range']:>8s}): {pp['months']:>5.1f}个月"
                      f"  投入{format_currency(pp['total_investment'])},"
                      f"  年省{format_currency(pp['actual_annual_saving'])}"
                      f"{rec_mark}")

            # MVP ROI
            if result["mvp_roi"]:
                mvp = result["mvp_roi"]
                print(f"\n  MVP验证ROI（{mvp['scenario']}）:")
                print(f"    投入: {format_currency(mvp['mvp_cost'])}, 周期: {mvp['mvp_period_months']}个月")
                print(f"    预期月节省: {format_currency(mvp['expected_monthly_saving'])}")
                print(f"    成功率: {mvp['success_rate']*100:.0f}%, 回本周期: {mvp['payback_months']}个月")
                print(f"    首年净收益: {format_currency(mvp['first_year_net_saving'])}, ROI: {mvp['roi_ratio']}%")
                print(f"    验证KPI: {mvp['kpi']}")

            print(f"\n  两种策略:")
            print(f"    老板A式(消灭岗位): {result['two_strategies']['cut_staff']['payback']}回本")
            print(f"    老板B式(优化流程): {result['two_strategies']['boost_efficiency']['payback']}")

            # 校验
            passed = (
                result["annual_labor_cost"] > 0
                and result["annual_savings_6months"] > 0
                and result["annual_savings_2years"] > result["annual_savings_6months"]
                and len(result["payback_period"]) == 5
                and len(result["visible_tiers"]) >= 3
                and result["recommended_tier"] in result["visible_tiers"]
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

    # 如果命令行强制指定了模式
    if args.mode != "auto":
        input_data["mode"] = args.mode

    result = calculate_roi(input_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROI三档测算引擎
根据团队结构和预算，计算三档回本周期和隐性成本。
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

# ===== 三档参数 =====
SCENARIO_PARAMS = {
    "conservative": {
        "name": "保守档",
        "effect_factor": 0.5,    # 效果系数（实际节省 = 预期节省 × 系数）
        "hidden_cost_pct": 0.40,  # 隐性成本加成比例
        "description": "保守档，考虑团队接受度低和效果打折",
    },
    "moderate": {
        "name": "中性档",
        "effect_factor": 1.0,
        "hidden_cost_pct": 0.25,
        "description": "中性档，一般情况",
    },
    "optimistic": {
        "name": "乐观档",
        "effect_factor": 1.3,
        "hidden_cost_pct": 0.15,
        "description": "乐观档，基础好团队配合好",
    },
}

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


def calculate_roi(input_data):
    """
    计算ROI三档测算

    Args:
        input_data: dict，包含：
            - team_structure: 各团队人数和薪资
            - budget: 预算（元）
            - team_acceptance: low/medium/high
            - digital_base: weak/medium/strong

    Returns:
        dict，完整ROI分析结果
    """
    team_structure = input_data.get("team_structure", {})
    budget = input_data.get("budget", 0)
    team_acceptance = input_data.get("team_acceptance", "medium")
    digital_base = input_data.get("digital_base", "medium")

    if team_acceptance not in TEAM_ACCEPTANCE_ADJUST:
        team_acceptance = "medium"
    if digital_base not in DIGITAL_BASE_ADJUST:
        digital_base = "medium"

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

    # ===== 计算三档回本周期 =====
    # 使用2年时的年节省作为稳态基准
    baseline_saving = annual_savings_2years

    # 整体调整系数（团队接受度 × 数字化基础）
    overall_adjust = TEAM_ACCEPTANCE_ADJUST[team_acceptance] * DIGITAL_BASE_ADJUST[digital_base]

    payback_period = {}
    for scenario_key, params in SCENARIO_PARAMS.items():
        # 实际投入 = 预算 × (1 + 隐性成本比例)
        total_investment = budget * (1 + params["hidden_cost_pct"])
        # 实际年节省 = 基准年节省 × 效果系数 × 整体调整系数
        actual_saving = baseline_saving * params["effect_factor"] * overall_adjust

        if actual_saving > 0:
            payback_months = round(total_investment / actual_saving * 12, 1)
        else:
            payback_months = float("inf")

        payback_period[scenario_key] = {
            "months": payback_months,
            "total_investment": round(total_investment),
            "actual_annual_saving": round(actual_saving),
            "effect_factor": params["effect_factor"],
            "hidden_cost_pct": f"{int(params['hidden_cost_pct'] * 100)}%",
            "adjustment_factor": round(overall_adjust, 2),
            "description": params["description"],
        }

    # ===== 隐性成本明细 =====
    hidden_costs = {
        "one_time": {
            "系统部署与集成": round(budget * 0.10),
            "数据治理与迁移": round(budget * 0.08),
            "人员培训": round(budget * 0.05),
            "流程改造咨询": round(budget * 0.05),
        },
        "recurring": {
            "年订阅/维护费": f"约{round(budget * 0.15)}/年",
            "持续优化人力": "需1-2人兼职维护",
        },
        "total_percentage": f"{int(SCENARIO_PARAMS['moderate']['hidden_cost_pct'] * 100)}%",
        "conservative_pct": f"{int(SCENARIO_PARAMS['conservative']['hidden_cost_pct'] * 100)}%",
        "optimistic_pct": f"{int(SCENARIO_PARAMS['optimistic']['hidden_cost_pct'] * 100)}%",
    }

    # 计算一次性隐性成本总和
    one_time_total = sum(hidden_costs["one_time"].values())
    hidden_costs["one_time"]["小计"] = one_time_total

    # ===== 两种策略对比 =====
    # 老板A式：消灭岗位（直接裁员，节省人力成本）
    # 用6个月时的节省来算，见效快
    if annual_savings_6months > 0:
        cut_staff_payback_months = round(budget / annual_savings_6months * 12, 1)
        cut_staff_saving = annual_savings_6months
    else:
        cut_staff_payback_months = float("inf")
        cut_staff_saving = 0

    # 老板B式：优化流程（不裁人但提升效率）
    # 回本周期更快，因为没有裁员阵痛，但收益体现为产能提升
    boost_efficiency_note = "效率提升30-50%，同等人力承接更多业务"

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
        "team_detail": team_detail,
        "savings_detail": savings_detail,
        "annual_labor_cost": annual_labor_cost,
        "annual_savings_6months": annual_savings_6months,
        "annual_savings_2years": annual_savings_2years,
        "saving_ratio_6months": round(annual_savings_6months / annual_labor_cost * 100, 1) if annual_labor_cost > 0 else 0,
        "saving_ratio_2years": round(annual_savings_2years / annual_labor_cost * 100, 1) if annual_labor_cost > 0 else 0,
        "budget": budget,
        "payback_period": payback_period,
        "hidden_costs": hidden_costs,
        "two_strategies": two_strategies,
        "team_acceptance": team_acceptance,
        "digital_base": digital_base,
    }


def format_currency(value):
    """格式化金额为万元或元"""
    if value >= 10000:
        return f"{value / 10000:.1f}万"
    return f"{value}元"


def main():
    parser = argparse.ArgumentParser(description="ROI三档测算引擎")
    parser.add_argument("--input", "-i", help="输入JSON文件路径或JSON字符串")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    args = parser.parse_args()

    # 自测模式
    if args.self_test:
        test_cases = [
            {
                "name": "康源健康（30家门店连锁药店）",
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
                },
            },
            {
                "name": "小型企业（低预算）",
                "input": {
                    "team_structure": {
                        "customer_service": {"count": 3, "avg_salary": 4500},
                        "content": {"count": 1, "avg_salary": 5000},
                        "operations": {"count": 2, "avg_salary": 5500},
                        "sales": {"count": 5, "avg_salary": 5000},
                        "admin_hr": {"count": 1, "avg_salary": 4500},
                    },
                    "budget": 50000,
                    "team_acceptance": "low",
                    "digital_base": "weak",
                },
            },
        ]

        print("=" * 70)
        print("ROI三档测算引擎 - 自测")
        print("=" * 70)

        all_passed = True
        for i, test in enumerate(test_cases, 1):
            result = calculate_roi(test["input"])
            print(f"\n【测试 {i}】{test['name']}")
            print(f"  年人力成本: {format_currency(result['annual_labor_cost'])}")
            print(f"  预算: {format_currency(result['budget'])}")
            print(f"  团队接受度: {result['team_acceptance']}, 数字化基础: {result['digital_base']}")
            print(f"\n  年节省预估:")
            print(f"    6个月时: {format_currency(result['annual_savings_6months'])}/年 "
                  f"({result['saving_ratio_6months']}%人力成本)")
            print(f"    2年成熟时: {format_currency(result['annual_savings_2years'])}/年 "
                  f"({result['saving_ratio_2years']}%人力成本)")
            print(f"\n  回本周期（基于2年稳态节省）:")
            for key in ["conservative", "moderate", "optimistic"]:
                pp = result["payback_period"][key]
                print(f"    {pp['description']}: {pp['months']}个月 "
                      f"(投入{format_currency(pp['total_investment'])}, "
                      f"年省{format_currency(pp['actual_annual_saving'])})")

            print(f"\n  两种策略:")
            print(f"    老板A式(消灭岗位): {result['two_strategies']['cut_staff']['payback']}回本")
            print(f"    老板B式(优化流程): {result['two_strategies']['boost_efficiency']['payback']}")

            # 校验
            passed = (
                result["annual_labor_cost"] > 0
                and result["annual_savings_6months"] > 0
                and result["annual_savings_2years"] > result["annual_savings_6months"]
                and result["payback_period"]["conservative"]["months"] > result["payback_period"]["moderate"]["months"]
                and result["payback_period"]["moderate"]["months"] > result["payback_period"]["optimistic"]["months"]
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

    result = calculate_roi(input_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

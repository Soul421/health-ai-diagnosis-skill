#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五维度AI落地评分引擎（v1.9.0升级）
根据企业问卷答案计算5维度评分总分，支持按行业类型动态权重校准。
新增：轻量模式/完整模式自动判断，适配不同预算企业。
"""

import json
import sys
import argparse

# 动态权重配置（各维度权重占比，总和=100%）
WEIGHT_CONFIG = {
    "default": {
        "digital_base": 0.25,        # 数字化基础 25%
        "resource_readiness": 0.20,  # 资源准备度 20%
        "pain_urgency": 0.25,        # 痛点紧迫度 25%
        "team_acceptance": 0.15,     # 团队接受度 15%
        "compliance_risk": 0.15,     # 合规风险 15%
    },
    "medical": {
        # 医疗机构/药房：合规权重更高，团队接受度权重降低
        "digital_base": 0.25,
        "resource_readiness": 0.20,
        "pain_urgency": 0.20,
        "team_acceptance": 0.10,
        "compliance_risk": 0.25,
    },
    "online": {
        # 纯线上/电商：数字化基础权重更高
        "digital_base": 0.30,
        "resource_readiness": 0.20,
        "pain_urgency": 0.25,
        "team_acceptance": 0.10,
        "compliance_risk": 0.15,
    },
    "experiential": {
        # 体验营销/会销：团队接受度权重更高
        "digital_base": 0.25,
        "resource_readiness": 0.15,
        "pain_urgency": 0.25,
        "team_acceptance": 0.20,
        "compliance_risk": 0.15,
    },
}

# 各维度满分（用于归一化到百分制）
DIMENSION_MAX = {
    "digital_base": 25,
    "resource_readiness": 20,
    "pain_urgency": 25,
    "team_acceptance": 15,
    "compliance_risk": 15,
}

# 诊断结论映射表（百分制）- 完整版
CONCLUSION_MAP_FULL = [
    {"min": 85, "max": 100, "level": "S", "conclusion": "准备充分，建议立即启动全面AI落地"},
    {"min": 70, "max": 84, "level": "A", "conclusion": "条件较好，建议优先试点后快速推广"},
    {"min": 55, "max": 69, "level": "B", "conclusion": "有一定基础，建议先补短板再推进"},
    {"min": 0, "max": 54, "level": "C", "conclusion": "基础不足，建议先做数字化基础建设"},
]

# 诊断结论映射表（百分制）- 轻量版
# 轻量模式下结论更积极，鼓励从小处着手
CONCLUSION_MAP_LIGHT = [
    {"min": 85, "max": 100, "level": "S", "conclusion": "基础很好，建议立即启动轻量AI落地，2周见效"},
    {"min": 70, "max": 84, "level": "A", "conclusion": "条件不错，建议选1个痛点先做MVP验证"},
    {"min": 55, "max": 69, "level": "B", "conclusion": "可以起步，建议从内容生成或智能客服试水"},
    {"min": 40, "max": 54, "level": "C", "conclusion": "基础一般，但低成本试水没问题，先做起来"},
    {"min": 0, "max": 39, "level": "D", "conclusion": "基础较弱，建议先用免费工具试试水，培养感觉"},
]


def detect_mode(input_data):
    """
    根据企业特征自动判断模式

    判断逻辑：
    - 预算 < 20万 → 轻量模式
    - 员工 < 50人 → 轻量模式
    - 年营收 < 3000万 → 轻量模式
    - 门店 < 5家 → 轻量模式
    - 其他 → 完整模式
    """
    budget_wan = input_data.get("budget_wan")
    employee_count = input_data.get("employee_count")
    annual_revenue_wan = input_data.get("annual_revenue_wan")
    store_count = input_data.get("store_count")
    forced_mode = input_data.get("mode")

    if forced_mode and forced_mode in ["light", "full"]:
        return forced_mode

    # 预算判断（优先）
    if budget_wan is not None and budget_wan > 0:
        if budget_wan <= 20:
            return "light"
        if budget_wan >= 50:
            return "full"

    # 员工数判断
    if employee_count is not None and employee_count < 50:
        return "light"

    # 年营收判断
    if annual_revenue_wan is not None and annual_revenue_wan < 3000:
        return "light"

    # 门店数判断
    if store_count is not None and store_count < 5:
        return "light"

    # 默认完整模式
    return "full"


def calculate_score(input_data):
    """
    计算五维度综合评分

    Args:
        input_data: dict，包含以下字段：
            - industry_type: str，行业类型
            - digital_base: 数字化基础得分 (0-25)
            - resource_readiness: 资源准备度得分 (0-20)
            - pain_urgency: 痛点紧迫度得分 (0-25)
            - team_acceptance: 团队接受度得分 (0-15)
            - compliance_risk: 合规风险得分 (0-15，风险越低分越高)
            - mode: light/full/auto（可选）
            - budget_wan: 预算（万元，可选，用于模式判断）
            - employee_count: 员工数（可选）
            - annual_revenue_wan: 年营收（万元，可选）
            - store_count: 门店数（可选）

    Returns:
        dict，完整的评分结果
    """
    industry_type = input_data.get("industry_type", "default")
    if industry_type not in WEIGHT_CONFIG:
        industry_type = "default"

    weights = WEIGHT_CONFIG[industry_type]

    # 原始得分
    raw_scores = {
        "digital_base": input_data.get("digital_base", 0),
        "resource_readiness": input_data.get("resource_readiness", 0),
        "pain_urgency": input_data.get("pain_urgency", 0),
        "team_acceptance": input_data.get("team_acceptance", 0),
        "compliance_risk": input_data.get("compliance_risk", 0),
    }

    # 校验分数范围
    for dim, score in raw_scores.items():
        max_score = DIMENSION_MAX[dim]
        if score < 0:
            raw_scores[dim] = 0
        elif score > max_score:
            raw_scores[dim] = max_score

    # 计算加权得分
    weighted_scores = {}
    total_score = 0.0
    for dim in raw_scores:
        normalized = (raw_scores[dim] / DIMENSION_MAX[dim]) * 100
        weighted = normalized * weights[dim]
        weighted_scores[dim] = round(weighted, 1)
        total_score += weighted

    total_score = round(total_score, 1)

    # 自动判断模式
    mode = detect_mode(input_data)

    # 根据模式选择结论映射
    conclusion_map = CONCLUSION_MAP_LIGHT if mode == "light" else CONCLUSION_MAP_FULL
    level = conclusion_map[-1]["level"]
    conclusion = conclusion_map[-1]["conclusion"]
    for item in conclusion_map:
        if item["min"] <= total_score <= item["max"]:
            level = item["level"]
            conclusion = item["conclusion"]
            break

    return {
        "version": "1.9.0",
        "mode": mode,
        "mode_label": "轻量模式" if mode == "light" else "完整模式",
        "industry_type": industry_type,
        "raw_scores": raw_scores,
        "weights": weights,
        "weighted_scores": weighted_scores,
        "total_score": total_score,
        "conclusion": conclusion,
        "level": level,
    }


def main():
    parser = argparse.ArgumentParser(description="五维度AI落地评分引擎 v1.9.0")
    parser.add_argument("--input", "-i", help="输入JSON文件路径，或直接传入JSON字符串")
    parser.add_argument("--industry", default="default",
                        help="行业类型：default/medical/online/experiential")
    parser.add_argument("--digital-base", type=float, help="数字化基础得分 (0-25)")
    parser.add_argument("--resource-readiness", type=float, help="资源准备度得分 (0-20)")
    parser.add_argument("--pain-urgency", type=float, help="痛点紧迫度得分 (0-25)")
    parser.add_argument("--team-acceptance", type=float, help="团队接受度得分 (0-15)")
    parser.add_argument("--compliance-risk", type=float, help="合规风险得分 (0-15)")
    parser.add_argument("--mode", choices=["light", "full", "auto"], default="auto",
                        help="模式：light(轻量)/full(完整)/auto(自动)")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    args = parser.parse_args()

    # 自测模式
    if args.self_test:
        test_cases = [
            {
                "name": "康源健康（连锁药店，30家门店）- 完整模式",
                "input": {
                    "industry_type": "medical",
                    "digital_base": 18,
                    "resource_readiness": 13,
                    "pain_urgency": 19,
                    "team_acceptance": 11,
                    "compliance_risk": 9,
                    "budget_wan": 50,
                    "employee_count": 200,
                    "annual_revenue_wan": 8000,
                    "store_count": 30,
                },
            },
            {
                "name": "小型会销企业（5家店，50人）- 轻量模式",
                "input": {
                    "industry_type": "experiential",
                    "digital_base": 8,
                    "resource_readiness": 7,
                    "pain_urgency": 18,
                    "team_acceptance": 8,
                    "compliance_risk": 8,
                    "budget_wan": 6,
                    "employee_count": 50,
                    "annual_revenue_wan": 2000,
                    "store_count": 5,
                },
            },
            {
                "name": "微型企业（低分案例）- 轻量模式",
                "input": {
                    "industry_type": "default",
                    "digital_base": 5,
                    "resource_readiness": 3,
                    "pain_urgency": 10,
                    "team_acceptance": 4,
                    "compliance_risk": 5,
                    "budget_wan": 2,
                    "employee_count": 10,
                    "annual_revenue_wan": 300,
                    "store_count": 1,
                },
            },
        ]
        print("=" * 60)
        print("五维度评分引擎 v1.9.0 - 自测")
        print("=" * 60)
        all_passed = True
        for i, test in enumerate(test_cases, 1):
            result = calculate_score(test["input"])
            print(f"\n【测试 {i}】{test['name']}")
            print(f"  模式: {result['mode_label']} (mode={result['mode']})")
            print(f"  行业类型: {result['industry_type']}")
            print(f"  原始得分: {result['raw_scores']}")
            print(f"  加权得分: {result['weighted_scores']}")
            print(f"  总分: {result['total_score']} / 100")
            print(f"  等级: {result['level']}级")
            print(f"  结论: {result['conclusion']}")

            passed = (
                0 <= result["total_score"] <= 100
                and result["mode"] in ["light", "full"]
            )
            if not passed:
                all_passed = False
                print(f"  ❌ 校验失败!")
            else:
                print(f"  ✅ 正常")

        print("\n" + "=" * 60)
        if all_passed:
            print("所有测试通过 ✅")
        else:
            print("部分测试失败 ❌")
        print("=" * 60)
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
        input_data = {
            "industry_type": args.industry,
            "digital_base": args.digital_base if args.digital_base is not None else 0,
            "resource_readiness": args.resource_readiness if args.resource_readiness is not None else 0,
            "pain_urgency": args.pain_urgency if args.pain_urgency is not None else 0,
            "team_acceptance": args.team_acceptance if args.team_acceptance is not None else 0,
            "compliance_risk": args.compliance_risk if args.compliance_risk is not None else 0,
        }
        if args.mode != "auto":
            input_data["mode"] = args.mode
        if args.digital_base is None and args.resource_readiness is None:
            parser.print_help()
            return 1

    if args.mode != "auto":
        input_data["mode"] = args.mode

    result = calculate_score(input_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

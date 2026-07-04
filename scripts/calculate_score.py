#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五维度AI落地评分引擎
根据企业问卷答案计算5维度评分总分，支持按行业类型动态权重校准。
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

# 诊断结论映射表（百分制）
CONCLUSION_MAP = [
    {"min": 85, "max": 100, "level": "S", "conclusion": "准备充分，建议立即启动"},
    {"min": 70, "max": 84, "level": "A", "conclusion": "条件较好，建议优先试点"},
    {"min": 55, "max": 69, "level": "B", "conclusion": "有一定基础，建议先补短板"},
    {"min": 0, "max": 54, "level": "C", "conclusion": "基础不足，建议先做数字化基础建设"},
]


def calculate_score(input_data):
    """
    计算五维度综合评分

    Args:
        input_data: dict，包含以下字段：
            - industry_type: str，行业类型 (default/medical/online/experiential)
            - digital_base: int/float，数字化基础得分 (0-25)
            - resource_readiness: int/float，资源准备度得分 (0-20)
            - pain_urgency: int/float，痛点紧迫度得分 (0-25)
            - team_acceptance: int/float，团队接受度得分 (0-15)
            - compliance_risk: int/float，合规风险得分 (0-15，风险越低分越高)

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

    # 校验分数范围，确保不超过满分
    for dim, score in raw_scores.items():
        max_score = DIMENSION_MAX[dim]
        if score < 0:
            raw_scores[dim] = 0
        elif score > max_score:
            raw_scores[dim] = max_score

    # 计算加权得分（各维度先归一化到百分制，再加权）
    weighted_scores = {}
    total_score = 0.0
    for dim in raw_scores:
        # 归一化到100分制
        normalized = (raw_scores[dim] / DIMENSION_MAX[dim]) * 100
        # 应用权重
        weighted = normalized * weights[dim]
        weighted_scores[dim] = round(weighted, 1)
        total_score += weighted

    total_score = round(total_score, 1)

    # 确定等级和结论
    level = "C"
    conclusion = "基础不足，建议先做数字化基础建设"
    for item in CONCLUSION_MAP:
        if item["min"] <= total_score <= item["max"]:
            level = item["level"]
            conclusion = item["conclusion"]
            break

    return {
        "raw_scores": raw_scores,
        "weights": weights,
        "weighted_scores": weighted_scores,
        "total_score": total_score,
        "conclusion": conclusion,
        "level": level,
    }


def main():
    parser = argparse.ArgumentParser(description="五维度AI落地评分引擎")
    parser.add_argument("--input", "-i", help="输入JSON文件路径，或直接传入JSON字符串")
    parser.add_argument("--industry", default="default",
                        help="行业类型：default/medical/online/experiential")
    parser.add_argument("--digital-base", type=float, help="数字化基础得分 (0-25)")
    parser.add_argument("--resource-readiness", type=float, help="资源准备度得分 (0-20)")
    parser.add_argument("--pain-urgency", type=float, help="痛点紧迫度得分 (0-25)")
    parser.add_argument("--team-acceptance", type=float, help="团队接受度得分 (0-15)")
    parser.add_argument("--compliance-risk", type=float, help="合规风险得分 (0-15)")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    args = parser.parse_args()

    # 自测模式
    if args.self_test:
        test_cases = [
            {
                "name": "康源健康（连锁药店，30家门店）",
                "input": {
                    "industry_type": "medical",
                    "digital_base": 18,
                    "resource_readiness": 13,
                    "pain_urgency": 19,
                    "team_acceptance": 11,
                    "compliance_risk": 9,
                },
            },
            {
                "name": "默认行业 - 高分案例",
                "input": {
                    "industry_type": "default",
                    "digital_base": 23,
                    "resource_readiness": 18,
                    "pain_urgency": 22,
                    "team_acceptance": 13,
                    "compliance_risk": 12,
                },
            },
            {
                "name": "默认行业 - 低分案例",
                "input": {
                    "industry_type": "default",
                    "digital_base": 8,
                    "resource_readiness": 5,
                    "pain_urgency": 10,
                    "team_acceptance": 4,
                    "compliance_risk": 5,
                },
            },
        ]
        print("=" * 60)
        print("五维度评分引擎 - 自测")
        print("=" * 60)
        all_passed = True
        for i, test in enumerate(test_cases, 1):
            result = calculate_score(test["input"])
            print(f"\n【测试 {i}】{test['name']}")
            print(f"  行业类型: {test['input']['industry_type']}")
            print(f"  原始得分: {test['input']}")
            print(f"  加权得分: {result['weighted_scores']}")
            print(f"  总分: {result['total_score']} / 100")
            print(f"  等级: {result['level']}级")
            print(f"  结论: {result['conclusion']}")

            # 简单校验
            passed = 0 <= result["total_score"] <= 100
            if not passed:
                all_passed = False
                print(f"  ❌ 总分超出范围!")
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
        # 尝试从文件或字符串读取
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                input_data = json.load(f)
        except (FileNotFoundError, OSError):
            # 可能是JSON字符串
            try:
                input_data = json.loads(args.input)
            except json.JSONDecodeError:
                print(f"错误: 无法解析输入 '{args.input}'", file=sys.stderr)
                return 1
    elif not sys.stdin.isatty():
        # 从stdin读取
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            print("错误: 标准输入不是有效的JSON", file=sys.stderr)
            return 1
    else:
        # 使用命令行参数
        input_data = {
            "industry_type": args.industry,
            "digital_base": args.digital_base if args.digital_base is not None else 0,
            "resource_readiness": args.resource_readiness if args.resource_readiness is not None else 0,
            "pain_urgency": args.pain_urgency if args.pain_urgency is not None else 0,
            "team_acceptance": args.team_acceptance if args.team_acceptance is not None else 0,
            "compliance_risk": args.compliance_risk if args.compliance_risk is not None else 0,
        }
        if args.digital_base is None and args.resource_readiness is None:
            parser.print_help()
            return 1

    result = calculate_score(input_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

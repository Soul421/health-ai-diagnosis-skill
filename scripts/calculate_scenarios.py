#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI场景优先级动态计算引擎
根据企业特征动态计算10个AI场景的综合得分并排序。
"""

import json
import sys
import argparse

# ===== 基准得分表 =====
BASE_SCENARIOS = [
    {
        "name": "智能客服",
        "pain_match": 5,
        "tech_maturity": 5,
        "roi": 5,
        "difficulty": 2,
        "related_pains": ["客服人力成本高", "客户响应慢", "售后问题多", "客服质量不稳定", "客户咨询量大"],
    },
    {
        "name": "AI内容生成",
        "pain_match": 4,
        "tech_maturity": 4,
        "roi": 4,
        "difficulty": 1,
        "related_pains": ["缺乏内容创作能力", "内容产出效率低", "营销素材不足", "文案撰写慢", "社媒运营人力不足"],
    },
    {
        "name": "私域运营AI",
        "pain_match": 4,
        "tech_maturity": 4,
        "roi": 4,
        "difficulty": 3,
        "related_pains": ["私域转化低", "客户复购率低", "社群运营成本高", "会员活跃度低", "用户分层难"],
    },
    {
        "name": "数据分析AI",
        "pain_match": 3,
        "tech_maturity": 4,
        "roi": 4,
        "difficulty": 3,
        "related_pains": ["数据无法支撑决策", "报表制作效率低", "数据分散不统一", "缺乏数据分析能力"],
    },
    {
        "name": "AI培训助手",
        "pain_match": 3,
        "tech_maturity": 3,
        "roi": 3,
        "difficulty": 2,
        "related_pains": ["新员工培训成本高", "培训效果差", "知识传承难", "门店培训覆盖不足"],
    },
    {
        "name": "AI直播/数字人",
        "pain_match": 4,
        "tech_maturity": 3,
        "roi": 3,
        "difficulty": 4,
        "related_pains": ["直播人力成本高", "主播难招", "内容产出效率低", "品牌露出不足"],
    },
    {
        "name": "智能排班",
        "pain_match": 3,
        "tech_maturity": 3,
        "roi": 3,
        "difficulty": 4,
        "related_pains": ["排班效率低", "人力成本高", "门店人力调配难", "考勤管理复杂"],
    },
    {
        "name": "HR招聘AI",
        "pain_match": 3,
        "tech_maturity": 3,
        "roi": 3,
        "difficulty": 3,
        "related_pains": ["招聘效率低", "简历筛选成本高", "人才评估难", "HR人手不足"],
    },
    {
        "name": "AI诊断辅助",
        "pain_match": 5,
        "tech_maturity": 3,
        "roi": 4,
        "difficulty": 5,
        "related_pains": ["专业人员不足", "诊断效率低", "服务能力受限", "健康咨询人力成本高"],
    },
    {
        "name": "门店服务诊断",
        "pain_match": 4,
        "tech_maturity": 4,
        "roi": 4,
        "difficulty": 3,
        "related_pains": ["门店服务质量差", "门店管理难", "服务标准不统一", "客户满意度低", "门店督导成本高"],
    },
]

# ===== 边界约束 =====
BOUNDS = {
    "pain_match": {"min": 1, "max": 6},
    "tech_maturity": {"min": 1, "max": 5},
    "roi": {"min": 1, "max": 6},
    "difficulty": {"min": 1, "max": 6},
}

# ===== 综合得分权重（百分制加权） =====
# 痛点匹配度35% + ROI预期30% + 技术成熟度15% + 落地难度(反向)20%
SCORE_WEIGHTS = {
    "pain_match": 35,
    "roi": 30,
    "tech_maturity": 15,
    "difficulty": 20,  # 反向计分：难度越低分越高
}


def clamp(value, min_val, max_val):
    """限制值在范围内"""
    return max(min_val, min(max_val, value))


def calculate_scenarios(input_data):
    """
    计算场景优先级

    Args:
        input_data: dict，包含企业特征数据

    Returns:
        dict，包含场景排序列表和top3
    """
    top_pains = input_data.get("top_pains", [])
    pain_urgency = input_data.get("pain_urgency", {})  # 可选：{痛点名称: 星级}
    has_crm = input_data.get("has_crm", False)
    has_erp = input_data.get("has_erp", False)
    has_ai_experience = input_data.get("has_ai_experience", False)
    has_tech_team = input_data.get("has_tech_team", False)
    digital_systems_count = input_data.get("digital_systems_count", 0)
    customer_service_team_size = input_data.get("customer_service_team_size", 0)
    content_team_size = input_data.get("content_team_size", 0)
    store_count = input_data.get("store_count", 0)
    annual_revenue_level = input_data.get("annual_revenue_level", "")
    budget_level = input_data.get("budget_level", "")
    is_chain_store = input_data.get("is_chain_store", False)

    # 解析预算数值
    budget_num = _parse_budget(budget_level)
    # 解析营收数值（取下限）
    revenue_num = _parse_revenue(annual_revenue_level)

    results = []
    for scenario in BASE_SCENARIOS:
        s = {
            "name": scenario["name"],
            "pain_match": scenario["pain_match"],
            "tech_maturity": scenario["tech_maturity"],
            "roi": scenario["roi"],
            "difficulty": scenario["difficulty"],
            "related_pains": scenario["related_pains"],
        }

        # ===== 动态调整：痛点匹配度 =====
        # Top 3痛点对应场景各+1分
        matched_pain_count = 0
        for pain in top_pains[:3]:  # 只取前3个
            if _pain_matches_scenario(pain, scenario["related_pains"]):
                matched_pain_count += 1
        if matched_pain_count > 0:
            s["pain_match"] += matched_pain_count  # 每个匹配的痛点+1

        # 紧迫度5星+0.5分（如果提供了紧迫度信息）
        for pain in top_pains[:3]:
            urgency = pain_urgency.get(pain, 0)
            if urgency >= 5 and _pain_matches_scenario(pain, scenario["related_pains"]):
                s["pain_match"] += 0.5
                break  # 只加一次

        # ===== 动态调整：落地难度 =====
        # 无数字化系统所有场景+1（难度增加）
        if digital_systems_count == 0:
            s["difficulty"] += 1

        # 有CRM → 私域运营AI难度-1
        if has_crm and scenario["name"] == "私域运营AI":
            s["difficulty"] -= 1

        # 有ERP → 数据分析AI难度-1
        if has_erp and scenario["name"] == "数据分析AI":
            s["difficulty"] -= 1

        # 无技术团队 → 定制化场景难度+1
        if not has_tech_team:
            # 定制化程度高的场景：AI诊断辅助、智能排班、数据分析AI
            if scenario["name"] in ["AI诊断辅助", "智能排班", "数据分析AI"]:
                s["difficulty"] += 1

        # 有AI经验 → 所有场景难度-0.5
        if has_ai_experience:
            s["difficulty"] -= 0.5

        # ===== 动态调整：ROI预期 =====
        # 客服≥10人 → 智能客服ROI+1
        if customer_service_team_size >= 10 and scenario["name"] == "智能客服":
            s["roi"] += 1

        # 内容≥5人 → AI内容生成ROI+1
        if content_team_size >= 5 and scenario["name"] == "AI内容生成":
            s["roi"] += 1

        # 门店≥10家 → 门店服务诊断ROI+1
        if store_count >= 10 and scenario["name"] == "门店服务诊断":
            s["roi"] += 1

        # 连锁门店 → 门店服务诊断ROI再+0.5
        if is_chain_store and scenario["name"] == "门店服务诊断":
            s["roi"] += 0.5

        # 营收≥5000万 → 所有场景ROI+0.5
        if revenue_num >= 5000:
            s["roi"] += 0.5

        # 预算<5万 → 高成本场景ROI-1
        if budget_num > 0 and budget_num < 5:
            # 高成本场景（落地难度≥4的）
            if s["difficulty"] >= 4:
                s["roi"] -= 1

        # 预算≥50万 → 所有场景ROI+0.5
        if budget_num >= 50:
            s["roi"] += 0.5

        # ===== 边界约束 =====
        s["pain_match"] = clamp(s["pain_match"], BOUNDS["pain_match"]["min"], BOUNDS["pain_match"]["max"])
        s["tech_maturity"] = clamp(s["tech_maturity"], BOUNDS["tech_maturity"]["min"], BOUNDS["tech_maturity"]["max"])
        s["roi"] = clamp(s["roi"], BOUNDS["roi"]["min"], BOUNDS["roi"]["max"])
        s["difficulty"] = clamp(s["difficulty"], BOUNDS["difficulty"]["min"], BOUNDS["difficulty"]["max"])

        # ===== 计算综合得分（百分制加权） =====
        pain_score = (s["pain_match"] / BOUNDS["pain_match"]["max"]) * SCORE_WEIGHTS["pain_match"]
        tech_score = (s["tech_maturity"] / BOUNDS["tech_maturity"]["max"]) * SCORE_WEIGHTS["tech_maturity"]
        roi_score = (s["roi"] / BOUNDS["roi"]["max"]) * SCORE_WEIGHTS["roi"]
        # 落地难度反向计分：难度越低分越高
        diff_score = ((BOUNDS["difficulty"]["max"] - s["difficulty"] + 1) / BOUNDS["difficulty"]["max"]) * SCORE_WEIGHTS["difficulty"]

        total = round(pain_score + tech_score + roi_score + diff_score, 1)
        s["score"] = total

        # 四舍五入维度分数
        s["pain_match"] = round(s["pain_match"], 1)
        s["tech_maturity"] = round(s["tech_maturity"], 1)
        s["roi"] = round(s["roi"], 1)
        s["difficulty"] = round(s["difficulty"], 1)

        # 移除辅助字段
        s.pop("related_pains", None)

        results.append(s)

    # 按得分排序
    results.sort(key=lambda x: x["score"], reverse=True)

    # 添加排名
    for i, s in enumerate(results, 1):
        s["rank"] = i

    # Top 3
    top3 = [s["name"] for s in results[:3]]

    return {
        "scenarios": results,
        "top3": top3,
    }


def _pain_matches_scenario(pain_text, related_pains):
    """判断用户痛点是否与场景相关（简单关键词匹配）"""
    pain_text = pain_text.lower()
    for keyword in related_pains:
        # 检查关键词中的核心词是否出现在痛点文本中
        # 简单匹配：取关键词的前2-3个字符进行匹配
        if len(keyword) >= 2:
            # 直接匹配完整关键词
            if keyword in pain_text:
                return True
            # 关键词部分匹配（前两个字）
            if keyword[:2] in pain_text:
                return True
    return False


def _parse_budget(budget_level):
    """解析预算等级，返回万元数值（取下限）"""
    if not budget_level:
        return 0
    mapping = {
        "0-5万": 0,
        "<5万": 0,
        "5万以下": 0,
        "5-20万": 5,
        "20-50万": 20,
        "20-100万": 20,
        "50-100万": 50,
        "100万以上": 100,
        "100万+": 100,
    }
    if budget_level in mapping:
        return mapping[budget_level]
    # 尝试数字提取
    import re
    match = re.search(r'(\d+(?:\.\d+)?)\s*万', str(budget_level))
    if match:
        return float(match.group(1))
    return 0


def _parse_revenue(revenue_level):
    """解析营收等级，返回万元数值（取下限）"""
    if not revenue_level:
        return 0
    mapping = {
        "500万以下": 0,
        "500-1000万": 500,
        "1000-5000万": 1000,
        "5000万-1亿": 5000,
        "5000万以上": 5000,
        "1亿以上": 10000,
        "1亿-5亿": 10000,
        "5亿以上": 50000,
    }
    if revenue_level in mapping:
        return mapping[revenue_level]
    return 0


def main():
    parser = argparse.ArgumentParser(description="AI场景优先级动态计算引擎")
    parser.add_argument("--input", "-i", help="输入JSON文件路径或JSON字符串")
    parser.add_argument("--self-test", action="store_true", help="运行自测")
    args = parser.parse_args()

    # 自测模式
    if args.self_test:
        test_cases = [
            {
                "name": "康源健康（连锁药店，30家门店）",
                "input": {
                    "top_pains": ["门店服务质量差", "客服人力成本高", "缺乏内容创作能力"],
                    "has_crm": True,
                    "has_erp": False,
                    "has_ai_experience": False,
                    "has_tech_team": False,
                    "digital_systems_count": 3,
                    "customer_service_team_size": 15,
                    "content_team_size": 5,
                    "store_count": 30,
                    "annual_revenue_level": "5000万-1亿",
                    "budget_level": "20-100万",
                    "is_chain_store": True,
                },
            },
            {
                "name": "小型单店（低数字化基础）",
                "input": {
                    "top_pains": ["客服人力成本高", "内容产出效率低"],
                    "has_crm": False,
                    "has_erp": False,
                    "has_ai_experience": False,
                    "has_tech_team": False,
                    "digital_systems_count": 0,
                    "customer_service_team_size": 3,
                    "content_team_size": 1,
                    "store_count": 1,
                    "annual_revenue_level": "500万以下",
                    "budget_level": "5万以下",
                    "is_chain_store": False,
                },
            },
        ]

        print("=" * 70)
        print("AI场景优先级计算引擎 - 自测")
        print("=" * 70)

        all_passed = True
        for i, test in enumerate(test_cases, 1):
            result = calculate_scenarios(test["input"])
            print(f"\n【测试 {i}】{test['name']}")
            print(f"  Top 3痛点: {test['input']['top_pains']}")
            print(f"  门店数: {test['input']['store_count']}, 客服: {test['input']['customer_service_team_size']}人")
            print(f"  营收: {test['input']['annual_revenue_level']}, 预算: {test['input']['budget_level']}")
            print(f"\n  场景排名 (Top 5):")
            for s in result["scenarios"][:5]:
                print(f"    {s['rank']}. {s['name']:12s}  得分: {s['score']:5.1f}  "
                      f"[痛点:{s['pain_match']:.1f} 技术:{s['tech_maturity']:.1f} "
                      f"ROI:{s['roi']:.1f} 难度:{s['difficulty']:.1f}]")
            print(f"\n  Top 3推荐: {result['top3']}")

            # 校验
            passed = (
                len(result["scenarios"]) == 10
                and all(0 <= s["score"] <= 100 for s in result["scenarios"])
                and len(result["top3"]) == 3
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

    result = calculate_scenarios(input_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

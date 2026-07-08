#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI场景优先级动态计算引擎（v1.11.0升级）
根据企业特征动态计算10个AI场景的综合得分并排序。
支持轻量模式：优先推荐低成本快见效场景，增加"2周可落地"标记。
v1.11.0 新增：全场景工具化 - 每个场景输出工具推荐、预算明细、落地周期。
"""

import json
import sys
import os
import argparse

# ===== 本体知识库导入（v1.11.0 新增）=====
_HAS_ONTOLOGY = False
SCENARIO_BASELINE = {}
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ontology import SCENARIO_BASELINE as _ONTOLOGY_SCENARIOS
    SCENARIO_BASELINE = _ONTOLOGY_SCENARIOS
    _HAS_ONTOLOGY = True
except ImportError:
    pass

# ===== 场景名称到 ontology key 的映射（v1.11.0 新增）=====
SCENE_NAME_TO_ONTOLOGY_KEY = {
    "智能客服": "customer_service",
    "AI内容生成": "content_marketing",
    "私域运营AI": "private_domain",
    "数据分析AI": "data_analysis",
    "AI培训助手": "training_learning",
    "AI直播/数字人": "content_marketing",  # 暂映射到内容生成
    "智能排班": "supply_chain",  # 暂映射到供应链
    "HR招聘AI": "training_learning",  # 暂映射到培训
    "AI诊断辅助": "product_recommendation",  # 暂映射到产品推荐
    "门店服务诊断": "store_monitor",
}

# ===== 基准得分表 =====
BASE_SCENARIOS = [
    {
        "name": "智能客服",
        "pain_match": 5,
        "tech_maturity": 5,
        "roi": 5,
        "difficulty": 2,
        "implementation_weeks": 2,  # 落地周期（周）
        "quick_win": True,  # 是否快见效
        "light_weight": True,  # 是否轻量场景（低预算可落地）
        "related_pains": ["客服人力成本高", "客户响应慢", "售后问题多", "客服质量不稳定", "客户咨询量大"],
    },
    {
        "name": "AI内容生成",
        "pain_match": 4,
        "tech_maturity": 4,
        "roi": 4,
        "difficulty": 1,
        "implementation_weeks": 2,
        "quick_win": True,
        "light_weight": True,
        "related_pains": ["缺乏内容创作能力", "内容产出效率低", "营销素材不足", "文案撰写慢", "社媒运营人力不足"],
    },
    {
        "name": "私域运营AI",
        "pain_match": 4,
        "tech_maturity": 4,
        "roi": 4,
        "difficulty": 3,
        "implementation_weeks": 4,
        "quick_win": True,
        "light_weight": True,
        "related_pains": ["私域转化低", "客户复购率低", "社群运营成本高", "会员活跃度低", "用户分层难"],
    },
    {
        "name": "数据分析AI",
        "pain_match": 3,
        "tech_maturity": 4,
        "roi": 4,
        "difficulty": 3,
        "implementation_weeks": 4,
        "quick_win": False,
        "light_weight": True,
        "related_pains": ["数据无法支撑决策", "报表制作效率低", "数据分散不统一", "缺乏数据分析能力"],
    },
    {
        "name": "AI培训助手",
        "pain_match": 3,
        "tech_maturity": 3,
        "roi": 3,
        "difficulty": 2,
        "implementation_weeks": 2,
        "quick_win": True,
        "light_weight": True,
        "related_pains": ["新员工培训成本高", "培训效果差", "知识传承难", "门店培训覆盖不足"],
    },
    {
        "name": "AI直播/数字人",
        "pain_match": 4,
        "tech_maturity": 3,
        "roi": 3,
        "difficulty": 4,
        "implementation_weeks": 6,
        "quick_win": False,
        "light_weight": False,
        "related_pains": ["直播人力成本高", "主播难招", "内容产出效率低", "品牌露出不足"],
    },
    {
        "name": "智能排班",
        "pain_match": 3,
        "tech_maturity": 3,
        "roi": 3,
        "difficulty": 4,
        "implementation_weeks": 6,
        "quick_win": False,
        "light_weight": False,
        "related_pains": ["排班效率低", "人力成本高", "门店人力调配难", "考勤管理复杂"],
    },
    {
        "name": "HR招聘AI",
        "pain_match": 3,
        "tech_maturity": 3,
        "roi": 3,
        "difficulty": 3,
        "implementation_weeks": 4,
        "quick_win": False,
        "light_weight": True,
        "related_pains": ["招聘效率低", "简历筛选成本高", "人才评估难", "HR人手不足"],
    },
    {
        "name": "AI诊断辅助",
        "pain_match": 5,
        "tech_maturity": 3,
        "roi": 4,
        "difficulty": 5,
        "implementation_weeks": 12,
        "quick_win": False,
        "light_weight": False,
        "related_pains": ["专业人员不足", "诊断效率低", "服务能力受限", "健康咨询人力成本高"],
    },
    {
        "name": "门店服务诊断",
        "pain_match": 4,
        "tech_maturity": 4,
        "roi": 4,
        "difficulty": 3,
        "implementation_weeks": 4,
        "quick_win": True,
        "light_weight": True,
        "related_pains": ["门店服务质量差", "门店管理难", "服务标准不统一", "客户满意度低", "门店督导成本高"],
    },
]

# ===== 2周可落地场景集合（轻量模式MVP首选） =====
TWO_WEEK_SCENARIOS = ["智能客服", "AI内容生成", "AI培训助手"]

# ===== 轻量模式优先推荐场景（低成本快见效） =====
LIGHT_WEIGHT_PRIORITY = [
    "AI内容生成",  # 最容易上手，见效快
    "智能客服",    # ROI最明确
    "AI培训助手",  # 团队赋能，成本低
    "私域运营AI",  # 有一定基础后再上
    "门店服务诊断",  # 门店连锁后效果明显
    "数据分析AI",  # 需要数据基础
    "HR招聘AI",
    "AI直播/数字人",
    "智能排班",
    "AI诊断辅助",
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

# ===== 轻量模式额外权重 =====
# 轻量模式下：落地难度权重提升，ROI权重略微降低（更看重可落地性）
LIGHT_WEIGHT_WEIGHTS = {
    "pain_match": 30,
    "roi": 25,
    "tech_maturity": 15,
    "difficulty": 30,  # 难度权重提升：更偏好简单易落地
}


def clamp(value, min_val, max_val):
    """限制值在范围内"""
    return max(min_val, min(max_val, value))


def calculate_scenarios(input_data):
    """
    计算场景优先级

    Args:
        input_data: dict，包含企业特征数据
            - mode: light/full/auto（轻量/完整/自动）
            - 其他企业特征字段

    Returns:
        dict，包含场景排序列表和top3
    """
    top_pains = input_data.get("top_pains", [])
    pain_urgency = input_data.get("pain_urgency", {})
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
    mode = input_data.get("mode", "auto")

    # 解析预算数值
    budget_num = _parse_budget(budget_level)
    # 解析营收数值（取下限）
    revenue_num = _parse_revenue(annual_revenue_level)

    # ===== 自动判断模式 =====
    if mode == "auto":
        mode = _auto_detect_mode(budget_num=budget_num, revenue_num=revenue_num,
                                store_count=store_count,
                                digital_systems_count=digital_systems_count)

    # 选择权重配置
    if mode == "light":
        weights = LIGHT_WEIGHT_WEIGHTS
    else:
        weights = SCORE_WEIGHTS

    results = []
    for scenario in BASE_SCENARIOS:
        s = {
            "name": scenario["name"],
            "pain_match": scenario["pain_match"],
            "tech_maturity": scenario["tech_maturity"],
            "roi": scenario["roi"],
            "difficulty": scenario["difficulty"],
            "implementation_weeks": scenario["implementation_weeks"],
            "quick_win": scenario["quick_win"],
            "light_weight": scenario["light_weight"],
            "two_week_launch": scenario["name"] in TWO_WEEK_SCENARIOS,
            "related_pains": scenario["related_pains"],
        }

        # ===== 动态调整：痛点匹配度 =====
        # Top 3痛点对应场景各+1分
        matched_pain_count = 0
        for pain in top_pains[:3]:
            if _pain_matches_scenario(pain, scenario["related_pains"]):
                matched_pain_count += 1
        if matched_pain_count > 0:
            s["pain_match"] += matched_pain_count

        # 紧迫度5星+0.5分
        for pain in top_pains[:3]:
            urgency = pain_urgency.get(pain, 0)
            if urgency >= 5 and _pain_matches_scenario(pain, scenario["related_pains"]):
                s["pain_match"] += 0.5
                break

        # ===== 动态调整：落地难度 =====
        if digital_systems_count == 0:
            s["difficulty"] += 1

        if has_crm and scenario["name"] == "私域运营AI":
            s["difficulty"] -= 1

        if has_erp and scenario["name"] == "数据分析AI":
            s["difficulty"] -= 1

        if not has_tech_team:
            if scenario["name"] in ["AI诊断辅助", "智能排班", "数据分析AI"]:
                s["difficulty"] += 1

        if has_ai_experience:
            s["difficulty"] -= 0.5

        # ===== 动态调整：ROI预期 =====
        if customer_service_team_size >= 10 and scenario["name"] == "智能客服":
            s["roi"] += 1

        if content_team_size >= 5 and scenario["name"] == "AI内容生成":
            s["roi"] += 1

        if store_count >= 10 and scenario["name"] == "门店服务诊断":
            s["roi"] += 1

        if is_chain_store and scenario["name"] == "门店服务诊断":
            s["roi"] += 0.5

        if revenue_num >= 5000:
            s["roi"] += 0.5

        if budget_num > 0 and budget_num < 5:
            if s["difficulty"] >= 4:
                s["roi"] -= 1

        if budget_num >= 50:
            s["roi"] += 0.5

        # ===== 轻量模式特有调整 =====
        if mode == "light":
            # 轻量场景额外加成：ROI +0.5，难度 -0.5
            if s["light_weight"]:
                s["roi"] += 0.5
                s["difficulty"] -= 0.5

            # 2周可落地场景额外加分：ROI +0.5，痛点匹配 +0.5（快速见效心理优势）
            if s["two_week_launch"]:
                s["roi"] += 0.5
                s["pain_match"] += 0.5

            # 非轻量场景（重投入场景）降低权重：ROI -1，难度 +1
            if not s["light_weight"]:
                s["roi"] -= 1
                s["difficulty"] += 1

        # ===== 边界约束 =====
        s["pain_match"] = clamp(s["pain_match"], BOUNDS["pain_match"]["min"], BOUNDS["pain_match"]["max"])
        s["tech_maturity"] = clamp(s["tech_maturity"], BOUNDS["tech_maturity"]["min"], BOUNDS["tech_maturity"]["max"])
        s["roi"] = clamp(s["roi"], BOUNDS["roi"]["min"], BOUNDS["roi"]["max"])
        s["difficulty"] = clamp(s["difficulty"], BOUNDS["difficulty"]["min"], BOUNDS["difficulty"]["max"])

        # ===== 计算综合得分（百分制加权） =====
        pain_score = (s["pain_match"] / BOUNDS["pain_match"]["max"]) * weights["pain_match"]
        tech_score = (s["tech_maturity"] / BOUNDS["tech_maturity"]["max"]) * weights["tech_maturity"]
        roi_score = (s["roi"] / BOUNDS["roi"]["max"]) * weights["roi"]
        diff_score = ((BOUNDS["difficulty"]["max"] - s["difficulty"] + 1) / BOUNDS["difficulty"]["max"]) * weights["difficulty"]

        total = round(pain_score + tech_score + roi_score + diff_score, 1)
        s["score"] = total

        # 四舍五入维度分数
        s["pain_match"] = round(s["pain_match"], 1)
        s["tech_maturity"] = round(s["tech_maturity"], 1)
        s["roi"] = round(s["roi"], 1)
        s["difficulty"] = round(s["difficulty"], 1)

        # 添加标签
        tags = []
        if s["two_week_launch"]:
            tags.append("2周可落地")
        if s["quick_win"]:
            tags.append("快见效")
        if s["light_weight"]:
            tags.append("轻量场景")
        else:
            tags.append("重投入")
        s["tags"] = tags

        # ===== v1.11.0 新增：从本体知识库获取工具/预算/时间线 =====
        tool_info = _get_scenario_tools(scenario["name"])
        if tool_info:
            s["tools"] = tool_info["tools"]
            s["budget"] = tool_info["budget"]
            s["timeline"] = tool_info["timeline"]

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

    # 轻量模式MVP首选（2周可落地且得分最高的）
    mvp_candidates = [s for s in results if s["two_week_launch"]]
    mvp_first = mvp_candidates[0]["name"] if mvp_candidates else top3[0]

    # ===== v1.11.0 新增：预算档位推荐和总预算估算 =====
    recommended_tier = _recommend_budget_tier(input_data)
    total_budget = _calculate_total_budget(results[:3], recommended_tier)

    return {
        "version": "1.11.0",
        "mode": mode,
        "mode_label": "轻量模式" if mode == "light" else "完整模式",
        "scenarios": results,
        "top3": top3,
        "mvp_first_choice": mvp_first,
        "two_week_scenarios": [s["name"] for s in results if s["two_week_launch"]],
        "light_weight_scenarios": [s["name"] for s in results if s["light_weight"]],
        "recommended_tier": recommended_tier,
        "recommended_tier_label": {"light": "轻量版", "standard": "标准版", "advanced": "进阶版"}.get(recommended_tier, "标准版"),
        "top3_budget_estimate": total_budget,
    }


def _auto_detect_mode(budget_num=0, revenue_num=0, store_count=0, digital_systems_count=0):
    """自动判断模式"""
    # 预算低于5万 → 轻量模式
    if budget_num > 0 and budget_num < 5:
        return "light"
    # 营收低于2000万 → 轻量模式
    if revenue_num > 0 and revenue_num < 2000:
        return "light"
    # 门店少于5家且数字化系统少于2个 → 轻量模式
    if store_count < 5 and digital_systems_count < 2:
        return "light"
    # 默认完整模式
    return "full"


# ===== v1.11.0 新增：工具化辅助函数 =====

def _get_scenario_tools(scene_name):
    """从本体知识库获取场景的工具、预算、时间线信息"""
    if not _HAS_ONTOLOGY:
        return None
    ontology_key = SCENE_NAME_TO_ONTOLOGY_KEY.get(scene_name)
    if not ontology_key:
        return None
    scenario_data = SCENARIO_BASELINE.get(ontology_key)
    if not scenario_data:
        return None
    return {
        "tools": scenario_data.get("tools", {}),
        "budget": scenario_data.get("budget", {}),
        "timeline": scenario_data.get("timeline", []),
    }


def _recommend_budget_tier(input_data):
    """根据企业规模推荐预算档位
    返回: light / standard / advanced
    """
    revenue_num = _parse_revenue(input_data.get("annual_revenue_level", ""))
    employee_count = input_data.get("employee_count", 0)
    store_count = input_data.get("store_count", 0)
    budget_num = _parse_budget(input_data.get("budget_level", ""))

    # 明确预算充足直接推荐高级版
    if budget_num >= 50:
        return "advanced"
    if budget_num >= 10 and budget_num < 50:
        return "standard"
    if budget_num > 0 and budget_num < 10:
        return "light"

    # 根据营收判断
    if revenue_num >= 10000:  # 1亿以上
        return "advanced"
    if revenue_num >= 1000 and revenue_num < 10000:  # 1000万-1亿
        return "standard"
    if revenue_num < 1000 and revenue_num > 0:  # 1000万以下
        return "light"

    # 根据员工数判断
    if employee_count >= 200:
        return "advanced"
    if employee_count >= 50 and employee_count < 200:
        return "standard"
    if employee_count > 0 and employee_count < 50:
        return "light"

    # 根据门店数判断
    if store_count >= 50:
        return "advanced"
    if store_count >= 10 and store_count < 50:
        return "standard"

    # 默认标准版
    return "standard"


def _calculate_total_budget(top_scenarios, tier):
    """计算Top N场景的总预算估算（元→万元显示）"""
    total_first_year = 0
    total_recurring = 0
    for s in top_scenarios:
        if "budget" in s and tier in s["budget"]:
            b = s["budget"][tier]
            total_first_year += b.get("first_year_total", 0)
            total_recurring += b.get("recurring_year_total", 0)
    return {
        "tier": tier,
        "first_year_total_wan": round(total_first_year / 10000, 1),
        "recurring_total_wan": round(total_recurring / 10000, 1),
    }


def _pain_matches_scenario(pain_text, related_pains):
    """判断用户痛点是否与场景相关（简单关键词匹配）"""
    pain_text = pain_text.lower()
    for keyword in related_pains:
        if len(keyword) >= 2:
            if keyword in pain_text:
                return True
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
    parser = argparse.ArgumentParser(description="AI场景优先级计算引擎 v1.9.0")
    parser.add_argument("--input", "-i", help="输入JSON文件路径或JSON字符串")
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
                    "mode": "full",
                },
            },
            {
                "name": "小型会销企业（5家店）- 轻量模式",
                "input": {
                    "top_pains": ["客服人力成本高", "内容产出效率低", "获客成本越来越高"],
                    "has_crm": False,
                    "has_erp": False,
                    "has_ai_experience": False,
                    "has_tech_team": False,
                    "digital_systems_count": 1,
                    "customer_service_team_size": 5,
                    "content_team_size": 3,
                    "store_count": 5,
                    "annual_revenue_level": "1000-5000万",
                    "budget_level": "5-20万",
                    "is_chain_store": False,
                    "mode": "light",
                },
            },
            {
                "name": "微型单店（低数字化基础）- 自动模式(轻量)",
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
                    "mode": "auto",
                },
            },
        ]

        print("=" * 70)
        print("AI场景优先级计算引擎 v1.11.0 - 自测")
        print("=" * 70)

        all_passed = True
        for i, test in enumerate(test_cases, 1):
            result = calculate_scenarios(test["input"])
            print(f"\n【测试 {i}】{test['name']}")
            print(f"  模式: {result['mode_label']} (mode={result['mode']})")
            print(f"  推荐档位: {result['recommended_tier_label']}")
            print(f"  Top 3痛点: {test['input']['top_pains']}")
            print(f"  门店数: {test['input']['store_count']}, 客服: {test['input']['customer_service_team_size']}人")
            print(f"  营收: {test['input']['annual_revenue_level']}, 预算: {test['input']['budget_level']}")
            print(f"\n  场景排名 (Top 5):")
            for s in result["scenarios"][:5]:
                tag_str = " ".join([f"[{t}]" for t in s["tags"]])
                has_tools = "✓工具" if "tools" in s and s["tools"] else " "
                print(f"    {s['rank']}. {s['name']:12s}  得分: {s['score']:5.1f}  "
                      f"[痛点:{s['pain_match']:.1f} 技术:{s['tech_maturity']:.1f} "
                      f"ROI:{s['roi']:.1f} 难度:{s['difficulty']:.1f}] "
                      f"{tag_str} {has_tools}")
            print(f"\n  Top 3推荐: {result['top3']}")
            print(f"  MVP首选: {result['mvp_first_choice']}")
            print(f"  2周可落地: {result['two_week_scenarios']}")
            if result["top3_budget_estimate"]["first_year_total_wan"] > 0:
                print(f"  Top3首年预算({result['recommended_tier_label']}): {result['top3_budget_estimate']['first_year_total_wan']}万")
                print(f"  Top3次年续费({result['recommended_tier_label']}): {result['top3_budget_estimate']['recurring_total_wan']}万")

            # 校验
            passed = (
                len(result["scenarios"]) == 10
                and all(0 <= s["score"] <= 100 for s in result["scenarios"])
                and len(result["top3"]) == 3
                and "two_week_scenarios" in result
                and "light_weight_scenarios" in result
                and "recommended_tier" in result
                and "top3_budget_estimate" in result
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

    if args.mode != "auto":
        input_data["mode"] = args.mode

    result = calculate_scenarios(input_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

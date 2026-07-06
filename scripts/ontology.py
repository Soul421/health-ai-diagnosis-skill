#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康行业AI落地诊断 - 本体知识库（Ontology）
=============================================
结构化的领域先验知识，所有脚本统一调用，确保口径一致。

对应 cognee 借鉴点5：本体知识注入（领域先验知识结构化）
包含：行业配置、维度定义、场景基准、ROI参数、合规红线、坑点清单
"""

import json
from typing import Dict, List, Any

# ============================================================
# 一、行业配置（动态权重）
# ============================================================
INDUSTRY_WEIGHT_CONFIG = {
    "default": {
        "label": "通用健康行业",
        "digital_base": 0.25,
        "resource_readiness": 0.20,
        "pain_urgency": 0.25,
        "team_acceptance": 0.15,
        "compliance_risk": 0.15,
    },
    "medical": {
        "label": "医疗机构/药房",
        "digital_base": 0.25,
        "resource_readiness": 0.20,
        "pain_urgency": 0.20,
        "team_acceptance": 0.10,
        "compliance_risk": 0.25,
    },
    "online": {
        "label": "纯线上/电商",
        "digital_base": 0.30,
        "resource_readiness": 0.20,
        "pain_urgency": 0.25,
        "team_acceptance": 0.10,
        "compliance_risk": 0.15,
    },
    "experiential": {
        "label": "体验营销/会销",
        "digital_base": 0.25,
        "resource_readiness": 0.15,
        "pain_urgency": 0.25,
        "team_acceptance": 0.20,
        "compliance_risk": 0.15,
    },
    "chain_store": {
        "label": "连锁门店/保健品店",
        "digital_base": 0.20,
        "resource_readiness": 0.25,
        "pain_urgency": 0.25,
        "team_acceptance": 0.15,
        "compliance_risk": 0.15,
    },
}

# ============================================================
# 二、维度定义（五维度评分体系）
# ============================================================
DIMENSION_DEFS = {
    "digital_base": {
        "label": "数字化基础",
        "max_score": 25,
        "description": "企业现有数字化系统、数据积累、IT基础设施水平",
        "sub_dimensions": ["系统覆盖度", "数据质量", "IT投入"],
    },
    "resource_readiness": {
        "label": "资源准备度",
        "max_score": 20,
        "description": "预算、人力、时间等资源配置情况",
        "sub_dimensions": ["预算充足度", "人力配置", "管理层支持"],
    },
    "pain_urgency": {
        "label": "痛点紧迫度",
        "max_score": 25,
        "description": "当前业务痛点的严重程度和AI解决的匹配度",
        "sub_dimensions": ["人力成本压力", "效率瓶颈", "客户流失"],
    },
    "team_acceptance": {
        "label": "团队接受度",
        "max_score": 15,
        "description": "员工对AI工具的接受意愿和学习能力",
        "sub_dimensions": ["年龄结构", "学习意愿", "变革阻力"],
    },
    "compliance_risk": {
        "label": "合规风险",
        "max_score": 15,
        "description": "行业监管严格程度及AI应用的合规挑战",
        "sub_dimensions": ["数据合规", "营销合规", "医疗合规"],
    },
}

# 诊断结论映射（百分制）
SCORE_CONCLUSION_MAP = [
    {"min": 85, "max": 100, "level": "S", "conclusion": "准备充分，建议立即启动", "action": "全速推进，3个月内完成核心场景落地"},
    {"min": 70, "max": 84, "level": "A", "conclusion": "条件较好，建议优先试点", "action": "选择1-2个高ROI场景试点，6个月内验证"},
    {"min": 55, "max": 69, "level": "B", "conclusion": "有一定基础，建议先补短板", "action": "补齐数据/团队短板后，再启动AI项目"},
    {"min": 40, "max": 54, "level": "C", "conclusion": "基础薄弱，建议谨慎投入", "action": "从低成本工具入手，逐步建立数字化能力"},
    {"min": 0, "max": 39, "level": "D", "conclusion": "暂不适合大规模AI投入", "action": "先完成数字化基础建设，1-2年后再考虑AI"},
]

# ============================================================
# 三、场景基准（10大AI落地场景）
# ============================================================
SCENARIO_BASELINE = {
    "customer_service": {
        "label": "智能客服/咨询",
        "category": "客户服务",
        "base_saving": 0.35,
        "implementation_cycle": "1-2个月",
        "difficulty": 2,
        "risk_level": "低",
        "typical_cost_range": [2, 8],
        "fit_industries": ["all"],
        "description": "AI客服机器人承接70%以上常见咨询，降低客服人力成本",
    },
    "content_marketing": {
        "label": "AI内容营销",
        "category": "市场营销",
        "base_saving": 0.40,
        "implementation_cycle": "1个月",
        "difficulty": 1,
        "risk_level": "低",
        "typical_cost_range": [1, 5],
        "fit_industries": ["all"],
        "description": "AI批量生成软文、海报文案、短视频脚本，提升内容产出效率",
    },
    "sales_assistant": {
        "label": "销售助手/陪练",
        "category": "销售赋能",
        "base_saving": 0.25,
        "implementation_cycle": "2-3个月",
        "difficulty": 3,
        "risk_level": "中",
        "typical_cost_range": [5, 15],
        "fit_industries": ["experiential", "chain_store"],
        "description": "AI销售话术推荐、客户画像分析、新人陪练，提升成单率",
    },
    "data_analysis": {
        "label": "智能数据分析",
        "category": "数据决策",
        "base_saving": 0.30,
        "implementation_cycle": "2个月",
        "difficulty": 3,
        "risk_level": "低",
        "typical_cost_range": [3, 10],
        "fit_industries": ["all"],
        "description": "AI自动分析经营数据、生成报告、发现异常，替代80%基础分析工作",
    },
    "training_learning": {
        "label": "AI培训/知识库",
        "category": "人才发展",
        "base_saving": 0.35,
        "implementation_cycle": "1-2个月",
        "difficulty": 2,
        "risk_level": "低",
        "typical_cost_range": [2, 8],
        "fit_industries": ["all"],
        "description": "企业知识库+AI问答，新人培训周期缩短50%，产品知识随时查询",
    },
    "store_monitor": {
        "label": "门店服务监控",
        "category": "门店管理",
        "base_saving": 0.20,
        "implementation_cycle": "2-3个月",
        "difficulty": 3,
        "risk_level": "中",
        "typical_cost_range": [5, 20],
        "fit_industries": ["chain_store", "medical", "experiential"],
        "description": "录音/录像AI分析门店服务质量，自动发现合规问题和服务短板",
    },
    "supply_chain": {
        "label": "供应链优化",
        "category": "运营效率",
        "base_saving": 0.15,
        "implementation_cycle": "3-6个月",
        "difficulty": 4,
        "risk_level": "中",
        "typical_cost_range": [10, 30],
        "fit_industries": ["chain_store", "online"],
        "description": "AI需求预测、智能补货、库存优化，降低库存成本和缺货率",
    },
    "private_domain": {
        "label": "私域运营自动化",
        "category": "市场营销",
        "base_saving": 0.30,
        "implementation_cycle": "1-2个月",
        "difficulty": 2,
        "risk_level": "低",
        "typical_cost_range": [2, 10],
        "fit_industries": ["all"],
        "description": "AI社群运营、个性化推送、客户分层，提升私域转化率和复购",
    },
    "quality_control": {
        "label": "智能质检/合规",
        "category": "合规风控",
        "base_saving": 0.40,
        "implementation_cycle": "2-3个月",
        "difficulty": 3,
        "risk_level": "高",
        "typical_cost_range": [5, 15],
        "fit_industries": ["medical", "chain_store", "experiential"],
        "description": "AI自动检测营销内容合规性、产品质量问题，降低罚款和投诉风险",
    },
    "product_recommendation": {
        "label": "智能推荐/选品",
        "category": "销售赋能",
        "base_saving": 0.20,
        "implementation_cycle": "2个月",
        "difficulty": 3,
        "risk_level": "中",
        "typical_cost_range": [3, 12],
        "fit_industries": ["online", "chain_store", "experiential"],
        "description": "基于客户画像的AI产品推荐，提升客单价和交叉销售率",
    },
}

# ============================================================
# 四、ROI计算参数
# ============================================================
ROI_PARAMS = {
    "hidden_cost_factor": {
        "year1": 1.0,   # 首年隐性成本 = 软件费 × 1.0（数据清洗+培训+审核+维护）
        "year2": 0.5,   # 第二年减半
        "year3": 0.3,   # 第三年趋于稳定
    },
    "payback_gears": [
        {"gear": "保守档", "saving_rate_multiplier": 0.5, "cost_multiplier": 1.2},
        {"gear": "基准档", "saving_rate_multiplier": 1.0, "cost_multiplier": 1.0},
        {"gear": "激进档", "saving_rate_multiplier": 1.5, "cost_multiplier": 0.8},
    ],
    "implementation_cycle_months": {
        "pilot": 2,     # 试点期
        "rollout": 4,   # 推广期
        "stable": 6,    # 稳态运营（开始计算完整收益）
    },
}

# ============================================================
# 五、合规红线（健康行业禁用词/风险点）
# ============================================================
COMPLIANCE_RULES = {
    "banned_words_medical": [
        "治愈", "根治", "痊愈", "药到病除", "包治百病", "神药",
        "最佳", "第一", "顶级", "唯一", "国家级", "最高级",
        "无效退款", "100%有效", "绝对安全", "无毒副作用",
    ],
    "banned_words_food": [
        "治疗", "预防疾病", "诊断", "处方", "药用",
        "防癌", "抗癌", "降血压", "降血糖", "减肥",
    ],
    "risk_levels": {
        "high": "可能面临20万以上罚款，严重者吊销执照",
        "medium": "可能面临投诉举报和市场监管约谈",
        "low": "存在合规瑕疵，建议优化表述",
    },
}

# ============================================================
# 六、落地坑点清单（Top 25）
# ============================================================
PITFALL_LIST = [
    {"id": "P001", "category": "合规", "severity": "critical",
     "title": "红线词地雷", "content": "AI写文案爱用治愈、根治、最佳等禁用词，罚款20万起。必须建敏感词库+人工复核双保险。"},
    {"id": "P002", "category": "组织", "severity": "high",
     "title": "员工软抵抗", "content": "表面配合实际不用、故意用错证明AI不行、抱团抵制——找年轻种子员工当突破口，店长必须带头用。"},
    {"id": "P003", "category": "数据", "severity": "high",
     "title": "数据质量差", "content": "中老年客户手机号换号率30%+、信息是子女填的。AI项目启动前必须先做数据清洗，脏数据不如不用。"},
    {"id": "P004", "category": "成本", "severity": "high",
     "title": "隐性成本冰山", "content": "只算软件费是自欺欺人——数据清洗、内容审核、培训、维护，隐性成本是显性的1倍。首年预算=软件费×2。"},
    {"id": "P005", "category": "内容", "severity": "medium",
     "title": "内容同质化", "content": "大家都用同一个大模型，文案越来越像，客户审美疲劳。必须建公司专属语料库，AI出稿后人改10%保差异化。"},
    {"id": "P006", "category": "技术", "severity": "medium",
     "title": "选型盲目追新", "content": "什么火上什么，从GPT到Agent到数字人，一年换三波。选一个痛点打穿，比十个浅尝辄止强。"},
    {"id": "P007", "category": "组织", "severity": "high",
     "title": "没有Owner", "content": "AI项目交给IT或运营代管，没人对最终结果负责。必须指定业务侧负责人，老板直接挂帅。"},
    {"id": "P008", "category": "数据", "severity": "medium",
     "title": "数据安全隐患", "content": "客户健康数据上传公网大模型，一旦泄露就是灭顶之灾。必须用私有化部署或脱敏后再调用。"},
    {"id": "P009", "category": "内容", "severity": "critical",
     "title": "医疗建议越界", "content": "AI客服给客户诊疗建议、推荐用药，涉嫌非法行医。话术必须限定在产品介绍范围内，严禁医疗建议。"},
    {"id": "P010", "category": "成本", "severity": "medium",
     "title": "Token费用失控", "content": "初期免费额度够用，上量后账单爆炸。必须设用量上限和告警，长文本用摘要压缩后再送模型。"},
    {"id": "P011", "category": "组织", "severity": "medium",
     "title": "培训走过场", "content": "发个操作手册就算培训完了，员工根本不会用。必须做场景化培训+实操考核+师傅带徒弟。"},
    {"id": "P012", "category": "技术", "severity": "low",
     "title": "过度定制化", "content": "什么功能都想要定制，项目越做越重。先用SaaS跑通流程，真有必要再定制。"},
    {"id": "P013", "category": "数据", "severity": "low",
     "title": "指标虚荣", "content": "追求AI覆盖率、对话量等虚荣指标，不看实际业务结果。只盯一个指标：省了多少钱/赚了多少钱。"},
    {"id": "P014", "category": "合规", "severity": "high",
     "title": "客户授权缺失", "content": "没拿到客户明确授权就用其数据训练AI，涉嫌违反个人信息保护法。必须有书面授权或明确告知。"},
    {"id": "P015", "category": "内容", "severity": "medium",
     "title": "人设崩塌", "content": "AI客服语气忽冷忽热、答非所问，客户体验还不如人工。必须严格定义人设和话术边界，定期抽检。"},
    {"id": "P016", "category": "组织", "severity": "low",
     "title": "部门墙阻隔", "content": "运营要数据销售不给、客服要知识库市场不配合。老板不拍板推动，AI项目必卡。"},
    {"id": "P017", "category": "技术", "severity": "medium",
     "title": "集成烂尾", "content": "AI工具和现有系统打通不了，数据两头跑，员工嫌麻烦不用。选型前先确认接口能力。"},
    {"id": "P018", "category": "成本", "severity": "low",
     "title": "重复采购", "content": "各部门各买各的AI工具，功能重叠浪费钱。统一采购、统一账号，按部门分配权限。"},
    {"id": "P019", "category": "合规", "severity": "medium",
     "title": "广告法风险", "content": "AI生成的宣传材料违反广告法，企业担责不担AI的责。所有对外内容必须人工审核后再发。"},
    {"id": "P020", "category": "数据", "severity": "high",
     "title": "数据孤岛", "content": "销售数据在企微、客服数据在工单、会员数据在ERP，AI拿不到全量数据。先做数据打通再谈AI。"},
    {"id": "P021", "category": "组织", "severity": "medium",
     "title": "期望过高", "content": "以为上了AI就能躺赚，结果发现只是工具升级。AI是效率放大器，不是救命仙丹，预期管理很重要。"},
    {"id": "P022", "category": "技术", "severity": "low",
     "title": "模型依赖症", "content": "什么都想丢给大模型，简单规则也用AI，成本高效率低。规则能搞定的用规则，搞不定的再上AI。"},
    {"id": "P023", "category": "内容", "severity": "low",
     "title": "缺乏反馈闭环", "content": "AI输出好不好没人评，质量越来越差。必须建立人工抽检+用户反馈的持续优化机制。"},
    {"id": "P024", "category": "合规", "severity": "critical",
     "title": "保健食品冒充药品", "content": "AI推荐时暗示产品有治疗功效，这是高压线。话术严格区分保健食品和药品，绝对不能越界。"},
    {"id": "P025", "category": "成本", "severity": "medium",
     "title": "ROI算不清", "content": "上线半年了还说不清AI到底带来了什么价值。上线前先定量化指标，上线后按月跟踪ROI。"},
]

# ============================================================
# 七、数据合理性校验规则（真相校验）
# ============================================================
DATA_VALIDATION_RULES = [
    {
        "id": "V001",
        "rule": "人均年营收合理性",
        "check": "revenue / employee_count",
        "min": 5,      # 健康行业人均年营收低于5万不合理
        "max": 200,    # 高于200万也不正常（非代理/贸易）
        "unit": "万元/人",
        "severity": "medium",
    },
    {
        "id": "V002",
        "rule": "门店人效合理性",
        "check": "store_count > 0 and employee_count / store_count",
        "min": 1,
        "max": 50,
        "unit": "人/店",
        "severity": "low",
    },
    {
        "id": "V003",
        "rule": "客户与员工比例",
        "check": "customer_count / employee_count",
        "min": 1,
        "max": 10000,
        "unit": "客户/员工",
        "severity": "low",
    },
    {
        "id": "V004",
        "rule": "IT预算占比合理性",
        "check": "it_budget / revenue if revenue > 0 else 0",
        "min": 0.001,
        "max": 0.3,
        "unit": "营收占比",
        "severity": "low",
    },
]

# ============================================================
# 八、三阶段路线图模板
# ============================================================
ROADMAP_TEMPLATE = {
    "phase1": {
        "name": "试点验证期（1-3个月）",
        "focus": "选1-2个高ROI场景快速验证",
        "key_deliverables": ["场景选型报告", "试点方案", "ROI验证数据"],
        "budget_range": [5, 15],
        "risk_level": "低",
    },
    "phase2": {
        "name": "推广建设期（3-9个月）",
        "focus": "核心场景全面推广，建立数据基础设施",
        "key_deliverables": ["全量上线方案", "数据中台", "培训体系"],
        "budget_range": [20, 50],
        "risk_level": "中",
    },
    "phase3": {
        "name": "深度优化期（9-18个月）",
        "focus": "AI深度融入业务，智能化决策升级",
        "key_deliverables": ["智能决策系统", "全链路AI覆盖", "持续优化机制"],
        "budget_range": [50, 100],
        "risk_level": "中高",
    },
}

# ============================================================
# 工具函数
# ============================================================

def get_industry_config(industry_type: str) -> Dict[str, Any]:
    """获取行业配置，不存在则返回默认"""
    return INDUSTRY_WEIGHT_CONFIG.get(industry_type, INDUSTRY_WEIGHT_CONFIG["default"])

def get_score_conclusion(total_score: float) -> Dict[str, str]:
    """根据总分获取诊断结论"""
    for item in SCORE_CONCLUSION_MAP:
        if item["min"] <= total_score <= item["max"]:
            return item
    return SCORE_CONCLUSION_MAP[-1]

def get_pitfalls_by_severity(severity: str) -> List[Dict]:
    """按严重程度获取坑点"""
    return [p for p in PITFALL_LIST if p["severity"] == severity]

def get_pitfalls_by_category(category: str) -> List[Dict]:
    """按分类获取坑点"""
    return [p for p in PITFALL_LIST if p["category"] == category]

def get_top_pitfalls(n: int = 5) -> List[Dict]:
    """获取Top N坑点（按严重程度排序）"""
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_pitfalls = sorted(PITFALL_LIST, key=lambda x: severity_order.get(x["severity"], 99))
    return sorted_pitfalls[:n]

def get_ontology_summary() -> Dict[str, Any]:
    """获取本体知识库概览（用于快速了解）"""
    return {
        "industries": len(INDUSTRY_WEIGHT_CONFIG),
        "dimensions": len(DIMENSION_DEFS),
        "scenarios": len(SCENARIO_BASELINE),
        "pitfalls": len(PITFALL_LIST),
        "compliance_rules": len(COMPLIANCE_RULES),
        "validation_rules": len(DATA_VALIDATION_RULES),
        "version": "1.8.0",
    }


if __name__ == "__main__":
    # 自测
    summary = get_ontology_summary()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\n行业配置示例（连锁门店）：")
    print(json.dumps(get_industry_config("chain_store"), ensure_ascii=False, indent=2))
    print("\nTop 5坑点：")
    for p in get_top_pitfalls(5):
        print(f"  [{p['severity']}] {p['title']}：{p['content'][:50]}...")
    print("\n评分结论示例（75分）：")
    print(json.dumps(get_score_conclusion(75), ensure_ascii=False, indent=2))

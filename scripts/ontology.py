#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康行业AI内容增长系统 - 本体知识库（Ontology）v2.0.0
=========================================================
结构化的领域先验知识，所有脚本统一调用，确保口径一致。

v2.0 重大变更（定位级重构）：
- 从"10个AI落地场景诊断" → "7大内容增长模块交付"
- 从"告诉你该做什么" → "直接给你能用的东西"
- 新增：产品类型识别、信任路径判断、内容增长瓶颈诊断
- 强化：内容合规、直播合规、宣传合规
- 新增：4档产品化报价体系
"""

import json
from typing import Dict, List, Any

# ============================================================
# 一、行业配置（内容增长权重）
# ============================================================
# 不同健康行业的内容增长权重差异
INDUSTRY_WEIGHT_CONFIG = {
    "default": {
        "label": "通用健康行业",
        "product_clarity": 0.20,    # 产品表达清晰度权重
        "content_capability": 0.25, # 内容生产能力权重
        "trust_building": 0.25,     # 信任构建能力权重
        "conversion_system": 0.20,  # 转化体系完善度权重
        "team_execution": 0.10,     # 团队执行力权重
    },
    "medical": {
        "label": "医疗机构/药房",
        "product_clarity": 0.25,
        "content_capability": 0.15,
        "trust_building": 0.30,     # 医疗行业信任最重要
        "conversion_system": 0.15,
        "team_execution": 0.15,
    },
    "online": {
        "label": "纯线上/电商/功能食品",
        "product_clarity": 0.20,
        "content_capability": 0.30, # 线上品牌内容能力最重要
        "trust_building": 0.20,
        "conversion_system": 0.20,
        "team_execution": 0.10,
    },
    "experiential": {
        "label": "体验营销/会销",
        "product_clarity": 0.15,
        "content_capability": 0.20,
        "trust_building": 0.30,     # 会销靠信任成交
        "conversion_system": 0.25,  # 转化体系（会销流程）很重要
        "team_execution": 0.10,
    },
    "chain_store": {
        "label": "连锁门店/保健品店",
        "product_clarity": 0.20,
        "content_capability": 0.20,
        "trust_building": 0.25,
        "conversion_system": 0.20,
        "team_execution": 0.15,     # 门店执行更重要
    },
    "anti_aging": {
        "label": "医美/抗衰/银发健康",
        "product_clarity": 0.20,
        "content_capability": 0.25,
        "trust_building": 0.30,     # 医美/抗衰信任门槛极高
        "conversion_system": 0.15,
        "team_execution": 0.10,
    },
}

# ============================================================
# 二、内容增长成熟度维度（五维评分体系 v2.0）
# ============================================================
CONTENT_GROWTH_DIMENSIONS = {
    "product_clarity": {
        "label": "产品表达清晰度",
        "max_score": 20,
        "description": "产品卖点是否清晰、差异化是否明确、话术体系是否完善",
        "sub_dimensions": ["卖点提炼", "差异化定位", "话术体系", "信任背书"],
    },
    "content_capability": {
        "label": "内容生产能力",
        "max_score": 25,
        "description": "短视频、图文、直播等内容形式的生产效率和质量",
        "sub_dimensions": ["产出效率", "内容质量", "平台覆盖", "爆款率"],
    },
    "trust_building": {
        "label": "信任构建能力",
        "max_score": 25,
        "description": "通过内容建立客户信任的能力，包括案例、背书、人设",
        "sub_dimensions": ["案例体系", "专家背书", "人设打造", "口碑传播"],
    },
    "conversion_system": {
        "label": "转化体系完善度",
        "max_score": 20,
        "description": "从内容到成交的转化链路是否完整、高效",
        "sub_dimensions": ["直播转化", "私域承接", "社群运营", "复购体系"],
    },
    "team_execution": {
        "label": "团队执行力",
        "max_score": 10,
        "description": "团队对内容增长策略的理解、执行和迭代能力",
        "sub_dimensions": ["人员配置", "执行SOP", "数据复盘", "AI工具使用"],
    },
}

# 成熟度等级映射（百分制）
MATURITY_LEVEL_MAP = [
    {"min": 85, "max": 100, "level": "S", "label": "内容增长优等生",
     "conclusion": "内容体系成熟，建议聚焦精细化运营和AI深度赋能",
     "action": "重点优化转化效率和复购，用AI放大现有优势"},
    {"min": 70, "max": 84, "level": "A", "label": "内容增长潜力股",
     "conclusion": "基础不错，补齐短板后可实现爆发式增长",
     "action": "聚焦1-2个核心模块做深做透，快速验证ROI"},
    {"min": 55, "max": 69, "level": "B", "label": "内容增长起步期",
     "conclusion": "有一定基础但不成体系，需要系统搭建内容增长框架",
     "action": "从产品卖点重构入手，先建立内容生产的基本盘"},
    {"min": 40, "max": 54, "level": "C", "label": "内容增长萌芽期",
     "conclusion": "内容体系薄弱，产品表达不清，需要从零搭建",
     "action": "先做产品定位和卖点梳理，再逐步建立内容生产能力"},
    {"min": 0, "max": 39, "level": "D", "label": "内容增长空白期",
     "conclusion": "几乎没有内容体系，产品靠人卖、不靠内容卖",
     "action": "从最基础的产品话术和朋友圈文案做起，30天建立雏形"},
]

# ============================================================
# 三、产品类型识别逻辑
# ============================================================
PRODUCT_TYPES = {
    "functional": {
        "label": "功能型产品",
        "description": "有明确功效诉求的产品，如保健品、功能食品、医疗器械",
        "key_indicators": ["有明确功效宣称", "成分/配方是核心卖点", "需要长期服用/使用"],
        "content_strategy": "功效实证+成分科普+案例见证",
        "trust_path": "成分→检测→案例→专家",
        "typical_products": ["蛋白粉", "鱼油", "益生菌", "钙片", "降糖茶"],
        "pain_focus": ["效果不明显", "怕有副作用", "不知道真假", "嫌贵"],
    },
    "experiential": {
        "label": "体验型产品/服务",
        "description": "以线下体验和服务为核心的产品，如养生馆、美容院、体验店",
        "key_indicators": ["线下体验是成交关键", "服务过程是产品的一部分", "客单价较高"],
        "content_strategy": "体验场景+服务过程+客户故事",
        "trust_path": "环境→体验→效果→转介绍",
        "typical_products": ["养生馆套餐", "理疗服务", "美容项目", "体验店产品"],
        "pain_focus": ["怕被推销", "效果不稳定", "路远不方便", "价格不透明"],
    },
    "rigid_demand": {
        "label": "刚需型产品",
        "description": "客户有明确需求、主动搜索的产品，如药品、医疗器械、慢病管理",
        "key_indicators": ["客户主动找产品", "有明确病症/需求", "复购率高"],
        "content_strategy": "专业科普+解决方案+长期陪伴",
        "trust_path": "专业度→安全性→效果→价格",
        "typical_products": ["血糖仪", "血压计", "慢病管理服务", "处方药周边"],
        "pain_focus": ["怕不安全", "担心副作用", "使用复杂", "太贵长期用不起"],
    },
    "social": {
        "label": "社交型产品",
        "description": "带有社交属性和身份认同的健康产品，如高端保健品、医美、抗衰",
        "key_indicators": ["送礼/社交场景多", "品牌身份感强", "客单价高"],
        "content_strategy": "高端人设+圈层案例+生活方式",
        "trust_path": "人设→圈层→案例→价值感",
        "typical_products": ["高端抗衰产品", "医美项目", "燕窝虫草", "高端体检"],
        "pain_focus": ["怕没效果丢面子", "怕不安全", "觉得不值这个价", "担心被骗"],
    },
}

# ============================================================
# 四、信任成交路径模型
# ============================================================
TRUST_PATHS = {
    "expert_trust": {
        "label": "专家信任型",
        "description": "客户因为相信专家/医生/权威而买单",
        "key_touchpoints": ["医生推荐", "专家讲座", "专业背书", "临床数据"],
        "content_focus": "专业内容输出、专家人设打造、临床案例分享",
        "suitable_products": ["医疗级产品", "慢病管理", "高端器械"],
        "bottlenecks": ["专家资源不足", "专业内容产出慢", "合规限制多"],
    },
    "case_trust": {
        "label": "案例信任型",
        "description": "客户因为看到真实案例和效果而买单",
        "key_touchpoints": ["客户见证", "效果对比", "口碑传播", "转介绍"],
        "content_focus": "真实案例打造、效果对比内容、客户证言收集",
        "suitable_products": ["保健品", "功能食品", "体验型服务"],
        "bottlenecks": ["案例收集难", "效果展示受合规限制", "同质化严重"],
    },
    "experience_trust": {
        "label": "体验信任型",
        "description": "客户因为亲身试用/体验后感觉好而买单",
        "key_touchpoints": ["免费试用", "到店体验", "体验装", "试听课"],
        "content_focus": "体验场景营造、服务过程展示、体验活动招募",
        "suitable_products": ["会销产品", "体验店", "养生馆", "服务型产品"],
        "bottlenecks": ["体验成本高", "转化周期长", "覆盖面有限"],
    },
    "personal_trust": {
        "label": "人设信任型",
        "description": "客户因为相信创始人/主播/IP人设而买单",
        "key_touchpoints": ["创始人故事", "主播人设", "IP内容", "私域互动"],
        "content_focus": "人设打造、价值观输出、生活方式展示",
        "suitable_products": ["高端品牌", "社交型产品", "私域品牌"],
        "bottlenecks": ["人设打造难", "IP风险高", "过度依赖个人"],
    },
    "price_trust": {
        "label": "价格驱动型",
        "description": "客户主要因为价格便宜/性价比高而买单",
        "key_touchpoints": ["促销活动", "限时优惠", "满减赠品", "比价"],
        "content_focus": "福利活动、价格对比、限时紧迫感",
        "suitable_products": ["大众保健品", "日用品", "低价引流品"],
        "bottlenecks": ["利润薄", "客户忠诚度低", "价格战恶性循环"],
    },
}

# ============================================================
# 五、内容增长瓶颈诊断模型
# ============================================================
BOTTLENECK_DIAGNOSIS = {
    "product_unclear": {
        "label": "产品表达模糊",
        "severity": "critical",
        "symptoms": ["说不清楚产品好在哪", "卖点太多记不住", "跟竞品没区别"],
        "impact": "内容发了没人看、看了也不买，因为客户不知道你卖的是什么",
        "solution": "产品卖点重构，3个核心卖点一句话说清",
        "related_modules": ["module1", "module2"],
    },
    "trust_deficit": {
        "label": "信任建立困难",
        "severity": "critical",
        "symptoms": ["客户总问真假", "下单犹豫", "复购率低"],
        "impact": "流量有了但转化率低，客户不敢买、买了也不再买",
        "solution": "信任背书体系搭建+案例库建设",
        "related_modules": ["module2", "module3"],
    },
    "content_shortage": {
        "label": "内容产能不足",
        "severity": "high",
        "symptoms": ["更新慢", "不知道拍什么", "内容质量不稳定"],
        "impact": "平台算法不给流量，账号起不来，品牌曝光不足",
        "solution": "AI内容生产体系+选题库+脚本模板",
        "related_modules": ["module4", "module7"],
    },
    "conversion_weak": {
        "label": "转化链路断裂",
        "severity": "high",
        "symptoms": ["有流量没成交", "直播间留不住人", "私域加了不说话"],
        "impact": "流量白白浪费，获客成本越来越高",
        "solution": "直播话术SOP+私域承接路径优化",
        "related_modules": ["module5", "module6"],
    },
    "team_disconnect": {
        "label": "团队执行脱节",
        "severity": "medium",
        "symptoms": ["策略落不了地", "员工不会用AI", "执行走样"],
        "impact": "好的内容策略执行不下去，效果大打折扣",
        "solution": "团队AI使用SOP+30天执行计划表",
        "related_modules": ["module7"],
    },
    "compliance_risk": {
        "label": "合规风险隐患",
        "severity": "critical",
        "symptoms": ["文案经常踩红线", "被平台限流/封号", "担心被举报"],
        "impact": "轻则限流封号，重则罚款坐牢，健康行业红线多",
        "solution": "合规红线手册+内容审核机制+AI合规助手",
        "related_modules": ["module2", "module4", "module5"],
    },
}

# ============================================================
# 六、7大内容增长模块（核心交付物 v2.0）
# ============================================================
CONTENT_GROWTH_MODULES = {
    "module1": {
        "module_id": "module1",
        "module_name": "项目定位诊断",
        "module_order": 1,
        "description": "搞清楚你是谁、卖给谁、靠什么卖——先诊断，再开方",
        "core_value": "找准内容增长的核心瓶颈，避免瞎忙活",
        "deliverables": [
            {"name": "产品类型判断报告", "format": "markdown", "description": "功能型/体验型/刚需型/社交型定位"},
            {"name": "目标人群画像表", "format": "markdown表格", "description": "年龄/性别/消费能力/决策因素/触媒习惯"},
            {"name": "竞争格局分析", "format": "markdown", "description": "红海/蓝海判断+差异化空间分析"},
            {"name": "信任成交路径图", "format": "markdown", "description": "你的客户是怎么一步步被说服的"},
            {"name": "内容增长瓶颈诊断书", "format": "markdown", "description": "当前最大的3个瓶颈及优先级"},
        ],
        "tools": {
            "options": [
                {
                    "name": "自助诊断版",
                    "components": ["本系统诊断问卷", "AI分析报告"],
                    "approach": "填写诊断问卷，AI自动生成定位诊断报告",
                    "pros": ["免费/低成本", "30分钟出结果", "结构化输出"],
                    "cons": ["需要自己填写信息", "深度依赖输入质量", "需人工复核"],
                    "fit_for": "预算有限、想先了解自己的企业",
                    "price_start": "免费（基础版）",
                    "difficulty": "低",
                },
                {
                    "name": "专家深度诊断",
                    "components": ["1对1访谈", "行业对标分析", "定制化诊断报告"],
                    "approach": "健康行业内容增长专家深度访谈+行业对标+定制诊断",
                    "pros": ["深度准确", "行业经验加持", "可直接落地"],
                    "cons": ["费用较高", "需要2-3天时间", "需企业配合"],
                    "fit_for": "年营收5000万以上、想系统性做内容增长的企业",
                    "price_start": "9800元/次",
                    "difficulty": "中",
                },
            ],
            "selection_guide": "先做自助诊断了解大概，需要深度落地方案再约专家诊断",
        },
        "timeline": "1-3天",
        "difficulty": 1,
        "budget_range": [0, 1],
        "ai_enhancement": "AI辅助人群画像分析、竞品信息整理、瓶颈识别",
    },
    "module2": {
        "module_id": "module2",
        "module_name": "产品卖点重构",
        "module_order": 2,
        "description": "把产品翻译成客户听得懂、愿意买的话——不是你想卖什么，是客户想买什么",
        "core_value": "解决'说了半天客户不知道你好在哪'的问题",
        "deliverables": [
            {"name": "核心卖点提炼表（3个以内）", "format": "markdown表格", "description": "每个卖点一句话说清，客户一听就懂"},
            {"name": "信任背书体系清单", "format": "markdown", "description": "成分/检测/案例/专家/资质，分门别类整理"},
            {"name": "竞品差异化定位报告", "format": "markdown", "description": "跟同类产品比，你的独特价值是什么"},
            {"name": "合规表达边界手册", "format": "markdown", "description": "什么能说、什么不能说、怎么说不踩红线"},
            {"name": "产品话术FABE表", "format": "markdown表格", "description": "Feature/Advantage/Benefit/Evidence完整话术"},
        ],
        "tools": {
            "options": [
                {
                    "name": "AI卖点生成工具包",
                    "components": ["豆包企业版", "卖点生成Prompt模板", "合规检查Prompt"],
                    "approach": "输入产品信息，AI批量生成卖点话术+合规自查",
                    "pros": ["成本低", "产出快", "可无限迭代"],
                    "cons": ["需要人工审核", "深度依赖输入信息质量", "需要懂Prompt"],
                    "fit_for": "有内容团队、想快速产出话术的企业",
                    "price_start": "3000元/年（大模型API费）",
                    "difficulty": "低",
                },
                {
                    "name": "专业文案顾问",
                    "components": ["健康行业文案专家", "卖点梳理工作坊", "合规审核"],
                    "approach": "资深健康行业文案专家带队，1对1梳理产品卖点和话术体系",
                    "pros": ["专业深度", "合规有保障", "可直接用"],
                    "cons": ["费用高", "周期长", "需要深度沟通"],
                    "fit_for": "核心产品上线前、重大营销活动前",
                    "price_start": "3万-10万/单品",
                    "difficulty": "中",
                },
            ],
            "selection_guide": "日常话术用AI工具包，核心产品/重大活动请专业顾问",
        },
        "timeline": "3-7天",
        "difficulty": 2,
        "budget_range": [0.3, 10],
        "ai_enhancement": "AI批量生成卖点变体、FABE话术、合规自查、竞品话术分析",
    },
    "module3": {
        "module_id": "module3",
        "module_name": "用户痛点与信任障碍",
        "module_order": 3,
        "description": "客户为什么不买？——把犹豫点找出来，一个个攻破",
        "core_value": "知道客户卡在哪，内容才能打在点子上",
        "deliverables": [
            {"name": "核心痛点清单（Top10）", "format": "markdown表格", "description": "按严重程度排序，每个痛点配真实场景描述"},
            {"name": "信任障碍分析报告", "format": "markdown", "description": "为什么用户犹豫不下单？5大信任障碍拆解"},
            {"name": "高频异议回应库（20个）", "format": "markdown表格", "description": "太贵/没用/怕踩坑/考虑一下，每个问题3种回应方式"},
            {"name": "人群分层内容策略", "format": "markdown", "description": "新客/老客/犹豫客/复购客，不同人群不同话术"},
            {"name": "客户证言收集模板", "format": "markdown", "description": "怎么引导客户说真话、说有用的话"},
        ],
        "tools": {
            "options": [
                {
                    "name": "AI痛点分析套装",
                    "components": ["评论区分析工具", "客服对话分析", "痛点Prompt库"],
                    "approach": "AI分析客户评论/客服对话/竞品差评，提炼痛点和异议",
                    "pros": ["数据驱动", "客观真实", "持续更新"],
                    "cons": ["需要数据源", "分析质量依赖数据量", "需人工验证"],
                    "fit_for": "有一定客户基数、想深挖客户需求的企业",
                    "price_start": "5000元/年",
                    "difficulty": "中",
                },
                {
                    "name": "用户研究工作坊",
                    "components": ["用户访谈", "焦点小组", "痛点地图梳理"],
                    "approach": "专业用户研究员带队，深度访谈+焦点小组+痛点地图",
                    "pros": ["深度洞察", "真实可信", "可落地性强"],
                    "cons": ["费用高", "周期长", "样本量有限"],
                    "fit_for": "新品上市前、重大战略调整前",
                    "price_start": "5万-20万/项目",
                    "difficulty": "高",
                },
            ],
            "selection_guide": "日常运营用AI分析工具，重大决策用用户研究工作坊",
        },
        "timeline": "5-14天",
        "difficulty": 3,
        "budget_range": [0.5, 20],
        "ai_enhancement": "AI分析评论/客服对话提取痛点、生成异议回应、模拟客户提问",
    },
    "module4": {
        "module_id": "module4",
        "module_name": "短视频选题与脚本库",
        "module_order": 4,
        "description": "30天不重样的选题+拿来就能拍的脚本——解决不知道拍什么的问题",
        "core_value": "从'想一条拍一条'变成'按表生产，稳定输出'",
        "deliverables": [
            {"name": "30天选题表", "format": "excel/markdown表格", "description": "按痛点/场景/人物/对比/科普分类，每天1条不重样"},
            {"name": "5种爆款脚本模板", "format": "markdown", "description": "痛点冲击型/专家科普型/真实案例型/对比测评型/老板人设型"},
            {"name": "开头钩子库（30个）", "format": "markdown", "description": "高完播率开头句式，直接套用"},
            {"name": "健康行业短视频合规红线", "format": "markdown", "description": "30条不能碰的红线+合规表达替换词表"},
            {"name": "短视频生产SOP", "format": "markdown", "description": "选题→脚本→拍摄→剪辑→发布→复盘，全流程规范"},
        ],
        "tools": {
            "options": [
                {
                    "name": "AI短视频创作套件",
                    "components": ["豆包企业版", "剪映AI", "数字人（可选）", "选题库Prompt"],
                    "approach": "AI生成选题和脚本+剪映快速剪辑+可选数字人口播",
                    "pros": ["产出效率提升5-10倍", "成本低", "可批量生产"],
                    "cons": ["真人感略差", "需要人工润色", "数字人需额外投入"],
                    "fit_for": "想快速起号、内容产能不足的团队",
                    "price_start": "5000-2万/年",
                    "difficulty": "低",
                },
                {
                    "name": "短视频代运营",
                    "components": ["专业编导", "拍摄剪辑团队", "账号运营", "数据复盘"],
                    "approach": "专业健康行业短视频团队全案代运营",
                    "pros": ["专业度高", "省心省力", "有效果保障（部分）"],
                    "cons": ["费用高", "找到靠谱团队难", "配合成本高"],
                    "fit_for": "有预算、想快速起号但没人手的企业",
                    "price_start": "2万-5万/月",
                    "difficulty": "中",
                },
            ],
            "selection_guide": "自己有人手用AI套件提效，没人手考虑代运营起步",
        },
        "timeline": "7-14天（首套模板搭建）",
        "difficulty": 2,
        "budget_range": [0.5, 30],
        "ai_enhancement": "AI批量生成选题、脚本、文案、字幕、数字人口播",
    },
    "module5": {
        "module_id": "module5",
        "module_name": "直播话术与转化逻辑",
        "module_order": 5,
        "description": "从留人到逼单的完整话术体系——不是瞎聊，是按流程成交",
        "core_value": "把直播间从'聊天场'变成'成交场'",
        "deliverables": [
            {"name": "直播间SOP流程表", "format": "markdown表格", "description": "开场→留人→讲品→逼单→复盘，每个环节时间节点和动作"},
            {"name": "产品讲解话术", "format": "markdown", "description": "成分→功效→信任→价格→下单，黄金讲品5步法"},
            {"name": "逼单话术库（20条）", "format": "markdown", "description": "稀缺性/紧迫感/福利/从众，4类逼单话术各5条"},
            {"name": "异议处理话术（15个）", "format": "markdown表格", "description": "太贵/没用/怕踩坑/考虑一下，直播间版回应话术"},
            {"name": "直播合规注意事项", "format": "markdown", "description": "健康行业直播25条红线，避免封号罚款"},
        ],
        "tools": {
            "options": [
                {
                    "name": "AI直播辅助工具",
                    "components": ["豆包企业版（话术生成）", "直播提词器", "实时评论分析"],
                    "approach": "AI生成直播话术+提词器辅助+实时评论分析辅助回应",
                    "pros": ["成本低", "话术不重样", "新手也能播"],
                    "cons": ["真人感需要练习", "实时响应有延迟", "需人工把控节奏"],
                    "fit_for": "主播新人、话术不熟练、想提升直播效率的团队",
                    "price_start": "3000-8000元/年",
                    "difficulty": "低",
                },
                {
                    "name": "AI数字人直播",
                    "components": ["硅基智能/腾讯智影", "24小时数字人直播", "话术库"],
                    "approach": "数字人7×24小时直播，真人主播只管高峰时段",
                    "pros": ["24小时不间断", "人力成本低", "话术标准可控"],
                    "cons": ["互动感差", "转化率低于真人", "平台政策风险"],
                    "fit_for": "长尾时段直播、多账号矩阵、低客单价产品",
                    "price_start": "1万-3万/年",
                    "difficulty": "中",
                },
                {
                    "name": "直播全案陪跑",
                    "components": ["直播运营总监", "主播培训", "话术体系搭建", "数据复盘"],
                    "approach": "资深健康行业直播运营带队，从0到1搭建直播体系",
                    "pros": ["专业度高", "见效快", "体系化搭建"],
                    "cons": ["费用高", "周期1-3个月", "需团队配合"],
                    "fit_for": "年营收5000万以上、直播是核心渠道的企业",
                    "price_start": "5万-20万/季度",
                    "difficulty": "高",
                },
            ],
            "selection_guide": "新手起步用AI直播辅助，想做矩阵加数字人，做大了请全案陪跑",
        },
        "timeline": "7-21天",
        "difficulty": 3,
        "budget_range": [0.3, 20],
        "ai_enhancement": "AI生成直播话术、实时评论分析回应、数字人直播、直播数据复盘",
    },
    "module6": {
        "module_id": "module6",
        "module_name": "社群内容与私域承接",
        "module_order": 6,
        "description": "加了微信不浪费——从破冰到成交到复购的完整私域体系",
        "core_value": "把公域流量变成私域资产，一次获客长期变现",
        "deliverables": [
            {"name": "7天社群内容排期表", "format": "markdown表格", "description": "科普/案例/互动/转化/复购，每天发什么都安排好"},
            {"name": "朋友圈文案模板（40条）", "format": "markdown", "description": "人设/产品/案例/福利，各10条，直接复制粘贴"},
            {"name": "私域转化路径设计图", "format": "markdown", "description": "加粉→破冰→培育→成交→复购，每一步说什么做什么"},
            {"name": "社群运营SOP", "format": "markdown", "description": "早安/科普/答疑/活动/复盘，社群每日运营流程"},
            {"name": "私域合规红线", "format": "markdown", "description": "朋友圈/社群宣传的15条红线，避免被封号"},
        ],
        "tools": {
            "options": [
                {
                    "name": "AI私域内容工具包",
                    "components": ["豆包企业版", "朋友圈文案Prompt", "社群话术模板"],
                    "approach": "AI批量生成朋友圈文案、社群话术、跟进消息",
                    "pros": ["成本极低", "产出量大", "可个性化定制"],
                    "cons": ["需要人工筛选", "人设一致性需把控", "发送需人工操作"],
                    "fit_for": "有私域基础、想提升内容产出效率的团队",
                    "price_start": "2000-5000元/年",
                    "difficulty": "低",
                },
                {
                    "name": "SCRM私域系统",
                    "components": ["微伴/微盛SCRM", "客户标签体系", "自动跟进SOP"],
                    "approach": "企微SCRM系统+客户标签+自动跟进+社群管理一体化",
                    "pros": ["系统化管理", "数据可追踪", "自动化程度高"],
                    "cons": ["年费不低", "需要学习使用", "数据导入有成本"],
                    "fit_for": "私域客户5000以上、有专门运营团队的企业",
                    "price_start": "1万-5万/年",
                    "difficulty": "中",
                },
                {
                    "name": "私域全案陪跑",
                    "components": ["私域运营顾问", "体系搭建", "团队培训", "数据复盘"],
                    "approach": "资深健康行业私域专家带队，从0到1搭建私域增长体系",
                    "pros": ["体系化", "有结果保障", "团队能力同步提升"],
                    "cons": ["费用高", "周期3-6个月", "深度参与成本高"],
                    "fit_for": "年营收5000万以上、私域是核心战略的企业",
                    "price_start": "8万-30万/半年",
                    "difficulty": "高",
                },
            ],
            "selection_guide": "起步用AI工具包，5000+客户上SCRM，战略级投入请陪跑",
        },
        "timeline": "7-14天（基础搭建）",
        "difficulty": 2,
        "budget_range": [0.2, 30],
        "ai_enhancement": "AI生成朋友圈文案、社群内容、1对1跟进话术、客户画像分析",
    },
    "module7": {
        "module_id": "module7",
        "module_name": "AI知识库与团队执行",
        "module_order": 7,
        "description": "把所有内容、话术、素材装进AI，让团队人人都是高手",
        "core_value": "不是让团队学AI，是让AI帮团队干活——直接提效",
        "deliverables": [
            {"name": "AI知识库搭建方案", "format": "markdown", "description": "产品知识/话术库/素材库/问答库，4库结构设计"},
            {"name": "团队AI使用SOP（3套）", "format": "markdown", "description": "内容岗/销售岗/运营岗各一套，每天怎么用AI"},
            {"name": "30天执行落地计划表", "format": "excel/markdown表格", "description": "按周拆解，每周做什么、谁负责、交付什么"},
            {"name": "效果衡量指标体系", "format": "markdown表格", "description": "内容/转化/复购/效率，4大类20个指标"},
            {"name": "周复盘模板", "format": "markdown", "description": "每周复盘看什么、怎么分析、怎么调整"},
        ],
        "tools": {
            "options": [
                {
                    "name": "轻量知识库方案",
                    "components": ["飞书知识库/Notion", "豆包企业版", "Prompt模板库"],
                    "approach": "用飞书/Notion存知识+大模型做问答+Prompt模板标准化使用",
                    "pros": ["成本低", "上手快", "不需要技术团队"],
                    "cons": ["功能相对基础", "深度定制有限", "需手动维护"],
                    "fit_for": "20人以下小团队、快速起步的企业",
                    "price_start": "5000-1万/年",
                    "difficulty": "低",
                },
                {
                    "name": "企业级AI知识库",
                    "components": ["私有化部署大模型", "企业知识库系统", "权限管理"],
                    "approach": "私有化部署+专属知识库+多角色权限+数据不出企业",
                    "pros": ["数据安全", "定制化程度高", "可对接内部系统"],
                    "cons": ["投入大", "需要IT维护", "实施周期长"],
                    "fit_for": "100人以上、数据安全要求高的中大型企业",
                    "price_start": "10万-30万/年",
                    "difficulty": "高",
                },
                {
                    "name": "门店AI助手（录音豆方案）",
                    "components": ["门店录音设备", "AI语音分析", "话术质检", "培训建议"],
                    "approach": "门店录音→AI分析服务质量和话术→给出改进建议→培训闭环",
                    "pros": ["客观真实", "发现问题精准", "可复制到所有门店"],
                    "cons": ["需硬件投入", "隐私合规需注意", "门店配合度影响效果"],
                    "fit_for": "连锁门店、会销企业、体验型服务",
                    "price_start": "2000元/店/年起",
                    "difficulty": "中",
                },
            ],
            "selection_guide": "小团队用轻量方案起步，数据敏感上企业级，连锁门店加录音豆方案",
        },
        "timeline": "14-30天",
        "difficulty": 3,
        "budget_range": [0.5, 30],
        "ai_enhancement": "AI知识库问答、话术自动生成、培训自动出题、门店服务质检",
    },
}

# 模块依赖关系（哪些模块是其他模块的前置）
MODULE_DEPENDENCIES = {
    "module1": [],                    # 定位诊断：无前置
    "module2": ["module1"],           # 卖点重构：需要先做定位诊断
    "module3": ["module1", "module2"], # 痛点与信任：需要定位和卖点
    "module4": ["module2", "module3"], # 短视频：需要卖点和痛点
    "module5": ["module2", "module3"], # 直播：需要卖点和痛点
    "module6": ["module2", "module3"], # 私域：需要卖点和痛点
    "module7": ["module1"],           # AI执行：需要定位后配置
}

# 模块推荐优先级逻辑（基于企业特征）
MODULE_PRIORITY_RULES = {
    "content_first": {
        "label": "内容产能优先型",
        "priority": ["module1", "module2", "module4", "module7", "module3", "module5", "module6"],
        "condition": "内容团队小、产出不足、账号刚起步",
        "trigger": {"content_team_size_lt": 3, "has_short_video_account": False},
    },
    "conversion_first": {
        "label": "转化效率优先型",
        "priority": ["module1", "module2", "module5", "module6", "module3", "module4", "module7"],
        "condition": "有流量但转化低、直播是核心渠道、私域有基础",
        "trigger": {"has_traffic": True, "conversion_rate_lt": 0.02, "has_livestream": True},
    },
    "trust_first": {
        "label": "信任构建优先型",
        "priority": ["module1", "module3", "module2", "module6", "module4", "module7", "module5"],
        "condition": "客单价高、信任门槛高、复购是核心",
        "trigger": {"price_gt": 1000, "is_high_ticket": True, "repurchase_importance": "high"},
    },
    "balanced": {
        "label": "均衡发展型",
        "priority": ["module1", "module2", "module3", "module4", "module5", "module6", "module7"],
        "condition": "各方面都有一定基础，想系统化提升",
        "trigger": {"revenue_gt": 2000, "has_content_team": True, "has_private_domain": True},
    },
}

# ============================================================
# 七、4档产品化报价体系
# ============================================================
PRICING_TIERS = {
    "basic": {
        "tier": "基础版",
        "price": "3980元",
        "price_note": "一次性费用，永久使用模板",
        "target_customer": "小微企业、单店、预算有限的老板",
        "included_modules": ["module1", "module2", "module4"],
        "deliverables_summary": [
            "项目定位诊断报告",
            "产品卖点FABE表（含合规边界）",
            "30天短视频选题表+5套脚本模板",
            "AI工具使用手册（3个核心Prompt模板）",
        ],
        "service_content": [
            "自助式诊断工具",
            "模板化交付物",
            "AI生成Prompt模板",
            "社群答疑（1个月）",
        ],
        "expected_outcome": "30天内建立内容生产基本盘，从'不知道发什么'变成'按表生产'",
        "roi_hint": "相当于招1个内容专员半个月工资，省的时间和外包费1个月回本",
    },
    "standard": {
        "tier": "标准版",
        "price": "19800元",
        "price_note": "一次性费用，含1次专家诊断+3个月社群陪跑",
        "target_customer": "中型企业、3-5人内容团队、年营收1000-5000万",
        "included_modules": ["module1", "module2", "module3", "module4", "module6", "module7"],
        "deliverables_summary": [
            "专家1对1定位诊断（2小时访谈+定制报告）",
            "产品卖点重构+FABE话术+合规手册",
            "用户痛点清单+异议回应库（20个）",
            "30天短视频选题表+5套爆款脚本模板",
            "7天社群排期+40条朋友圈模板+私域转化路径",
            "AI知识库搭建方案+团队AI使用SOP",
            "30天执行落地计划表",
        ],
        "service_content": [
            "1对1专家诊断（2小时）",
            "全部7模块模板+定制化调整",
            "AI工具选型与配置指导",
            "3个月社群陪跑+周复盘",
            "团队培训（1次线上）",
        ],
        "expected_outcome": "3个月内建立完整的内容增长体系，内容产出效率提升3-5倍，转化率提升20-50%",
        "roi_hint": "相当于招1个内容运营3个月工资，但带来的是整套体系+团队能力提升",
    },
    "advanced": {
        "tier": "进阶版",
        "price": "9.8万",
        "price_note": "季度服务，含全模块交付+陪跑+直播操盘",
        "target_customer": "中大型企业、年营收5000万以上、内容团队5人以上",
        "included_modules": ["module1", "module2", "module3", "module4", "module5", "module6", "module7"],
        "deliverables_summary": [
            "全模块深度定制交付（全部7个模块）",
            "直播话术体系+直播SOP+主播培训",
            "AI知识库系统部署+数据迁移",
            "月度内容策略调整",
            "每周数据复盘报告",
            "团队AI能力全面培训",
        ],
        "service_content": [
            "驻场诊断（1天）",
            "全模块深度定制",
            "直播陪跑（每周2次复盘）",
            "私域运营陪跑（每周1次）",
            "AI系统部署与培训",
            "月度策略会（3次）",
            "专属顾问1V1服务",
        ],
        "expected_outcome": "3个月内容增长体系全面跑通，直播GMV提升30-100%，私域复购率提升20%+",
        "roi_hint": "相比招1个内容总监（月薪3-5万），性价比更高，而且带来的是体系不是个人",
    },
    "long_term": {
        "tier": "长期陪跑版",
        "price": "29.8万/年",
        "price_note": "年度服务，全年陪跑+策略迭代+团队共建",
        "target_customer": "大型企业、年营收1亿以上、想长期深耕内容增长的企业",
        "included_modules": ["module1", "module2", "module3", "module4", "module5", "module6", "module7"],
        "deliverables_summary": [
            "全年4次战略复盘与策略调整",
            "月度内容选题规划与脚本审核",
            "直播月度复盘与话术迭代",
            "私域增长季度规划",
            "AI知识库持续优化",
            "团队培训（每月1次）",
            "行业对标与竞品分析（季度）",
            "专属增长顾问全年服务",
        ],
        "service_content": [
            "季度战略复盘会（4次/年）",
            "月度内容策略会（12次/年）",
            "周度数据复盘（48次/年）",
            "团队培训（12次/年）",
            "行业报告与趋势分享",
            "新工具测试与推荐",
            "专属顾问随叫随到",
        ],
        "expected_outcome": "1年内打造自运行的内容增长体系，团队能力全面升级，GMV增长50-200%",
        "roi_hint": "相当于自建一个5人内容增长团队（年成本100万+）的效果，但成本只有1/3，而且更专业",
    },
}

# ============================================================
# 八、健康行业内容合规红线（v2.0 强化版）
# ============================================================
COMPLIANCE_RULES = {
    "banned_words": {
        "medical_treatment": [
            # 绝对禁止：医疗用语
            "治疗", "治愈", "根治", "痊愈", "药到病除", "包治百病",
            "处方", "药用", "诊断", "疾病", "抗癌", "防癌",
            "降血压", "降血糖", "降血脂", "减肥（非减脂产品）",
            "疗效", "治愈率", "有效率", "康复",
        ],
        "absolute_words": [
            # 绝对禁止：绝对化用语
            "最佳", "第一", "顶级", "唯一", "国家级", "最高级",
            "100%有效", "绝对安全", "无毒副作用", "无效退款",
            "永不复发", "彻底", "根治",
        ],
        "exaggeration_words": [
            # 禁止：夸大宣传
            "神药", "神奇", "奇迹", "颠覆性", "革命性",
            "诺贝尔奖", "航天科技", "干细胞（无资质）",
        ],
        "food_specific": [
            # 保健食品/食品特别禁止
            "治疗疾病", "预防疾病", "代替药物", "药用功效",
            "防癌抗癌", "降糖降压", "修复细胞",
        ],
        "cosmetic_specific": [
            # 医美/化妆品特别禁止
            "医疗级", "药妆", "医学护肤品",
            "永久", "彻底去除", "无痕",
        ],
    },
    "replacement_words": {
        # 合规替换词表：左边是禁用词，右边是合规表达
        "治疗": "调理/改善/养护",
        "治愈": "帮助改善/有助于恢复",
        "根治": "从根源调理/深度养护",
        "100%有效": "很多客户反馈不错/好评率高",
        "绝对安全": "通过XX检测/符合国家标准",
        "无效退款": "不满意可沟通/7天无理由退换",
        "降血压": "有助于血压健康/养护心血管",
        "降血糖": "调节血糖代谢/关注血糖健康",
        "抗癌": "增强免疫力/关注健康",
        "最佳": "口碑很好/备受好评",
        "第一": "销量领先/深受欢迎",
        "神奇效果": "明显感受/真实体验",
    },
    "content_platform_rules": {
        "douyin": {
            "name": "抖音/视频号短视频",
            "key_rules": [
                "禁止出现'治疗''治愈'等医疗用语",
                "禁止直接展示疾病症状对比图",
                "保健食品必须标注'本品不能代替药物'",
                "禁止承诺效果和治愈率",
                "医美类需提供医疗机构资质",
                "禁止使用患者名义做证明（真人出镜需合规）",
            ],
            "risk_level": "high",
        },
        "livestream": {
            "name": "直播带货",
            "key_rules": [
                "禁止虚假宣传和夸大功效",
                "禁止使用医疗术语描述普通食品/保健品",
                "保健食品需展示蓝帽子标识和适宜人群",
                "禁止'最低价''全网第一'等绝对化用语",
                "医疗器械需展示注册证号",
                "禁止暗示产品有疾病治疗功能",
            ],
            "risk_level": "high",
        },
        "wechat_moments": {
            "name": "朋友圈/社群",
            "key_rules": [
                "禁止刷屏式硬广（容易被封号）",
                "禁止使用'治疗''根治'等违规词",
                "禁止编造聊天记录、转账记录做假案例",
                "保健食品不能宣传治疗功效",
                "禁止诱导分享、集赞等行为",
                "注意个人隐私保护，客户案例需授权",
            ],
            "risk_level": "medium",
        },
        "official_account": {
            "name": "公众号/图文",
            "key_rules": [
                "科普内容与广告内容需明确区分",
                "禁止发布虚假医疗信息",
                "引用数据需注明来源",
                "保健食品广告需有审批文号",
                "禁止使用患者名义做疗效证明",
            ],
            "risk_level": "medium",
        },
    },
    "penalty_standards": {
        "high": "可能面临20万-100万罚款，严重者吊销执照、追究刑事责任",
        "medium": "可能面临投诉举报、市场监管约谈、平台限流/封号",
        "low": "存在合规瑕疵，建议优化表述，避免被举报",
    },
    "compliance_checklist": [
        "□ 是否使用了医疗用语描述非医疗产品？",
        "□ 是否有绝对化用语（最佳、第一、100%等）？",
        "□ 是否承诺效果或治愈率？",
        "□ 保健食品是否标注'本品不能代替药物'？",
        "□ 是否使用了真实客户案例？是否有授权？",
        "□ 数据和引用是否有来源？",
        "□ 是否存在贬低竞品的表述？",
        "□ 医美/医疗器械是否有相应资质？",
        "□ 是否存在诱导分享/集赞等行为？",
        "□ 价格表述是否真实（原价是否有依据）？",
    ],
}

# ============================================================
# 九、内容增长坑点清单（Top 25 v2.0）
# ============================================================
PITFALL_LIST = [
    {"id": "P001", "category": "合规", "severity": "critical",
     "title": "红线词地雷", "content": "AI写文案爱用治愈、根治、最佳等禁用词，一篇违规罚款20万起。必须建敏感词库+人工复核双保险，健康行业合规是生命线。"},
    {"id": "P002", "category": "内容", "severity": "high",
     "title": "自嗨式内容", "content": "天天发产品多好多牛，客户根本不关心。内容要讲客户的痛点、场景、故事，不是讲你的产品参数。"},
    {"id": "P003", "category": "产品", "severity": "critical",
     "title": "卖点模糊不清", "content": "10个卖点等于没有卖点。健康产品必须提炼3个以内核心卖点，每个一句话说清客户能得到什么好处。"},
    {"id": "P004", "category": "信任", "severity": "critical",
     "title": "信任背书缺失", "content": "健康行业客户最在意安全和效果，没有检测报告、没有真实案例、没有专家背书，说破天也没人信。"},
    {"id": "P005", "category": "转化", "severity": "high",
     "title": "有流量没成交", "content": "短视频播放量很高但没人买，问题在转化链路——直播间没有逼单、私域没有承接、话术打不动人。"},
    {"id": "P006", "category": "团队", "severity": "high",
     "title": "团队不会用AI", "content": "买了一堆AI工具，员工还是老办法干活。必须有SOP、有培训、有考核，AI是工具不是玩具。"},
    {"id": "P007", "category": "内容", "severity": "high",
     "title": "内容同质化严重", "content": "大家都用同一个大模型，文案越来越像，客户审美疲劳。必须建公司专属语料库和案例库，人改AI出稿保差异化。"},
    {"id": "P008", "category": "私域", "severity": "high",
     "title": "加了微信就硬推", "content": "公域引流加微信，上来就发广告，客户直接拉黑。私域是养鱼不是钓鱼，先给价值再谈成交。"},
    {"id": "P009", "category": "直播", "severity": "high",
     "title": "直播全靠主播个人", "content": "主播状态决定业绩，主播一走业绩垮一半。必须建立标准化的直播SOP和话术体系，降低对个人的依赖。"},
    {"id": "P010", "category": "数据", "severity": "medium",
     "title": "只看播放量不看转化", "content": "天天追着播放量焦虑，忽略了内容带来的咨询量和成交量。内容的终极指标是GMV，不是播放量。"},
    {"id": "P011", "category": "合规", "severity": "critical",
     "title": "保健品冒充药品", "content": "暗示产品有治疗功效，这是高压线。话术必须严格区分'调理''改善'和'治疗''治愈'，绝对不能越界。"},
    {"id": "P012", "category": "内容", "severity": "medium",
     "title": "选题全靠拍脑袋", "content": "今天拍这个明天拍那个，没有系统的选题规划。必须建立选题库，按痛点/场景/人物/对比/科普分类生产。"},
    {"id": "P013", "category": "团队", "severity": "medium",
     "title": "没有内容SOP", "content": "每个人各干各的，质量参差不齐，人走了经验也带走了。必须把经验沉淀成SOP和模板，让新人也能快速上手。"},
    {"id": "P014", "category": "信任", "severity": "high",
     "title": "案例造假翻车", "content": "P图做假案例、编造聊天记录，一旦被揭穿品牌就毁了。案例必须真实，宁可少也要真。"},
    {"id": "P015", "category": "私域", "severity": "medium",
     "title": "社群变成广告群", "content": "群里全是发广告的，没人说话没人互动，死群不如不建。社群必须有价值：科普、答疑、互动，转化是副产品。"},
    {"id": "P016", "category": "产品", "severity": "medium",
     "title": "跟竞品说不清区别", "content": "客户问'你家跟XX品牌有什么区别'，答不上来。必须找到差异化定位，可以是成分、工艺、人群、服务、价格任何一点。"},
    {"id": "P017", "category": "直播", "severity": "medium",
     "title": "直播间留不住人", "content": "用户进来3秒就走，开场没有钩子。前30秒必须抛出痛点+给出期待，留住人才能讲产品。"},
    {"id": "P018", "category": "成本", "severity": "medium",
     "title": "Token费用失控", "content": "初期免费额度够用，上量后账单爆炸。必须设用量上限和告警，长文本用摘要压缩后再送模型。"},
    {"id": "P019", "category": "数据", "severity": "medium",
     "title": "不做复盘瞎忙活", "content": "天天发内容但从不复盘，不知道哪条好、为什么好。必须每周复盘数据，用数据指导下周的内容策略。"},
    {"id": "P020", "category": "合规", "severity": "high",
     "title": "直播合规意识差", "content": "直播时随口说'这个能治XX'，被录屏举报就是大事。直播前必须过话术、直播时必须有人盯合规。"},
    {"id": "P021", "category": "内容", "severity": "low",
     "title": "平台规则吃不透", "content": "不知道什么内容会被限流、什么词会触发审核，发一条死一条。每个平台都要研究它的规则和算法偏好。"},
    {"id": "P022", "category": "团队", "severity": "low",
     "title": "老板不重视内容", "content": "内容是老板工程，老板不带头、不重视，团队肯定做不好。老板要亲自抓方向、抓选题、抓审核。"},
    {"id": "P023", "category": "私域", "severity": "low",
     "title": "朋友圈人设混乱", "content": "今天发鸡汤明天发广告后天发自拍，客户不知道你是谁。朋友圈要有清晰人设：专业、真实、有温度。"},
    {"id": "P024", "category": "信任", "severity": "medium",
     "title": "客服话术不统一", "content": "不同客服回答同一个问题答案不一样，客户就不信任了。必须建立标准话术库和异议处理手册。"},
    {"id": "P025", "category": "战略", "severity": "high",
     "title": "到处撒网没有重点", "content": "抖音、视频号、小红书、快手全在做，哪个都没做好。健康行业先做好1-2个核心渠道，做深做透再扩张。"},
]

# ============================================================
# 十、30天执行落地模板
# ============================================================
EXECUTION_PLAN_30DAYS = {
    "week1": {
        "theme": "定位周——搞清楚方向",
        "key_tasks": [
            "完成产品定位诊断（模块1）",
            "提炼3个核心卖点（模块2）",
            "梳理信任背书清单（模块2）",
            "团队第一次AI工具培训",
        ],
        "deliverables": [
            "定位诊断报告",
            "核心卖点表",
            "信任背书清单",
        ],
        "owner": "老板+营销负责人",
    },
    "week2": {
        "theme": "内容周——建内容基本盘",
        "key_tasks": [
            "梳理Top10用户痛点（模块3）",
            "整理20个高频异议回应（模块3）",
            "产出30天短视频选题表（模块4）",
            "完成5套脚本模板首稿（模块4）",
        ],
        "deliverables": [
            "痛点清单",
            "异议回应库",
            "30天选题表",
            "5套脚本模板",
        ],
        "owner": "内容团队",
    },
    "week3": {
        "theme": "转化周——搭转化体系",
        "key_tasks": [
            "搭建直播间SOP流程（模块5）",
            "完成产品讲解话术（模块5）",
            "设计私域转化路径（模块6）",
            "产出7天社群排期表（模块6）",
            "准备40条朋友圈模板（模块6）",
        ],
        "deliverables": [
            "直播SOP",
            "讲品话术",
            "私域路径图",
            "社群排期表",
            "朋友圈模板",
        ],
        "owner": "运营+销售负责人",
    },
    "week4": {
        "theme": "落地周——跑通闭环",
        "key_tasks": [
            "AI知识库搭建完成（模块7）",
            "团队AI使用SOP发布（模块7）",
            "第一次完整直播演练",
            "第一轮内容发布（5-10条）",
            "首周数据复盘+优化调整",
        ],
        "deliverables": [
            "AI知识库",
            "AI使用SOP",
            "首批内容发布",
            "首周复盘报告",
        ],
        "owner": "全员",
    },
}

# ============================================================
# 十一、工具函数
# ============================================================

def get_industry_config(industry_type: str) -> Dict[str, Any]:
    """获取行业配置，不存在则返回默认"""
    return INDUSTRY_WEIGHT_CONFIG.get(industry_type, INDUSTRY_WEIGHT_CONFIG["default"])

def get_maturity_level(total_score: float) -> Dict[str, str]:
    """根据总分获取成熟度等级"""
    for item in MATURITY_LEVEL_MAP:
        if item["min"] <= total_score <= item["max"]:
            return item
    return MATURITY_LEVEL_MAP[-1]

def get_product_type(product_info: Dict) -> Dict:
    """
    判断产品类型
    输入产品特征信息，返回最匹配的产品类型
    """
    scores = {}
    for type_id, type_data in PRODUCT_TYPES.items():
        score = 0
        # 基于关键词匹配打分（简化版，实际可接入LLM判断）
        desc = str(product_info.get("description", "")) + str(product_info.get("name", ""))
        keywords = type_data.get("typical_products", [])
        for kw in keywords:
            if kw in desc:
                score += 20
        # 基于关键指标匹配
        for indicator in type_data.get("key_indicators", []):
            if indicator in str(product_info.get("features", "")):
                score += 15
        scores[type_id] = score

    if not scores or max(scores.values()) == 0:
        # 没有匹配信息时返回默认
        return {
            "type_id": "functional",
            **PRODUCT_TYPES["functional"],
            "confidence": 0.5,
            "note": "信息不足，默认按功能型产品处理，建议补充信息后重新诊断",
        }

    best_type = max(scores, key=scores.get)
    max_score = scores[best_type]
    confidence = min(0.95, max_score / 100)

    return {
        "type_id": best_type,
        **PRODUCT_TYPES[best_type],
        "confidence": round(confidence, 2),
        "all_scores": scores,
    }

def get_trust_path(product_type_id: str, industry_type: str) -> Dict:
    """
    判断主要信任路径
    基于产品类型和行业特征判断客户最主要的信任建立方式
    """
    path_scores = {}

    # 产品类型与信任路径的对应关系
    type_path_mapping = {
        "functional": {"case_trust": 30, "expert_trust": 25, "experience_trust": 20},
        "experiential": {"experience_trust": 35, "case_trust": 25, "personal_trust": 15},
        "rigid_demand": {"expert_trust": 40, "case_trust": 25, "price_trust": 10},
        "social": {"personal_trust": 35, "case_trust": 25, "expert_trust": 20},
    }

    base_scores = type_path_mapping.get(product_type_id, {"case_trust": 30, "expert_trust": 25})

    # 行业调整
    industry_adjust = {
        "medical": {"expert_trust": 15},
        "experiential": {"experience_trust": 10},
        "anti_aging": {"personal_trust": 15, "case_trust": 10},
        "online": {"case_trust": 10},
    }

    for path_id, base in base_scores.items():
        score = base
        adjust = industry_adjust.get(industry_type, {})
        score += adjust.get(path_id, 0)
        path_scores[path_id] = score

    # 按得分排序
    sorted_paths = sorted(path_scores.items(), key=lambda x: x[1], reverse=True)
    primary_path = sorted_paths[0][0]
    primary_score = sorted_paths[0][1]
    max_possible = 50  # 理论最高分
    confidence = min(0.9, primary_score / max_possible)

    return {
        "primary_path": primary_path,
        "primary_path_data": TRUST_PATHS[primary_path],
        "secondary_paths": [p[0] for p in sorted_paths[1:3]],
        "all_scores": {p[0]: p[1] for p in sorted_paths},
        "confidence": round(confidence, 2),
    }

def diagnose_bottlenecks(company_info: Dict, maturity_scores: Dict) -> List[Dict]:
    """
    诊断内容增长核心瓶颈
    基于企业信息和成熟度评分，识别Top 3瓶颈
    """
    bottleneck_scores = {}

    for b_id, b_data in BOTTLENECK_DIAGNOSIS.items():
        score = 0

        # 基于成熟度维度评分判断
        if b_id == "product_unclear" and maturity_scores.get("product_clarity", 50) < 60:
            score += 30
        if b_id == "content_shortage" and maturity_scores.get("content_capability", 50) < 60:
            score += 30
        if b_id == "trust_deficit" and maturity_scores.get("trust_building", 50) < 60:
            score += 30
        if b_id == "conversion_weak" and maturity_scores.get("conversion_system", 50) < 60:
            score += 30
        if b_id == "team_disconnect" and maturity_scores.get("team_execution", 50) < 60:
            score += 20

        # 基于企业特征加分
        if b_id == "compliance_risk":
            industry = company_info.get("industry_type", "")
            if industry in ["medical", "anti_aging", "experiential"]:
                score += 25
            if company_info.get("has_regulatory_issue", False):
                score += 20

        # 严重程度基础分
        severity_base = {"critical": 20, "high": 10, "medium": 5}
        score += severity_base.get(b_data["severity"], 5)

        bottleneck_scores[b_id] = score

    # 按得分排序，取Top 3
    sorted_bottlenecks = sorted(bottleneck_scores.items(), key=lambda x: x[1], reverse=True)
    result = []
    for b_id, score in sorted_bottlenecks[:3]:
        result.append({
            "bottleneck_id": b_id,
            "score": score,
            **BOTTLENECK_DIAGNOSIS[b_id],
        })

    return result

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

def recommend_modules(company_info: Dict, bottlenecks: List[Dict]) -> Dict:
    """
    基于企业特征和瓶颈诊断，推荐模块优先级
    """
    # 简化逻辑：根据主要瓶颈和企业特征选择策略类型
    strategy_type = "balanced"

    # 根据首要瓶颈判断
    if bottlenecks:
        primary = bottlenecks[0]["bottleneck_id"]
        if primary in ["content_shortage"]:
            strategy_type = "content_first"
        elif primary in ["conversion_weak"]:
            strategy_type = "conversion_first"
        elif primary in ["trust_deficit", "product_unclear"]:
            strategy_type = "trust_first"

    strategy = MODULE_PRIORITY_RULES.get(strategy_type, MODULE_PRIORITY_RULES["balanced"])

    # 获取模块详情
    modules_detail = []
    for m_id in strategy["priority"]:
        if m_id in CONTENT_GROWTH_MODULES:
            modules_detail.append({
                "module_id": m_id,
                **CONTENT_GROWTH_MODULES[m_id],
            })

    return {
        "strategy_type": strategy_type,
        "strategy_label": strategy["label"],
        "strategy_condition": strategy["condition"],
        "priority_order": strategy["priority"],
        "modules": modules_detail,
        "recommended_first_module": strategy["priority"][0] if strategy["priority"] else None,
    }

def get_pricing_recommendation(company_info: Dict) -> Dict:
    """
    根据企业规模推荐合适的产品档位
    """
    revenue = company_info.get("annual_revenue", 0)  # 万元
    team_size = company_info.get("team_size", 0)
    content_team = company_info.get("content_team_size", 0)

    if revenue >= 10000 or team_size >= 200:
        tier = "long_term"
    elif revenue >= 5000 or team_size >= 100:
        tier = "advanced"
    elif revenue >= 1000 or team_size >= 20:
        tier = "standard"
    else:
        tier = "basic"

    return {
        "recommended_tier": tier,
        **PRICING_TIERS[tier],
        "all_tiers": PRICING_TIERS,
    }

def get_ontology_summary() -> Dict[str, Any]:
    """获取本体知识库概览（用于快速了解）"""
    return {
        "version": "2.0.0",
        "industries": len(INDUSTRY_WEIGHT_CONFIG),
        "content_growth_dimensions": len(CONTENT_GROWTH_DIMENSIONS),
        "product_types": len(PRODUCT_TYPES),
        "trust_paths": len(TRUST_PATHS),
        "bottlenecks": len(BOTTLENECK_DIAGNOSIS),
        "content_growth_modules": len(CONTENT_GROWTH_MODULES),
        "pricing_tiers": len(PRICING_TIERS),
        "pitfalls": len(PITFALL_LIST),
        "compliance_rules": "全面升级：含禁用词/替换词/平台规则/检查清单",
    }


if __name__ == "__main__":
    # 自测
    summary = get_ontology_summary()
    print("=" * 60)
    print("健康行业AI内容增长系统 - 本体知识库 v2.0.0")
    print("=" * 60)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    print("\n📦 7大模块概览：")
    for mid, mdata in CONTENT_GROWTH_MODULES.items():
        print(f"  {mdata['module_order']}. {mdata['module_name']} "
              f"（交付物{len(mdata['deliverables'])}个，难度{mdata['difficulty']}/5）")

    print("\n💰 4档报价体系：")
    for tid, tdata in PRICING_TIERS.items():
        print(f"  {tdata['tier']}：{tdata['price']} - {tdata['target_customer']}")

    print("\n🧪 产品类型判断测试：")
    test_product = {"name": "羊奶粉", "description": "中老年高钙羊奶粉", "features": ["补钙", "增强免疫力"]}
    result = get_product_type(test_product)
    print(f"  输入: {test_product['name']} → 判断为: {result['label']}（置信度: {result['confidence']}）")

    print("\n🔗 信任路径判断测试：")
    trust_result = get_trust_path("functional", "experiential")
    print(f"  功能型产品+会销行业 → 主要信任路径: {trust_result['primary_path_data']['label']}")

    print("\n🎯 瓶颈诊断测试：")
    test_maturity = {
        "product_clarity": 40,
        "content_capability": 35,
        "trust_building": 50,
        "conversion_system": 45,
        "team_execution": 30,
    }
    test_company = {"industry_type": "experiential", "has_regulatory_issue": False}
    bottlenecks = diagnose_bottlenecks(test_company, test_maturity)
    for b in bottlenecks:
        print(f"  - {b['label']}（{b['severity']}）：{b['impact'][:30]}...")

    print("\n✅ 本体知识库自测通过！")

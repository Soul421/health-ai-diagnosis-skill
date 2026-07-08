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
        "tools": {
            "primary": [
                {"name": "智齿科技", "role": "核心客服系统+AI机器人", "reason": "国内头部智能客服厂商，15000+企业验证，支持多模型接入，独立解决率80%+"},
                {"name": "飞书妙记/企微", "role": "内部协作+工单流转", "reason": "与现有办公系统打通，客服工单无缝流转"},
            ],
            "alternatives": [
                {"name": "网易七鱼", "role": "智能客服+工单", "reason": "网易技术背书，AI能力强，适合中大型企业"},
                {"name": "美洽", "role": "全渠道客服", "reason": "40万+企业客户，获客导向，适合新媒体获客场景"},
                {"name": "腾讯企点", "role": "腾讯生态客服", "reason": "深度集成微信/企微，适合社交流量大的企业"},
            ],
            "description": "全渠道智能客服系统，覆盖官网、公众号、小程序、热线等全部服务渠道，AI机器人自动应答70%+常见问题，人工坐席专注复杂问题。",
        },
        "budget": {
            "light": {
                "tool_cost_year": 15000,
                "implementation_cost": 3000,
                "training_cost": 2000,
                "maintenance_cost_year": 2000,
                "first_year_total": 22000,
                "recurring_year_total": 17000,
                "note": "5坐席以内，基础AI机器人，适合3-5人客服小团队",
            },
            "standard": {
                "tool_cost_year": 50000,
                "implementation_cost": 15000,
                "training_cost": 8000,
                "maintenance_cost_year": 8000,
                "first_year_total": 81000,
                "recurring_year_total": 58000,
                "note": "10-20坐席，全渠道接入+AI质检+客户画像，适合中型客服中心",
            },
            "advanced": {
                "tool_cost_year": 150000,
                "implementation_cost": 50000,
                "training_cost": 20000,
                "maintenance_cost_year": 30000,
                "first_year_total": 250000,
                "recurring_year_total": 180000,
                "note": "30+坐席，私有化部署+多语言+深度定制，适合大型企业/全球化业务",
            },
        },
        "timeline": [
            {"week": 1, "task": "需求梳理+选型确认", "deliverable": "客服需求清单、选型报告"},
            {"week": 2, "task": "系统部署+知识库搭建", "deliverable": "客服系统上线、FAQ知识库（200+问）"},
            {"week": 3, "task": "AI机器人训练+坐席培训", "deliverable": "AI机器人上线、坐席操作手册"},
            {"week": 4, "task": "全渠道接入+联调测试", "deliverable": "全渠道客服接入完成、测试报告"},
            {"week": 5, "task": "试运行+优化调优", "deliverable": "试运行报告、知识库优化迭代"},
            {"week": 6, "task": "正式上线+验收", "deliverable": "正式上线、验收报告、运维手册"},
        ],
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
        "tools": {
            "primary": [
                {"name": "豆包企业版（火山引擎）", "role": "核心内容生成大模型", "reason": "中文内容生成质量领先，月活3.45亿，支持多模态（图文+视频），API按量计费成本可控"},
                {"name": "Canva可画/创客贴", "role": "AI设计+海报生成", "reason": "模板丰富，AI一键生成海报，适合非设计人员快速出图"},
            ],
            "alternatives": [
                {"name": "文心一言（百度智能云）", "role": "内容生成+搜索增强", "reason": "搜索生态加持，适合需要实时信息的内容场景"},
                {"name": "通义千问（阿里云）", "role": "企业级内容生成", "reason": "阿里云生态，性价比高，API调用成本低"},
                {"name": "智谱清言", "role": "PPT+视频生成", "reason": "PPT和短视频生成能力强，适合营销物料多样化需求"},
            ],
            "description": "基于大语言模型的AI内容生产流水线，覆盖文案写作、海报设计、短视频脚本、社媒推文等全场景内容需求，内容产出效率提升3-5倍。",
        },
        "budget": {
            "light": {
                "tool_cost_year": 8000,
                "implementation_cost": 0,
                "training_cost": 2000,
                "maintenance_cost_year": 1000,
                "first_year_total": 11000,
                "recurring_year_total": 9000,
                "note": "2-3人内容团队，豆包加强版+设计工具基础版，月产出50篇内容",
            },
            "standard": {
                "tool_cost_year": 30000,
                "implementation_cost": 5000,
                "training_cost": 8000,
                "maintenance_cost_year": 4000,
                "first_year_total": 47000,
                "recurring_year_total": 34000,
                "note": "5-10人内容团队，企业版大模型API+品牌语料库+多模态生成，月产出200篇内容",
            },
            "advanced": {
                "tool_cost_year": 100000,
                "implementation_cost": 30000,
                "training_cost": 20000,
                "maintenance_cost_year": 15000,
                "first_year_total": 165000,
                "recurring_year_total": 115000,
                "note": "15人以上内容团队，私有化部署+专属模型微调+内容中台，月产出500+篇全渠道内容",
            },
        },
        "timeline": [
            {"week": 1, "task": "工具选型+账号开通", "deliverable": "工具采购清单、账号开通完成"},
            {"week": 2, "task": "品牌语料导入+Prompt工程", "deliverable": "品牌语料库、内容生成Prompt模板（20+套）"},
            {"week": 3, "task": "团队培训+试运行", "deliverable": "培训手册、首批AI生成内容（30篇）"},
            {"week": 4, "task": "流程标准化+正式启用", "deliverable": "内容生产SOP、审核流程规范、正式投入使用"},
        ],
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
        "tools": {
            "primary": [
                {"name": "纷享销客CRM", "role": "销售管理+AI赋能", "reason": "国产智能CRM领军者，快消/制造等行业深度适配，AI助手内置销售话术推荐和客户画像"},
                {"name": "企业微信", "role": "客户沟通+私域沉淀", "reason": "健康行业私域运营主阵地，客户资产沉淀在企业侧"},
            ],
            "alternatives": [
                {"name": "销售易", "role": "PaaS平台型CRM", "reason": "定制化能力强，适合有IT团队的中大型企业"},
                {"name": "超兔CRM", "role": "工贸一体化CRM", "reason": "性价比高，轻量部署，适合中小企业快速上手"},
                {"name": "Zoho CRM", "role": "国际化CRM", "reason": "价格透明，模块化采购，适合有海外业务的企业"},
            ],
            "description": "AI驱动的销售赋能系统，覆盖客户画像分析、销售话术推荐、新人陪练、商机自动跟进等场景，帮助销售团队提升成单率和人效。",
        },
        "budget": {
            "light": {
                "tool_cost_year": 25000,
                "implementation_cost": 8000,
                "training_cost": 5000,
                "maintenance_cost_year": 4000,
                "first_year_total": 42000,
                "recurring_year_total": 29000,
                "note": "10人销售团队，CRM专业版+基础AI功能，适合小型销售团队",
            },
            "standard": {
                "tool_cost_year": 80000,
                "implementation_cost": 30000,
                "training_cost": 15000,
                "maintenance_cost_year": 12000,
                "first_year_total": 137000,
                "recurring_year_total": 92000,
                "note": "30-50人销售团队，CRM旗舰版+AI销售助手+话术库，适合中型销售团队",
            },
            "advanced": {
                "tool_cost_year": 250000,
                "implementation_cost": 100000,
                "training_cost": 40000,
                "maintenance_cost_year": 40000,
                "first_year_total": 430000,
                "recurring_year_total": 290000,
                "note": "100人以上销售团队，私有化部署+定制开发+BI分析+AI陪练系统，适合大型销售组织",
            },
        },
        "timeline": [
            {"week": 1, "task": "业务调研+需求梳理", "deliverable": "业务流程图、需求规格说明书"},
            {"week": 2, "task": "系统选型+方案确认", "deliverable": "选型报告、实施方案、采购合同"},
            {"week": 3, "task": "系统部署+基础配置", "deliverable": "CRM系统部署完成、基础配置到位"},
            {"week": 4, "task": "数据迁移+话术库建设", "deliverable": "历史数据迁移、销售话术库（100+条）"},
            {"week": 5, "task": "AI助手配置+流程定制", "deliverable": "AI销售助手配置完成、销售流程固化"},
            {"week": 6, "task": "团队培训+试运行", "deliverable": "全员培训完成、试运行启动"},
            {"week": 7, "task": "优化调优+制度配套", "deliverable": "优化报告、销售管理制度更新"},
            {"week": 8, "task": "正式上线+验收", "deliverable": "正式上线、验收报告、运维手册"},
        ],
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
        "tools": {
            "primary": [
                {"name": "帆软FineBI", "role": "BI分析平台", "reason": "国产BI龙头，本地化服务强，自助分析能力出色，企业级数据可视化首选"},
                {"name": "飞书多维表格", "role": "轻量数据协作", "reason": "飞书生态内零成本上手，适合快速搭建数据看板和轻量分析"},
            ],
            "alternatives": [
                {"name": "观远数据", "role": "SaaS型BI+AI分析", "reason": "AI分析能力强，SaaS订阅模式，部署快，适合成长型企业"},
                {"name": "Tableau", "role": "国际BI工具", "reason": "可视化能力顶级，适合数据分析团队强的企业"},
                {"name": "Power BI", "role": "微软生态BI", "reason": "与Office无缝集成，性价比高，适合中小团队"},
            ],
            "description": "一站式智能数据分析平台，打通销售、客服、库存、财务等多系统数据，自动生成经营分析报告，支持自然语言问答式查询，让业务人员自助做分析。",
        },
        "budget": {
            "light": {
                "tool_cost_year": 15000,
                "implementation_cost": 5000,
                "training_cost": 3000,
                "maintenance_cost_year": 2000,
                "first_year_total": 25000,
                "recurring_year_total": 17000,
                "note": "5-10人分析用户，BI基础版+3个核心数据看板，适合小企业数据起步",
            },
            "standard": {
                "tool_cost_year": 60000,
                "implementation_cost": 25000,
                "training_cost": 12000,
                "maintenance_cost_year": 10000,
                "first_year_total": 107000,
                "recurring_year_total": 70000,
                "note": "20-30人分析用户，BI专业版+10个业务看板+AI数据分析，适合中型企业数据中台",
            },
            "advanced": {
                "tool_cost_year": 200000,
                "implementation_cost": 80000,
                "training_cost": 30000,
                "maintenance_cost_year": 35000,
                "first_year_total": 345000,
                "recurring_year_total": 235000,
                "note": "50人以上分析用户，企业版+数据仓库+AI智能洞察+移动BI，适合大型企业数据驱动决策",
            },
        },
        "timeline": [
            {"week": 1, "task": "数据调研+需求梳理", "deliverable": "数据源清单、指标体系设计"},
            {"week": 2, "task": "工具选型+方案确认", "deliverable": "选型报告、实施方案"},
            {"week": 3, "task": "数据接入+清洗建模", "deliverable": "3-5个核心数据源接入、数据模型搭建"},
            {"week": 4, "task": "核心看板开发", "deliverable": "经营总览、销售、客服3大核心看板"},
            {"week": 5, "task": "AI分析配置+报表自动化", "deliverable": "AI智能问答配置、自动报表生成"},
            {"week": 6, "task": "培训推广+试运行", "deliverable": "全员培训、试运行报告"},
            {"week": 7, "task": "优化迭代", "deliverable": "需求迭代、性能优化"},
            {"week": 8, "task": "正式上线+验收", "deliverable": "正式上线、验收报告、数据字典"},
        ],
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
        "tools": {
            "primary": [
                {"name": "飞书知识库+知识问答", "role": "知识库+AI问答", "reason": "飞书生态零成本升级，文档协作+AI问答一体化，5分钟搭建可问答的AI知识库"},
                {"name": "飞书妙记", "role": "培训录音转文字", "reason": "培训录音自动转写，生成结构化笔记，方便复习检索"},
            ],
            "alternatives": [
                {"name": "语雀", "role": "知识库+文档协作", "reason": "阿里出品，文档编辑体验好，目录管理清晰，适合内容型团队"},
                {"name": "钉钉知识库", "role": "钉钉生态知识库", "reason": "适合已使用钉钉的企业，与组织架构深度集成"},
                {"name": "企业微信文档", "role": "企微生态文档", "reason": "适合微信生态企业，与客户沟通无缝衔接"},
            ],
            "description": "AI驱动的企业知识管理系统，将产品知识、SOP、培训资料结构化沉淀，支持自然语言问答，员工随时查询，新人培训周期缩短50%以上。",
        },
        "budget": {
            "light": {
                "tool_cost_year": 6000,
                "implementation_cost": 1000,
                "training_cost": 2000,
                "maintenance_cost_year": 1000,
                "first_year_total": 10000,
                "recurring_year_total": 7000,
                "note": "30人以内团队，飞书/语雀基础版+知识库50篇文档，适合小团队知识沉淀起步",
            },
            "standard": {
                "tool_cost_year": 30000,
                "implementation_cost": 8000,
                "training_cost": 8000,
                "maintenance_cost_year": 4000,
                "first_year_total": 50000,
                "recurring_year_total": 34000,
                "note": "100人团队，企业版+AI问答+培训课程体系，知识库200+文档，适合中型企业知识管理",
            },
            "advanced": {
                "tool_cost_year": 80000,
                "implementation_cost": 25000,
                "training_cost": 20000,
                "maintenance_cost_year": 12000,
                "first_year_total": 137000,
                "recurring_year_total": 92000,
                "note": "300人以上企业，私有化部署+专属知识库+学习路径规划+考试系统，适合大型企业培训体系",
            },
        },
        "timeline": [
            {"week": 1, "task": "知识盘点+结构设计", "deliverable": "知识资产清单、知识库架构设计"},
            {"week": 2, "task": "工具部署+核心知识导入", "deliverable": "系统上线、首批50篇核心文档入库"},
            {"week": 3, "task": "AI问答配置+权限设置", "deliverable": "AI问答功能配置完成、权限体系搭建"},
            {"week": 4, "task": "培训推广+试运行", "deliverable": "使用培训完成、全员推广、试运行报告"},
            {"week": 5, "task": "知识持续运营机制建立", "deliverable": "知识运营SOP、知识更新机制"},
            {"week": 6, "task": "验收+正式运行", "deliverable": "验收报告、正式运行"},
        ],
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
        "tools": {
            "primary": [
                {"name": "飞书录音豆+妙记", "role": "录音采集+语音转写", "reason": "硬件+软件一体化，飞书生态内打通，部署简单，成本低，适合连锁门店快速落地"},
                {"name": "lark-cli", "role": "数据批量拉取+分析", "reason": "开源命令行工具，批量获取妙记文本，自动化分析处理"},
                {"name": "飞书多维表格", "role": "话术库+合规规则库", "reason": "零代码搭建标准话术库和合规规则库，灵活可配置"},
            ],
            "alternatives": [
                {"name": "智齿科技智能质检", "role": "客服+门店统一质检", "reason": "适合已有智齿客服的企业，客服+门店统一质检平台"},
                {"name": "科大讯飞质检", "role": "专业语音质检", "reason": "语音识别技术龙头，方言识别准确率高，适合电话/语音为主的场景"},
                {"name": "得助智能（中关村科金）", "role": "金融级合规质检", "reason": "金融级合规能力，多模态统一分析，适合合规要求高的企业"},
            ],
            "description": "通过录音设备采集门店服务对话，AI自动转写、分类、分析，识别合规风险话术和服务问题，每日生成门店服务日报，赋能店长晨会复盘和服务质量提升。",
        },
        "budget": {
            "light": {
                "tool_cost_year": 20000,
                "implementation_cost": 5000,
                "training_cost": 3000,
                "maintenance_cost_year": 2000,
                "first_year_total": 30000,
                "recurring_year_total": 22000,
                "note": "5-10家门店，每店1台录音豆+飞书妙记基础版，每日1小时采样，适合小型连锁试点",
            },
            "standard": {
                "tool_cost_year": 80000,
                "implementation_cost": 25000,
                "training_cost": 12000,
                "maintenance_cost_year": 8000,
                "first_year_total": 125000,
                "recurring_year_total": 88000,
                "note": "20-50家门店，全量录音+AI分析平台+话术库+自动日报，适合中型连锁全面推广",
            },
            "advanced": {
                "tool_cost_year": 250000,
                "implementation_cost": 80000,
                "training_cost": 30000,
                "maintenance_cost_year": 30000,
                "first_year_total": 390000,
                "recurring_year_total": 280000,
                "note": "100家以上门店，私有化部署+视频分析+实时预警+培训闭环，适合大型连锁全链路服务管控",
            },
        },
        "timeline": [
            {"week": 1, "task": "试点门店选择+设备采购", "deliverable": "试点门店清单、录音豆采购到位"},
            {"week": 2, "task": "设备部署+录音测试", "deliverable": "设备安装完成、录音质量测试报告"},
            {"week": 3, "task": "话术库搭建+分析规则配置", "deliverable": "标准话术库（50+条）、合规风险规则（20+条）"},
            {"week": 4, "task": "日报模板设计+自动化配置", "deliverable": "门店服务日报模板、自动化分析流程"},
            {"week": 5, "task": "店长培训+试点运行", "deliverable": "店长培训完成、5家试点门店试运行"},
            {"week": 6, "task": "试点复盘+方案优化", "deliverable": "试点总结报告、方案优化调整"},
            {"week": 7, "task": "批量推广+话术库扩充", "deliverable": "全部门店推广、话术库扩充至100+条"},
            {"week": 8, "task": "验收+运营机制建立", "deliverable": "验收报告、门店服务质量运营机制"},
        ],
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
        "tools": {
            "primary": [
                {"name": "用友U8+/畅捷通T+", "role": "ERP+进销存+供应链", "reason": "国内ERP龙头，500万+企业客户，健康行业方案成熟，财务业务一体化"},
                {"name": "帆软FineBI", "role": "供应链数据分析", "reason": "库存分析、销量预测、补货建议的数据可视化和AI分析"},
            ],
            "alternatives": [
                {"name": "金蝶云星辰/云苍穹", "role": "云原生ERP+供应链", "reason": "金蝶云原生架构，AI智能体丰富，适合成长型到大型企业全覆盖"},
                {"name": "浪潮GS", "role": "大型集团供应链", "reason": "全栈信创，集团化管控强，适合国资/大型集团企业"},
                {"name": "鼎捷ERP", "role": "制造+供应链", "reason": "制造业供应链深耕，生产+供应链一体化能力强"},
            ],
            "description": "基于ERP的智能供应链优化方案，涵盖需求预测、智能补货、库存优化、供应商协同等核心场景，通过AI算法降低库存成本15-30%，减少缺货率20%以上。",
        },
        "budget": {
            "light": {
                "tool_cost_year": 30000,
                "implementation_cost": 15000,
                "training_cost": 8000,
                "maintenance_cost_year": 5000,
                "first_year_total": 58000,
                "recurring_year_total": 35000,
                "note": "小型企业，畅捷通/用友基础版+进销存模块，单仓管理，适合单店/小型批发",
            },
            "standard": {
                "tool_cost_year": 120000,
                "implementation_cost": 60000,
                "training_cost": 25000,
                "maintenance_cost_year": 20000,
                "first_year_total": 225000,
                "recurring_year_total": 140000,
                "note": "中型企业，U8+/金蝶K/3专业版+供应链+需求预测，多仓多店，适合中型连锁/分销",
            },
            "advanced": {
                "tool_cost_year": 400000,
                "implementation_cost": 200000,
                "training_cost": 60000,
                "maintenance_cost_year": 70000,
                "first_year_total": 730000,
                "recurring_year_total": 470000,
                "note": "大型企业，U9 Cloud/云苍穹旗舰版+SRM+智能补货+AI预测，集团化管控，适合大型连锁/供应链集团",
            },
        },
        "timeline": [
            {"week": 1, "task": "业务调研+现状诊断", "deliverable": "供应链现状诊断报告、需求清单"},
            {"week": 2, "task": "系统选型+方案设计", "deliverable": "选型报告、业务蓝图设计"},
            {"week": 3, "task": "基础数据整理+系统部署", "deliverable": "基础数据规范、系统部署完成"},
            {"week": 4, "task": "进销存模块配置+培训", "deliverable": "进销存模块上线、操作培训"},
            {"week": 5, "task": "需求预测模型+库存优化", "deliverable": "需求预测模型、库存优化方案"},
            {"week": 6, "task": "智能补货配置+测试", "deliverable": "智能补货规则、系统测试报告"},
            {"week": 7, "task": "供应商协同+流程优化", "deliverable": "供应商协同方案、流程优化SOP"},
            {"week": 8, "task": "试点运行+数据验证", "deliverable": "试点运行报告、数据验证结果"},
            {"week": 9, "task": "全面推广+制度配套", "deliverable": "全面推广方案、管理制度更新"},
            {"week": 10, "task": "优化迭代", "deliverable": "优化报告、模型调优"},
            {"week": 11, "task": "验收准备", "deliverable": "验收材料准备"},
            {"week": 12, "task": "正式验收+持续优化机制", "deliverable": "验收报告、持续优化机制"},
        ],
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
        "tools": {
            "primary": [
                {"name": "有赞SCRM", "role": "私域全链路运营", "reason": "600万+商家验证，私域+商城闭环，会员全生命周期管理，AI智能标签+营销画布"},
                {"name": "企业微信", "role": "客户连接+社群运营", "reason": "健康行业私域主阵地，客户资产企业化，合规安全"},
            ],
            "alternatives": [
                {"name": "微伴助手", "role": "企微AI SCRM", "reason": "20万+企业客户，AI驱动自动化运营，适合中大型企业全链路私域"},
                {"name": "微盛企微管家", "role": "企微管家+AI", "reason": "腾讯系服务商，AI功能全面，规模化服务能力强"},
                {"name": "小裂变SCRM", "role": "裂变获客+私域", "reason": "AI裂变获客能力强，单客获客成本低，适合拉新需求强的企业"},
            ],
            "description": "AI驱动的私域流量运营系统，覆盖获客、转化、复购全链路，通过客户分层、个性化推送、自动化营销、社群AI运营等手段，提升私域转化率和复购率。",
        },
        "budget": {
            "light": {
                "tool_cost_year": 12000,
                "implementation_cost": 3000,
                "training_cost": 3000,
                "maintenance_cost_year": 2000,
                "first_year_total": 20000,
                "recurring_year_total": 14000,
                "note": "2-3人运营团队，SCRM基础版+企微助手，会员5000以内，适合小企业私域起步",
            },
            "standard": {
                "tool_cost_year": 50000,
                "implementation_cost": 15000,
                "training_cost": 10000,
                "maintenance_cost_year": 6000,
                "first_year_total": 81000,
                "recurring_year_total": 56000,
                "note": "5-10人运营团队，SCRM专业版+AI标签+营销画布+社群运营，会员5万以内，适合中型企业私域体系化运营",
            },
            "advanced": {
                "tool_cost_year": 180000,
                "implementation_cost": 50000,
                "training_cost": 25000,
                "maintenance_cost_year": 25000,
                "first_year_total": 280000,
                "recurring_year_total": 205000,
                "note": "15人以上运营团队，旗舰版+私有化+AI智能运营+数据中台，会员20万+，适合大型企业私域矩阵运营",
            },
        },
        "timeline": [
            {"week": 1, "task": "私域现状诊断+需求梳理", "deliverable": "私域现状诊断报告、需求清单"},
            {"week": 2, "task": "工具选型+方案确认", "deliverable": "选型报告、私域运营方案"},
            {"week": 3, "task": "系统部署+基础配置", "deliverable": "SCRM系统部署、企微助手配置"},
            {"week": 4, "task": "会员体系+标签体系搭建", "deliverable": "会员等级体系、客户标签体系（50+标签）"},
            {"week": 5, "task": "营销画布+自动化配置", "deliverable": "10+自动化营销流程、营销画布模板"},
            {"week": 6, "task": "内容库+话术库建设", "deliverable": "私域内容库、销售话术库"},
            {"week": 7, "task": "团队培训+试运行", "deliverable": "全员培训、试运行启动"},
            {"week": 8, "task": "优化+正式运行", "deliverable": "优化报告、正式运行、数据监测体系"},
        ],
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
        "tools": {
            "primary": [
                {"name": "得助智能（中关村科金）", "role": "全渠道智能质检", "reason": "金融级合规质检标杆，支持语音+文本+视频多模态，私有化部署成熟，合规规则模板丰富"},
                {"name": "飞书妙记+多维表格", "role": "轻量质检+规则库", "reason": "飞书生态内低成本方案，适合门店服务、培训等场景的基础质检"},
            ],
            "alternatives": [
                {"name": "科大讯飞智能质检", "role": "语音质检专家", "reason": "语音识别技术第一，方言识别准，情绪识别成熟，适合电话/语音为主的场景"},
                {"name": "阿里云智能质检", "role": "云原生质检", "reason": "阿里云生态，数据处理规模大，适合已使用阿里云的企业"},
                {"name": "腾讯企点智能质检", "role": "腾讯生态质检", "reason": "腾讯企点生态内，文本质检基础版5000元/年起，适合腾讯系企业"},
            ],
            "description": "AI驱动的全渠道智能质检系统，覆盖客服通话、在线聊天、营销内容、门店服务等场景，自动识别违规话术、敏感词、服务流程问题，全量质检替代人工抽检，合规风险降低60%以上。",
        },
        "budget": {
            "light": {
                "tool_cost_year": 20000,
                "implementation_cost": 5000,
                "training_cost": 3000,
                "maintenance_cost_year": 2000,
                "first_year_total": 30000,
                "recurring_year_total": 22000,
                "note": "10-30坐席，SaaS轻量版+基础质检规则，适合小型客服/门店团队合规起步",
            },
            "standard": {
                "tool_cost_year": 80000,
                "implementation_cost": 25000,
                "training_cost": 12000,
                "maintenance_cost_year": 10000,
                "first_year_total": 127000,
                "recurring_year_total": 90000,
                "note": "50-100坐席，标准SaaS版+三模质检+风险分级告警+API集成，适合中型企业全面合规管控",
            },
            "advanced": {
                "tool_cost_year": 250000,
                "implementation_cost": 80000,
                "training_cost": 30000,
                "maintenance_cost_year": 35000,
                "first_year_total": 395000,
                "recurring_year_total": 285000,
                "note": "200+坐席，私有化部署+全链路质检+实时预警+深度定制+驻场服务，适合大型企业/金融级合规",
            },
        },
        "timeline": [
            {"week": 1, "task": "合规需求调研+风险盘点", "deliverable": "合规风险清单、质检需求规格书"},
            {"week": 2, "task": "工具选型+方案确认", "deliverable": "选型报告、质检方案设计"},
            {"week": 3, "task": "系统部署+质检规则配置", "deliverable": "系统部署完成、首批30+质检规则配置"},
            {"week": 4, "task": "数据对接+测试验证", "deliverable": "多渠道数据对接、质检准确率测试报告"},
            {"week": 5, "task": "规则优化+告警机制", "deliverable": "规则优化调整、风险分级告警机制"},
            {"week": 6, "task": "团队培训+试运行", "deliverable": "质检团队培训、试运行启动"},
            {"week": 7, "task": "流程优化+制度配套", "deliverable": "质检流程SOP、合规管理制度更新"},
            {"week": 8, "task": "验收+持续运营", "deliverable": "验收报告、质检运营机制"},
        ],
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
        "tools": {
            "primary": [
                {"name": "有赞AI推荐+商品分析", "role": "电商推荐+选品分析", "reason": "600万+商家数据沉淀，与商城系统深度打通，AI智能推荐+商品画像+选品分析一体化"},
                {"name": "帆软FineBI", "role": "销售数据分析", "reason": "销售数据多维度分析，客户分层+产品分析支撑选品决策"},
            ],
            "alternatives": [
                {"name": "阿里云智能推荐", "role": "企业级推荐引擎", "reason": "阿里电商技术积累，推荐算法成熟，适合技术型团队自建推荐系统"},
                {"name": "腾讯智能推荐", "role": "社交+内容推荐", "reason": "腾讯社交数据加持，适合社交电商和内容电商场景"},
                {"name": "第三方选品工具（卖家精灵等）", "role": "跨境/电商选品", "reason": "适合跨境电商和平台电商的选品调研，数据维度丰富"},
            ],
            "description": "基于客户画像和消费行为数据的AI智能推荐系统，通过千人千面的产品推荐、关联销售、智能选品等功能，提升客单价15-30%，交叉销售率提升20%以上。",
        },
        "budget": {
            "light": {
                "tool_cost_year": 15000,
                "implementation_cost": 3000,
                "training_cost": 2000,
                "maintenance_cost_year": 2000,
                "first_year_total": 22000,
                "recurring_year_total": 17000,
                "note": "单店/小型电商，有赞专业版+基础推荐+选品分析，SKU 500以内，适合小企业选品起步",
            },
            "standard": {
                "tool_cost_year": 50000,
                "implementation_cost": 15000,
                "training_cost": 8000,
                "maintenance_cost_year": 6000,
                "first_year_total": 79000,
                "recurring_year_total": 56000,
                "note": "多店/中型电商，有赞旗舰版+AI智能推荐+商品画像+选品模型，SKU 2000以内，适合中型企业精细化选品",
            },
            "advanced": {
                "tool_cost_year": 150000,
                "implementation_cost": 50000,
                "training_cost": 20000,
                "maintenance_cost_year": 20000,
                "first_year_total": 240000,
                "recurring_year_total": 170000,
                "note": "大型连锁/平台，自建推荐引擎+用户画像平台+实时推荐+AB测试，SKU 1万+，适合大型企业个性化推荐体系",
            },
        },
        "timeline": [
            {"week": 1, "task": "商品盘点+客户画像分析", "deliverable": "商品清单、客户分层模型"},
            {"week": 2, "task": "工具选型+方案设计", "deliverable": "选型报告、推荐方案设计"},
            {"week": 3, "task": "系统部署+数据接入", "deliverable": "系统部署完成、销售/会员数据接入"},
            {"week": 4, "task": "推荐模型配置+商品标签", "deliverable": "商品标签体系（100+标签）、推荐规则配置"},
            {"week": 5, "task": "选品分析模型+报表", "deliverable": "选品分析模型、商品销售分析报表"},
            {"week": 6, "task": "测试调优+培训", "deliverable": "AB测试报告、运营团队培训"},
            {"week": 7, "task": "试运行+效果验证", "deliverable": "试运行报告、推荐效果验证数据"},
            {"week": 8, "task": "正式上线+持续优化", "deliverable": "正式上线、持续优化机制"},
        ],
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
        "version": "1.11.0",
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

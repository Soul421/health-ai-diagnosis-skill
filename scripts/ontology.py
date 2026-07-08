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
            "options": [
                {
                    "name": "轻量SaaS方案",
                    "components": ["美洽", "企业微信客服"],
                    "approach": "基于轻量SaaS客服系统，快速搭建全渠道接入+基础AI机器人",
                    "pros": ["价格低，按坐席计费，5坐席年付不到2万", "部署快，3-5天即可上线", "操作简单，客服上手快"],
                    "cons": ["AI能力较基础，复杂问题解决率一般", "高级功能（质检、CRM打通）需额外付费", "定制化能力弱"],
                    "fit_for": "10人以下客服小团队、初创企业、预算有限的门店",
                    "price_start": "1.5万/年起（5坐席）",
                    "difficulty": "低",
                },
                {
                    "name": "全渠道智能客服方案",
                    "components": ["智齿科技", "AI机器人", "工单系统"],
                    "approach": "头部智能客服厂商方案，全渠道接入+AI机器人+质检+CRM一体化",
                    "pros": ["AI独立解决率80%+，大幅减少人工坐席", "15000+企业验证，健康行业有成熟案例", "全渠道统一工作台，客服效率提升50%以上"],
                    "cons": ["价格相对较高，中大型方案年付5万起", "实施周期2-4周，需要专人对接", "部分高级功能需额外采购"],
                    "fit_for": "中型企业、10-30人客服团队、连锁药房/医疗机构客服中心",
                    "price_start": "5万/年起（10坐席）",
                    "difficulty": "中",
                },
                {
                    "name": "腾讯生态客服方案",
                    "components": ["腾讯企点", "企业微信", "微信客服"],
                    "approach": "腾讯生态内深度整合，微信/企微/公众号/小程序全渠道客服",
                    "pros": ["与微信/企微深度打通，社交流量无缝衔接", "客户资产沉淀在企微，便于私域运营", "腾讯技术背书，数据安全合规"],
                    "cons": ["非腾讯生态渠道（如官网、热线）支持较弱", "AI能力中等，复杂场景需额外对接大模型", "价格不透明，按需报价"],
                    "fit_for": "微信/企微流量为主的企业、公众号/小程序运营型企业、私域导向的健康品牌",
                    "price_start": "3万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "企业级旗舰方案",
                    "components": ["网易七鱼企业版", "私有化部署", "多语言支持"],
                    "approach": "中大型企业级智能客服，支持私有化部署+深度定制+全球化",
                    "pros": ["网易技术背书，AI能力行业领先", "私有化部署，数据安全有保障", "支持多语言、多区域、复杂路由", "定制化能力强，可对接内部系统"],
                    "cons": ["价格高，企业版年付15万起", "实施周期长，1-2个月", "需要IT团队配合维护"],
                    "fit_for": "大型企业/集团、全球化业务、合规要求高的药企/医疗机构",
                    "price_start": "15万/年起",
                    "difficulty": "高",
                },
            ],
            "selection_guide": "预算少、团队小选轻量SaaS方案；客服体量大、追求AI效果选全渠道智能客服方案；微信/私域流量为主选腾讯生态客服方案；大型企业/合规要求高选企业级旗舰方案。",
            "note": "价格为2026年市场参考价，实际以厂商报价为准",
        },        "budget": {
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
            "options": [
                {
                    "name": "入门创作套餐",
                    "components": ["豆包个人版", "创客贴基础版"],
                    "approach": "个人级大模型+在线设计工具，低成本快速提升内容产出",
                    "pros": ["成本极低，年投入不到1万", "即开即用，零学习成本", "覆盖文案+海报基础需求"],
                    "cons": ["个人版无法保证数据隐私", "品牌风格一致性弱", "团队协作功能缺失"],
                    "fit_for": "2-3人小团队、初创公司、内容产出量不大的企业",
                    "price_start": "0.8万/年起",
                    "difficulty": "低",
                },
                {
                    "name": "企业级内容中台方案",
                    "components": ["豆包企业版（火山引擎）", "Canva可画企业版", "品牌语料库"],
                    "approach": "企业级大模型+专业设计工具+品牌语料库，内容生产流水线化",
                    "pros": ["中文内容生成质量领先，月活3.45亿用户验证", "品牌语料库确保风格一致，输出可控", "多模态生成（文案+海报+短视频脚本）", "API按量计费，成本可控"],
                    "cons": ["企业版年投入3万起", "需要专人维护语料库和Prompt模板", "设计工具需单独付费"],
                    "fit_for": "5-10人内容团队、中型健康品牌、月产出200篇以上内容的企业",
                    "price_start": "3万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "阿里生态内容方案",
                    "components": ["通义千问（阿里云）", "钉钉文档", "魔搭社区模型"],
                    "approach": "阿里云生态内一站式内容生产，与钉钉/阿里云服务深度集成",
                    "pros": ["阿里云生态，数据打通方便", "API调用成本低，性价比高", "钉钉文档协作+AI生成一体化", "模型选择丰富，魔搭社区按需调用"],
                    "cons": ["内容生成质量略逊于豆包/文心", "非阿里云用户迁移成本高", "设计工具需额外对接"],
                    "fit_for": "已使用阿里云/钉钉的企业、技术驱动型团队、成本敏感型企业",
                    "price_start": "2万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "私有化内容工厂方案",
                    "components": ["私有化部署大模型", "专属模型微调", "内容中台系统"],
                    "approach": "私有化部署+专属模型微调+内容中台，数据安全+品牌定制双保障",
                    "pros": ["数据不出企业，健康数据安全有保障", "专属模型微调，品牌风格高度一致", "内容中台统一管理，全渠道分发", "支持复杂的内容审核流程"],
                    "cons": ["投入大，首年10万以上", "实施周期长，2-3个月", "需要IT团队持续维护"],
                    "fit_for": "大型健康集团、合规要求高的药企、15人以上内容团队",
                    "price_start": "10万/年起",
                    "difficulty": "高",
                },
            ],
            "selection_guide": "小团队低成本试手选入门创作套餐；追求内容质量和品牌一致性选企业级内容中台方案；阿里云/钉钉用户选阿里生态内容方案；数据安全要求高的大企业选私有化内容工厂方案。",
            "note": "价格为2026年市场参考价，实际以厂商报价为准",
        },        "budget": {
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
            "options": [
                {
                    "name": "轻量CRM方案",
                    "components": ["超兔CRM", "企业微信"],
                    "approach": "轻量化CRM+企微客户管理，快速上手，满足基础销售管理需求",
                    "pros": ["性价比高，10人团队年付2.5万起", "工贸一体化，适合产供销一体企业", "部署快，1-2周即可上线"],
                    "cons": ["AI功能较基础，高级销售助手需升级", "定制化能力有限", "生态集成度一般"],
                    "fit_for": "10人以下销售小团队、中小企业、工贸一体化健康产品企业",
                    "price_start": "2.5万/年起（10用户）",
                    "difficulty": "低",
                },
                {
                    "name": "智能CRM方案",
                    "components": ["纷享销客CRM", "AI销售助手", "话术库"],
                    "approach": "国产智能CRM领军者，AI助手内置话术推荐+客户画像+商机管理",
                    "pros": ["快消/健康行业深度适配，有成熟案例", "AI销售助手实时话术推荐，新人上手快", "客户画像+商机分析，销售决策有数据支撑", "PaaS平台支持一定程度定制"],
                    "cons": ["中大型方案年投入8万起", "实施周期1-2个月", "需要销售管理层推动使用"],
                    "fit_for": "30-50人销售团队、中型健康企业、连锁门店销售体系、会销企业",
                    "price_start": "8万/年起（30用户）",
                    "difficulty": "中",
                },
                {
                    "name": "企微私域销售方案",
                    "components": ["企业微信", "微伴助手/微盛", "SCRM销售助手"],
                    "approach": "以企微为核心的私域销售体系，客户连接+销售赋能+社群运营一体化",
                    "pros": ["客户资产企业化，销售离职不带走客户", "AI话术推荐+客户画像+自动跟进", "与私域运营无缝衔接，获客+转化+复购全链路"],
                    "cons": ["偏私域场景，B端复杂销售流程支持有限", "AI能力依赖第三方SCRM厂商", "深度定制需技术对接"],
                    "fit_for": "私域导向的健康品牌、DTC模式企业、社群销售为主的会销/体验营销企业",
                    "price_start": "5万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "PaaS平台定制方案",
                    "components": ["销售易CRM", "PaaS平台定制", "BI分析+AI陪练"],
                    "approach": "PaaS平台型CRM，支持深度定制，适合复杂销售流程和大型销售组织",
                    "pros": ["定制化能力强，适配复杂销售流程", "100人以上大团队管理能力强", "BI+AI+流程自动化全链路", "国际化能力较好"],
                    "cons": ["价格高，年投入25万起", "实施周期2-3个月", "需要IT团队或外包维护"],
                    "fit_for": "100人以上大型销售团队、集团型企业、有IT团队的中大型健康企业",
                    "price_start": "25万/年起",
                    "difficulty": "高",
                },
            ],
            "selection_guide": "小团队快上手选轻量CRM方案；中型销售团队追求AI赋能选智能CRM方案；私域/社群销售为主选企微私域销售方案；大型销售组织需要定制选PaaS平台定制方案。",
            "note": "价格为2026年市场参考价，实际以厂商报价为准",
        },        "budget": {
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
            "options": [
                {
                    "name": "零代码轻量分析方案",
                    "components": ["飞书多维表格", "飞书仪表盘"],
                    "approach": "零代码搭建数据看板，业务人员自助做分析，快速见效",
                    "pros": ["飞书用户零成本上手，几乎无额外投入", "拖拽式操作，业务人员也能做看板", "实时协作，数据自动更新", "适合快速搭建轻量数据看板"],
                    "cons": ["大数据量处理能力有限", "复杂分析和AI洞察能力不足", "无法对接复杂的业务系统"],
                    "fit_for": "5-10人小团队、飞书用户、数字化基础薄弱的企业、快速验证数据价值",
                    "price_start": "0.5万/年起（飞书升级费用）",
                    "difficulty": "低",
                },
                {
                    "name": "SaaS型BI方案",
                    "components": ["观远数据", "AI分析助手"],
                    "approach": "SaaS订阅式BI平台，AI智能分析+自助看板+移动BI，部署快效果好",
                    "pros": ["AI分析能力强，自然语言问答+自动洞察", "SaaS模式，部署快，2-3周上线", "移动BI支持，管理层随时看数据", "性价比高，比传统BI便宜50%"],
                    "cons": ["超大数据量性能不如传统重型BI", "私有化部署版本价格翻倍", "高级定制能力有限"],
                    "fit_for": "中型企业、20-30人分析用户、成长型健康品牌、追求快速见效的数据团队",
                    "price_start": "6万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "企业级BI方案",
                    "components": ["帆软FineBI", "数据仓库", "AI智能洞察"],
                    "approach": "国产BI龙头企业级方案，大数据量+深度分析+企业级管控",
                    "pros": ["国产BI第一，本地化服务强", "大数据量处理能力强，支持亿级数据", "企业级权限管控，合规性好", "生态丰富，可对接几乎所有数据源"],
                    "cons": ["价格高，企业版年付20万起", "实施周期1-2个月", "需要专业数据分析人员维护"],
                    "fit_for": "大型企业、50人以上分析用户、数据量大的连锁/集团、合规要求高的药企",
                    "price_start": "20万/年起",
                    "difficulty": "高",
                },
                {
                    "name": "微软生态方案",
                    "components": ["Power BI", "Excel", "Azure云服务"],
                    "approach": "微软生态内数据分析方案，与Office/Azure无缝集成",
                    "pros": ["与Excel/Office无缝衔接，员工学习成本低", "性价比高，基础版几千元/年", "Azure云生态，可扩展到高级分析", "适合熟悉微软技术栈的团队"],
                    "cons": ["国内本地化服务不如国产BI", "复杂中国式报表支持较弱", "AI分析功能在国内版功能有限"],
                    "fit_for": "微软技术栈企业、外企/合资企业、Excel重度用户的中小团队",
                    "price_start": "1.5万/年起",
                    "difficulty": "中",
                },
            ],
            "selection_guide": "飞书用户、预算少选零代码轻量分析方案；追求AI分析、快速部署选SaaS型BI方案；大型企业、数据量大选企业级BI方案；微软/Office生态选微软生态方案。",
            "note": "价格为2026年市场参考价，实际以厂商报价为准",
        },        "budget": {
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
            "options": [
                {
                    "name": "飞书轻量知识库方案",
                    "components": ["飞书文档", "飞书知识库", "飞书知识问答"],
                    "approach": "飞书生态内零成本升级，文档协作+AI问答一体化，5分钟搭建可问答的知识库",
                    "pros": ["飞书用户几乎零成本，基础版免费", "文档编辑体验好，团队协作顺畅", "AI问答一键开启，快速见效", "妙记自动转写培训录音，生成结构化笔记"],
                    "cons": ["专业培训功能（考试、学习路径）较弱", "大型组织权限管理稍显不足", "非飞书用户迁移成本高"],
                    "fit_for": "30人以内小团队、飞书用户、知识沉淀起步阶段、轻量培训需求",
                    "price_start": "0.6万/年起（飞书升级费用）",
                    "difficulty": "低",
                },
                {
                    "name": "企业知识管理方案",
                    "components": ["飞书知识库企业版", "飞书妙记", "培训课程体系"],
                    "approach": "企业级知识库+AI问答+培训体系，知识沉淀+员工培训一体化",
                    "pros": ["AI问答准确率高，支持多轮对话", "妙记转写培训录音，自动生成学习笔记", "培训课程体系+学习进度跟踪", "权限管理完善，适合多部门多角色"],
                    "cons": ["专业考试功能需对接第三方", "深度定制化能力有限", "年投入3万起，需持续运营"],
                    "fit_for": "100人左右中型企业、知识密集型团队、有体系化培训需求的健康企业",
                    "price_start": "3万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "钉钉/企微生态方案",
                    "components": ["钉钉知识库/企微文档", "钉钉培训/企微上课"],
                    "approach": "钉钉/企微生态内知识管理+培训，与组织架构深度集成",
                    "pros": ["与现有办公系统打通，无需额外安装", "组织架构自动同步，人员管理方便", "钉钉有成熟的培训/考试功能", "成本较低，基础版几千元/年"],
                    "cons": ["AI问答能力不如飞书/专用知识库", "文档编辑体验一般", "知识库结构管理相对简单"],
                    "fit_for": "已使用钉钉/企微的企业、组织架构复杂的连锁门店、传统型企业",
                    "price_start": "1万/年起",
                    "difficulty": "低",
                },
                {
                    "name": "企业大学方案",
                    "components": ["私有化知识库", "在线学习平台", "考试系统"],
                    "approach": "私有化部署的企业级知识管理+在线学习平台，适合大型企业培训体系",
                    "pros": ["私有化部署，数据安全有保障", "完整的学习路径+考试+证书体系", "支持千人同时在线学习", "可深度定制，对接HR系统"],
                    "cons": ["投入大，首年8万以上", "实施周期2-3个月", "需要专人运营维护"],
                    "fit_for": "300人以上大型企业、连锁门店总部培训体系、有完善HR培训部门的企业",
                    "price_start": "8万/年起",
                    "difficulty": "高",
                },
            ],
            "selection_guide": "飞书用户、小团队选飞书轻量知识库方案；中型企业体系化知识管理选企业知识管理方案；钉钉/企微用户选钉钉/企微生态方案；大型企业完整培训体系选企业大学方案。",
            "note": "价格为2026年市场参考价，实际以厂商报价为准",
        },        "budget": {
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
            "options": [
                {
                    "name": "飞书录音豆方案",
                    "components": ["飞书录音豆", "飞书妙记", "飞书多维表格", "lark-cli"],
                    "approach": "硬件+软件一体化的飞书生态方案，录音采集+AI转写+自动日报，低成本快速落地",
                    "pros": ["部署简单，硬件开箱即用，软件飞书内打通", "成本低，5家门店试点首年3万以内", "多维表格灵活搭建话术库和规则库", "lark-cli批量处理，自动化程度高"],
                    "cons": ["仅支持语音，不支持视频分析", "高级质检功能需自行开发", "门店数量多后管理成本上升"],
                    "fit_for": "5-20家小型连锁、飞书用户、预算有限想快速验证的门店、店长负责制的门店体系",
                    "price_start": "2万/年起（5家门店）",
                    "difficulty": "低",
                },
                {
                    "name": "客服联动质检方案",
                    "components": ["智齿科技智能质检", "智齿客服系统"],
                    "approach": "客服+门店统一质检平台，适合已有智齿客服的企业延伸到门店场景",
                    "pros": ["客服+门店统一质检平台，数据打通", "AI质检能力成熟，规则模板丰富", "适合已有智齿客服的企业，增量投入少", "支持语音+文本多渠道质检"],
                    "cons": ["门店端录音采集需额外对接硬件", "门店场景的适配不如专用方案", "中大型方案年投入8万起"],
                    "fit_for": "已有智齿客服的企业、客服+门店均需质检的企业、20-50家门店的中型连锁",
                    "price_start": "8万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "专业语音质检方案",
                    "components": ["科大讯飞智能质检", "录音采集设备", "质检分析平台"],
                    "approach": "专业语音技术厂商方案，方言识别+情绪识别+全量质检，准确率行业领先",
                    "pros": ["语音识别技术龙头，方言/口音识别准确率高", "情绪识别成熟，可检测服务态度问题", "支持大规模并发，百店以上无压力", "健康/医疗行业有成熟案例"],
                    "cons": ["价格较高，中大型方案年投入15万起", "实施周期1-2个月", "需要专业人员维护质检规则"],
                    "fit_for": "50家以上中大型连锁、方言多的区域连锁、对语音识别准确率要求高的企业",
                    "price_start": "15万/年起",
                    "difficulty": "高",
                },
                {
                    "name": "金融级合规质检方案",
                    "components": ["得助智能（中关村科金）", "多模态质检", "实时预警"],
                    "approach": "金融级合规质检方案，语音+文本+视频多模态，实时预警+深度定制",
                    "pros": ["金融级合规能力，合规规则模板丰富", "多模态统一分析（语音+文本+视频）", "实时预警，违规问题即时发现", "私有化部署成熟，数据安全有保障"],
                    "cons": ["价格高，年投入25万起", "实施周期2-3个月", "功能偏重，小企业用不上全部功能"],
                    "fit_for": "合规要求高的药企/医疗机构、100家以上大型连锁、需要视频+语音多模态质检的企业",
                    "price_start": "25万/年起",
                    "difficulty": "高",
                },
            ],
            "selection_guide": "飞书用户、少量门店快速验证选飞书录音豆方案；已有智齿客服的企业选客服联动质检方案；门店多、方言复杂选专业语音质检方案；合规要求极高的大企业选金融级合规质检方案。",
            "note": "价格为2026年市场参考价，实际以厂商报价为准",
        },        "budget": {
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
            "options": [
                {
                    "name": "轻量进销存方案",
                    "components": ["畅捷通T+", "用友基础版"],
                    "approach": "小型企业进销存+基础供应链管理，财务业务一体化，快速上手",
                    "pros": ["成本低，首年3万以内", "财务业务一体化，做账+库存+采购一套搞定", "用友旗下产品，升级路径清晰", "本地化服务网点多"],
                    "cons": ["AI预测和智能补货功能较弱", "大规模多仓管理能力有限", "定制化程度不高"],
                    "fit_for": "小型企业、单仓管理、10人以下供应链团队、年营收5000万以下",
                    "price_start": "3万/年起",
                    "difficulty": "低",
                },
                {
                    "name": "成长型企业供应链方案",
                    "components": ["用友U8+", "供应链模块", "需求预测"],
                    "approach": "中型企业级ERP+供应链管理，需求预测+智能补货+多仓管理",
                    "pros": ["国产ERP龙头，500万+企业验证", "健康行业有成熟解决方案", "供应链+财务+生产一体化", "服务网络完善，本地实施能力强"],
                    "cons": ["中大型方案首年投入12万起", "实施周期2-3个月", "需要专人维护系统"],
                    "fit_for": "中型企业、多仓多店、年营收5000万-5亿、有专职供应链团队的健康企业",
                    "price_start": "12万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "云原生智能供应链方案",
                    "components": ["金蝶云苍穹/云星辰", "AI智能体", "SRM供应商协同"],
                    "approach": "金蝶云原生ERP+AI智能供应链，支持从采购到仓储到配送全链路智能化",
                    "pros": ["云原生架构，弹性扩展，上线快", "AI智能体丰富，需求预测+智能补货+异常预警", "从小型到大型企业全覆盖，升级平滑", "移动端体验好，随时随地处理业务"],
                    "cons": ["大型方案价格高，年投入40万起", "深度定制需要金蝶生态伙伴", "老系统数据迁移有成本"],
                    "fit_for": "成长型到大型企业、重视云原生和AI能力、多组织多地点的集团型健康企业",
                    "price_start": "25万/年起",
                    "difficulty": "高",
                },
                {
                    "name": "钉钉/氚云轻定制方案",
                    "components": ["钉钉", "氚云/简道云", "钉钉宜搭"],
                    "approach": "钉钉生态内低代码搭建供应链系统，灵活定制，成本可控",
                    "pros": ["钉钉用户零学习成本，组织架构同步", "低代码搭建，按需定制，灵活调整", "成本低，基础版几万块就能用", "上线快，2-4周即可投入使用"],
                    "cons": ["复杂供应链场景支持有限", "大数据量性能不如专业ERP", "AI预测等高级功能较弱"],
                    "fit_for": "钉钉用户、中小企业、需求变化快的企业、预算有限想先跑通流程的企业",
                    "price_start": "5万/年起",
                    "difficulty": "中",
                },
            ],
            "selection_guide": "小企业快上手选轻量进销存方案；中型企业一体化管理选成长型企业供应链方案；追求云原生和AI能力选云原生智能供应链方案；钉钉用户、预算有限选钉钉/氚云轻定制方案。",
            "note": "价格为2026年市场参考价，实际以厂商报价为准",
        },        "budget": {
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
            "options": [
                {
                    "name": "轻量私域起步方案",
                    "components": ["企业微信", "小裂变SCRM基础版"],
                    "approach": "企微+轻量SCRM，低成本搭建私域基础，适合私域运营起步阶段",
                    "pros": ["成本低，首年1-2万即可起步", "上手快，1-2周即可开始运营", "裂变获客能力强，单客获客成本低", "适合验证私域价值"],
                    "cons": ["功能较基础，高级自动化能力有限", "大规模运营后需要升级", "数据深度分析能力一般"],
                    "fit_for": "2-3人运营小团队、私域起步阶段、会员5000以内、拉新需求强的健康品牌",
                    "price_start": "1.2万/年起",
                    "difficulty": "低",
                },
                {
                    "name": "私域全链路运营方案",
                    "components": ["有赞SCRM", "企业微信", "有赞商城"],
                    "approach": "有赞SCRM+商城+企微，获客-转化-复购全链路私域运营闭环",
                    "pros": ["600万+商家验证，私域+商城闭环", "AI智能标签+营销画布，自动化程度高", "会员全生命周期管理", "健康/美妆行业有成熟方案"],
                    "cons": ["中大型方案年投入5万起", "与非有赞商城对接需要额外开发", "部分高级功能需单独付费"],
                    "fit_for": "5-10人运营团队、会员5万以内、有赞商城用户、追求私域+商城一体化的健康品牌",
                    "price_start": "5万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "企微AI深度运营方案",
                    "components": ["微伴助手/微盛企微管家", "企业微信", "AI运营助手"],
                    "approach": "腾讯系SCRM厂商方案，企微深度集成+AI自动化运营，适合中大型企业",
                    "pros": ["企微深度集成，功能全面", "AI驱动自动化运营，千人千面推送", "社群AI运营，7x24小时自动回复", "规模化服务能力强，支持大团队"],
                    "cons": ["旗舰版年投入18万起", "功能多上手需要时间", "需要持续运营才能发挥效果"],
                    "fit_for": "10人以上运营团队、会员20万+、中大型健康品牌、重视AI自动化运营的企业",
                    "price_start": "18万/年起",
                    "difficulty": "高",
                },
                {
                    "name": "腾讯生态私域方案",
                    "components": ["微盛企微管家", "腾讯云", "微信生态工具"],
                    "approach": "腾讯系服务商方案，微信生态内全链路私域，官方合作有保障",
                    "pros": ["腾讯官方授权，接口稳定有保障", "微信生态工具最全，视频号+公众号+小程序打通", "数据安全合规，腾讯云背书", "适合腾讯生态内的深度玩法"],
                    "cons": ["非腾讯生态渠道支持弱", "价格不透明，按需报价", "定制化需要通过服务商"],
                    "fit_for": "微信/视频号流量为主的企业、腾讯云用户、重视生态打通的健康品牌",
                    "price_start": "8万/年起",
                    "difficulty": "中",
                },
            ],
            "selection_guide": "私域起步、预算少先选轻量私域起步方案；有赞商城用户、追求全链路闭环选私域全链路运营方案；中大型企业重视AI运营选企微AI深度运营方案；腾讯生态重度用户选腾讯生态私域方案。",
            "note": "价格为2026年市场参考价，实际以厂商报价为准",
        },        "budget": {
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
            "options": [
                {
                    "name": "飞书轻量质检方案",
                    "components": ["飞书妙记", "飞书多维表格", "合规规则库"],
                    "approach": "飞书生态内低成本方案，语音转写+规则库+人工抽检，适合基础质检需求",
                    "pros": ["成本极低，飞书用户几乎零成本上手", "多维表格灵活搭建合规规则库", "妙记转写准确率高，支持多人讨论", "适合门店服务、培训等场景的基础质检"],
                    "cons": ["全量自动质检需要人工配置规则", "视频质检不支持", "大规模并发处理能力有限"],
                    "fit_for": "10-30人小团队、飞书用户、基础合规需求、预算有限先跑通质检流程的企业",
                    "price_start": "2万/年起",
                    "difficulty": "低",
                },
                {
                    "name": "专业语音质检方案",
                    "components": ["科大讯飞智能质检", "语音识别引擎", "质检分析平台"],
                    "approach": "语音识别龙头企业方案，方言识别+情绪识别+全量质检，准确率行业领先",
                    "pros": ["语音识别技术第一，方言/口音识别准", "情绪识别成熟，可检测服务态度问题", "全量质检替代人工抽检，覆盖率100%", "健康/医疗行业有成熟方案"],
                    "cons": ["中大型方案年投入8万起", "视频质检需要额外采购模块", "实施需要1-2个月"],
                    "fit_for": "50-100坐席、电话/语音为主的客服中心、方言多的区域企业、连锁门店语音质检",
                    "price_start": "8万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "全渠道合规质检方案",
                    "components": ["得助智能（中关村科金）", "多模态质检", "实时预警"],
                    "approach": "金融级全渠道智能质检，语音+文本+视频多模态，合规规则模板丰富",
                    "pros": ["金融级合规能力，健康行业合规规则模板现成可用", "多模态统一分析（语音+文本+视频+图片）", "实时预警，违规问题即时发现处理", "私有化部署成熟，数据安全有保障"],
                    "cons": ["价格高，企业版年投入25万起", "实施周期2-3个月", "功能丰富但需要专业团队运营"],
                    "fit_for": "合规要求高的药企/医疗机构、200+坐席大型客服中心、需要全渠道全模态质检的企业",
                    "price_start": "25万/年起",
                    "difficulty": "高",
                },
                {
                    "name": "阿里云原生质检方案",
                    "components": ["阿里云智能质检", "阿里云语音", "阿里云数据中台"],
                    "approach": "阿里云生态内智能质检，云原生架构，弹性扩展，适合阿里云用户",
                    "pros": ["阿里云生态，数据打通方便", "云原生架构，按需付费，弹性扩展", "数据处理规模大，支持海量并发", "阿里云用户统一账单，管理方便"],
                    "cons": ["非阿里云用户迁移成本高", "实施需要阿里云生态伙伴", "行业定制模板不如垂直厂商丰富"],
                    "fit_for": "阿里云用户、云原生架构企业、数据量大的互联网型健康企业",
                    "price_start": "6万/年起",
                    "difficulty": "中",
                },
            ],
            "selection_guide": "飞书用户、小团队、预算少先选飞书轻量质检方案；语音为主、追求准确率选专业语音质检方案；合规要求高、多模态需求选全渠道合规质检方案；阿里云用户选阿里云原生质检方案。",
            "note": "价格为2026年市场参考价，实际以厂商报价为准",
        },        "budget": {
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
            "options": [
                {
                    "name": "电商平台内置AI推荐方案",
                    "components": ["有赞AI推荐", "有赞商品分析"],
                    "approach": "基于有赞商城的内置AI推荐功能，与商城深度打通，开箱即用",
                    "pros": ["与商城系统深度打通，数据无缝衔接", "600万+商家数据沉淀，推荐算法成熟", "部署快，开通即用，几乎零实施成本", "商品画像+选品分析+推荐一体化"],
                    "cons": ["仅限有赞生态，跨平台能力弱", "推荐算法深度定制能力有限", "SKU太多时效果打折扣"],
                    "fit_for": "有赞商城用户、单店/小型电商、SKU 500以内、想快速验证推荐效果的健康品牌",
                    "price_start": "1.5万/年起",
                    "difficulty": "低",
                },
                {
                    "name": "精细化选品推荐方案",
                    "components": ["有赞旗舰版", "AI智能推荐", "商品画像+选品模型"],
                    "approach": "电商平台高级版+AI智能推荐+选品分析，适合多店中型电商精细化运营",
                    "pros": ["AI智能推荐+商品画像+选品模型全链路", "支持多店统一管理，数据汇总分析", "千人千面推荐，客单价提升15-30%", "关联销售+交叉销售，复购率提升"],
                    "cons": ["旗舰版年投入5万起", "需要有专人运营优化推荐模型", "数据积累不够时效果一般"],
                    "fit_for": "多店/中型电商、SKU 2000以内、有运营团队、追求精细化选品的健康品牌",
                    "price_start": "5万/年起",
                    "difficulty": "中",
                },
                {
                    "name": "企业级推荐引擎方案",
                    "components": ["阿里云智能推荐", "用户画像平台", "AB测试平台"],
                    "approach": "阿里电商技术沉淀的企业级推荐引擎，支持自建推荐系统，深度定制",
                    "pros": ["阿里电商技术积累，推荐算法行业领先", "企业级SLA，稳定性有保障", "支持深度定制和自有算法接入", "用户画像+推荐+AB测试全链路"],
                    "cons": ["技术门槛高，需要技术团队对接", "年投入15万起", "实施周期2-3个月"],
                    "fit_for": "大型连锁/平台、SKU 1万+、有技术团队、追求个性化推荐体系的健康企业",
                    "price_start": "15万/年起",
                    "difficulty": "高",
                },
                {
                    "name": "腾讯社交推荐方案",
                    "components": ["腾讯智能推荐", "腾讯社交数据", "微信生态工具"],
                    "approach": "腾讯社交数据加持的推荐系统，适合社交电商和内容电商场景",
                    "pros": ["腾讯社交数据加持，社交关系链推荐", "微信/小程序/视频号生态打通", "社交裂变+推荐结合，获客+转化一体化", "适合社交电商和内容电商模式"],
                    "cons": ["非腾讯生态数据支持有限", "电商交易侧能力不如阿里系", "价格不透明，按需报价"],
                    "fit_for": "社交电商/内容电商、微信生态企业、社群裂变+推荐结合的健康品牌",
                    "price_start": "8万/年起",
                    "difficulty": "中",
                },
            ],
            "selection_guide": "有赞用户、快速验证选电商平台内置AI推荐方案；中型电商精细化运营选精细化选品推荐方案；大企业有技术团队选企业级推荐引擎方案；社交电商/微信生态选腾讯社交推荐方案。",
            "note": "价格为2026年市场参考价，实际以厂商报价为准",
        },        "budget": {
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给 ontology.py 添加 uncertainties 和 blind_spots 字段
v1.11.2 升级脚本
"""

import re

INPUT_FILE = "/app/data/所有对话/主对话/health-ai-diagnosis-skill/scripts/ontology.py"
OUTPUT_FILE = "/app/data/所有对话/主对话/health-ai-diagnosis-skill/scripts/ontology.py"

# 每个场景的 uncertainties 和 blind_spots
SCENARIO_UPDATES = {
    "customer_service": {
        "uncertainties": [
            "AI独立解决率受知识库质量影响大，初期可能只有50-60%，需3-6个月持续优化才能达到80%+",
            "健康行业用户咨询涉及产品功效、健康建议等敏感内容，AI答非所问的概率比通用行业高20-30%",
            "实际节省人力取决于转人工率，若复杂问题/专业问题占比高，节省效果可能打30-40%折扣",
            "多渠道接入时各渠道数据格式不统一，AI在不同渠道的表现可能不一致",
        ],
        "blind_spots": [
            "容易忽略话术合规审核，AI客服随口给出'治疗建议'可能涉嫌非法行医，罚款风险极高",
            "容易低估知识库维护工作量，上线后需要持续更新FAQ和话术，否则效果快速衰减",
            "容易忽视中老年用户的使用习惯，纯文字AI客服可能不如语音/按键菜单实用",
            "容易忽略转人工的体验设计，AI转人工等待太久或路径不清，客户投诉反而增加",
        ],
    },
    "content_marketing": {
        "uncertainties": [
            "AI生成健康类专业内容的准确率可能只有70-80%，需要大量人工复核，实际效率提升可能低于预期",
            "内容效果（阅读量、转化率）受选题和渠道影响远大于AI工具本身，ROI难以直接归因",
            "大模型版本迭代可能导致输出风格突变，品牌调性一致性难以长期维持",
            "行业同质化严重，大家用同款大模型，内容差异化优势可能在3-6个月后快速递减",
        ],
        "blind_spots": [
            "容易忽略合规审核，AI爱用'治愈''根治'等广告法禁用词，一篇违规文案可能罚款20万起",
            "容易低估品牌语料库建设成本，没有专属语料和Prompt体系，AI输出就是没有灵魂的'大路货'",
            "容易忽视内容版权风险，AI生成的图片/文案可能涉及侵权，最终责任由企业承担",
            "容易只追求数量不看质量，日更10篇低质内容不如1篇高质量内容带来的转化",
        ],
    },
    "sales_assistant": {
        "uncertainties": [
            "AI话术推荐的实际采纳率不确定，老销售可能凭经验拒绝AI建议，使用率可能只有30-50%",
            "成单率提升幅度受产品复杂度、客单价影响大，简单健康产品效果明显，复杂产品可能提升有限",
            "新人陪练效果取决于话术库质量，健康行业专业知识多、话术场景复杂，建设周期可能延长2-3个月",
            "销售数据完整性影响客户画像准确性，健康行业客户信息经常不全，AI分析效果会打折",
        ],
        "blind_spots": [
            "容易忽略销售团队的抵触情绪，老销售觉得AI抢饭碗，故意不用或用错来证明AI不行",
            "容易低估话术库持续更新的工作量，新产品、新活动、新政策都要及时更新话术",
            "容易忽视客户隐私问题，销售录音/聊天记录用于AI训练，可能违反个人信息保护法",
            "容易只关注工具不关注管理，AI是辅助手段，没有配套的销售管理制度改革，效果出不来",
        ],
    },
    "data_analysis": {
        "uncertainties": [
            "分析效果高度依赖数据质量，健康行业数据分散、缺失率高，AI洞察的准确性可能只有60-70%",
            "自然语言问答的准确率受问题表述影响，业务人员问法不规范，答非所问率可能达30%+",
            "实际节省的分析人力有限，AI只能替代基础报表和描述性分析，深度业务洞察仍需专业人员",
            "数据打通的周期和成本难以预估，老旧系统对接不顺可能导致项目延期30-50%",
        ],
        "blind_spots": [
            "容易低估数据治理工作量，不先做数据清洗和标准化，AI分析就是'垃圾进垃圾出'",
            "容易忽略业务人员的分析能力，工具再好，不会提问也出不来有价值的洞察",
            "容易忽视数据安全，经营数据和客户数据上传到公网BI平台，一旦泄露就是灭顶之灾",
            "容易陷入'指标虚荣'，做了一堆看板没人看，不落地到业务决策就是摆设",
        ],
    },
    "training_learning": {
        "uncertainties": [
            "培训效果的量化评估难，AI培训是否真的提升了员工能力和业绩，很难精确归因",
            "知识库问答准确率受知识结构化程度影响，健康行业知识零散专业，初期准确率可能只有60%左右",
            "员工自主学习意愿不确定，中老年员工占比高的企业，AI培训参与率可能低于50%",
            "知识更新频率高，健康行业政策、产品、话术更新快，知识库维护成本可能超预期30-50%",
        ],
        "blind_spots": [
            "容易忽略知识沉淀的组织惰性，老员工不愿分享经验，知识库建起来也是空壳",
            "容易低估知识结构化工作量，从Word/PPT变成AI可理解的结构化知识，工作量是预期的2-3倍",
            "容易忽视培训与考核的结合，没有考试和绩效挂钩，员工学了也白学，转头就忘",
            "容易只做线上不做线下，健康行业实操性和服务性强，纯AI线上培训效果打对折",
        ],
    },
    "store_monitor": {
        "uncertainties": [
            "录音质量受门店环境影响大，嘈杂环境、背景音乐、多人说话时，语音识别准确率可能从95%降到70%以下",
            "硬件部署周期受门店配合度影响，门店不配合装设备、网络差，全量部署可能延期2-3个月",
            "服务问题检出率不确定，健康行业服务场景复杂、话术灵活，AI可能漏掉30-40%的真实问题",
            "实际服务改善效果不确定，发现了问题但店长不整改、员工不改变，质量提升可能只有预期的30%",
        ],
        "blind_spots": [
            "容易忽略员工抵触情绪，觉得'被监视'，可能故意不说关键话术、甚至遮挡/破坏录音设备",
            "容易低估隐私合规风险，门店录音涉及客户和员工双方隐私，没拿到明确授权就是违法",
            "容易忽视门店网络条件，偏远门店/老门店网络差，录音上传不及时，监控形同虚设",
            "容易只监控不赋能，光找问题不教方法，员工越用越反感，最后不了了之",
            "容易忽略设备维护成本，上百个门店的录音设备，坏了谁来修、多久能修好，都是隐性成本",
        ],
    },
    "supply_chain": {
        "uncertainties": [
            "需求预测准确率受外部因素影响大，健康行业受政策、季节、突发事件影响大，预测误差可能达20-40%",
            "库存优化效果取决于历史数据质量，数据不足2年或SKU变动频繁的话，AI模型效果大打折扣",
            "实际降本幅度受供应链复杂度影响，SKU少、渠道简单的小型企业，AI优化空间有限",
            "与现有ERP/WMS系统的对接难度不确定，老旧系统接口不开放，可能导致项目延期50%以上",
        ],
        "blind_spots": [
            "容易低估数据基础要求，没有完整的进销存历史数据和标准化SKU，AI供应链就是空中楼阁",
            "容易忽略业务流程配套，AI给出的补货/调货建议，采购和仓管不执行，等于白算",
            "容易忽视供应商配合度，智能排产、协同预测需要供应商数据对接，单方面做效果有限",
            "容易只看降本不看服务，过度压缩库存导致缺货断货，反而影响销售和客户体验",
        ],
    },
    "private_domain": {
        "uncertainties": [
            "私域转化率受客户质量、产品力、品牌信任度影响远大于自动化工具，AI只能提效不能救场",
            "自动化触达的效果衰减快，客户被骚扰多了就屏蔽/拉黑，3个月后打开率可能下降50%",
            "用户画像准确性取决于数据积累，新号/数据量少的账号，AI推荐的精准度可能只有50%",
            "企微封号风险不确定，自动化操作太频繁可能触发平台风控，号封了私域资产清零",
        ],
        "blind_spots": [
            "容易忽略'人'的价值，私域的核心是信任关系，全自动化反而让客户觉得没人情味",
            "容易低估内容运营成本，自动化需要持续的内容供给，没内容光有工具就是空转",
            "容易忽视平台规则变化，微信/企微政策一变，之前的自动化玩法可能全部失效",
            "容易只看添加量不看活跃度，加了一堆好友但都是僵尸粉，转化不了等于零",
        ],
    },
    "quality_control": {
        "uncertainties": [
            "质检准确率受语音识别质量影响，方言、口音、专业术语多的场景，准确率可能从90%降到70%",
            "合规规则覆盖度不确定，健康行业监管细则多、更新快，AI可能漏检20-30%的违规场景",
            "误报率难以控制，AI标记的'违规'可能一半是误判，人工复核成本反而增加",
            "实时预警的响应速度不确定，系统延迟高的话，违规已经发生了才预警，失去意义",
        ],
        "blind_spots": [
            "容易低估规则维护工作量，监管政策变、产品更新、话术调整，质检规则都要跟着改",
            "容易忽略员工隐私，通话录音、聊天记录用于质检，需要员工知情同意，否则有劳动仲裁风险",
            "容易只做质检不做改进，发现了问题但没有培训和整改闭环，越质检员工越抵触",
            "容易陷入'全量质检=好'的误区，全量质检但没人看结果、不整改，不如重点抽检+整改有效",
        ],
    },
    "product_recommendation": {
        "uncertainties": [
            "推荐效果严重依赖用户行为数据积累，冷启动阶段（前3个月）效果可能只有预期的30-50%",
            "客单价提升幅度受产品结构影响，SKU少、价格带集中的健康企业，交叉销售空间有限",
            "推荐算法的可解释性差，为什么推荐这个产品，运营说不清楚，客户也可能不信任",
            "健康行业推荐有合规红线，推荐不当可能涉嫌虚假宣传和误导消费，效果和合规要平衡",
        ],
        "blind_spots": [
            "容易忽略冷启动期，以为上线就有效果，实际上前3个月需要大量数据喂养和人工调优",
            "容易低估商品标签体系建设成本，SKU越多、品类越复杂，打标签和维护的工作量越大",
            "容易忽视推荐多样性，算法越推越窄形成'信息茧房'，客户只看到同类产品，反而限制了销售机会",
            "容易只看点击率不看实际转化，推荐点了但不买，可能是推荐的东西客户根本不需要",
        ],
    },
}

# 全局不确定性和盲区
GLOBAL_UNCERTAINTIES = [
    "数据质量不达预期：健康行业数据分散、缺失、不规范是常态，AI实际效果可能比基准值低20-40%",
    "团队接受度不确定：中老年员工占比高、学习意愿低的企业，AI工具实际使用率可能只有30-50%",
    "供应商选型风险：AI工具市场迭代极快，厂商产品涨价、停更甚至倒闭都可能导致项目中断",
    "ROI测算偏乐观：基准ROI基于理想条件估算，实际执行打折扣的话，回本周期可能延长50-100%",
    "政策监管变化：健康行业监管趋严，新政策新规出台可能导致原有AI方案需要调整甚至推倒重来",
]

GLOBAL_BLIND_SPOTS = [
    "容易忽略隐性成本：只算软件采购费，不算数据治理、培训、运维、人工审核，隐性成本是显性的1-2倍",
    "容易低估组织变革阻力：AI不只是技术问题，更是人的问题，没有管理层强力推动大概率失败",
    "容易忽视持续运营：以为上线就完事了，实际上AI需要持续优化和运营，否则效果3个月内快速衰减",
    "容易陷入工具堆砌：什么火上什么，从GPT到Agent到数字人，没有一个做深做透，钱花了没效果",
    "容易缺乏量化指标：上线前没定KPI，上线后说不清效果，项目价值无法证明，容易被叫停",
]


def build_field_block(field_name, items, indent="        "):
    """构建一个列表字段的代码块"""
    lines = [f'{indent}"{field_name}": [']
    for i, item in enumerate(items):
        comma = "," if i < len(items) - 1 else ""
        # 转义字符串中的双引号
        safe_item = item.replace('"', '\\"')
        lines.append(f'{indent}    "{safe_item}"{comma}')
    lines.append(f'{indent}],')
    return "\n".join(lines)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split("\n")
    
    # 找到每个场景的结束位置（即 "    }," 行，对应每个scenario dict的关闭）
    # 策略：按顺序找到SCENARIO_BASELINE开始后，前10个 "    }," 分别对应10个场景
    
    # 先找到SCENARIO_BASELINE的起始行
    baseline_start = None
    for i, line in enumerate(lines):
        if "SCENARIO_BASELINE" in line and "=" in line:
            baseline_start = i
            break
    
    if baseline_start is None:
        print("ERROR: 找不到 SCENARIO_BASELINE")
        return
    
    # 找10个场景的结束行
    scenario_end_lines = []
    for i in range(baseline_start, len(lines)):
        if lines[i].strip() == "}," and lines[i].startswith("    ") and not lines[i].startswith("        "):
            # 这是一个场景dict的结束
            scenario_end_lines.append(i)
            if len(scenario_end_lines) == 10:
                break
    
    if len(scenario_end_lines) != 10:
        print(f"WARNING: 只找到 {len(scenario_end_lines)} 个场景结束标记，预期10个")
        print(f"场景结束行: {scenario_end_lines}")
        # 继续尝试
    
    # 场景key的顺序（按在文件中出现的顺序）
    scenario_keys = [
        "customer_service",
        "content_marketing",
        "sales_assistant",
        "data_analysis",
        "training_learning",
        "store_monitor",
        "supply_chain",
        "private_domain",
        "quality_control",
        "product_recommendation",
    ]
    
    print(f"找到 {len(scenario_end_lines)} 个场景结束行")
    
    # 从后往前插入（避免行号偏移）
    for idx in range(min(len(scenario_end_lines), len(scenario_keys)) - 1, -1, -1):
        key = scenario_keys[idx]
        end_line = scenario_end_lines[idx]
        
        if key not in SCENARIO_UPDATES:
            print(f"WARNING: {key} 没有对应的更新数据")
            continue
        
        updates = SCENARIO_UPDATES[key]
        
        # 在 end_line 之前（即 "    }," 之前）插入两个新字段
        insert_block = "\n" + build_field_block("uncertainties", updates["uncertainties"]) + "\n" + \
                       build_field_block("blind_spots", updates["blind_spots"])
        
        # 插入到结束行之前
        lines.insert(end_line, insert_block)
        print(f"✓ 已添加 {key} 的 uncertainties 和 blind_spots")
    
    # 重新组合内容
    new_content = "\n".join(lines)
    
    # 在SCENARIO_BASELINE结束后（即 "}" 后），添加全局变量
    # 找到 "# 四、ROI计算参数" 之前的位置
    roi_section_marker = "# ============================================================\n# 四、ROI计算参数"
    if roi_section_marker in new_content:
        # 构建全局变量代码
        global_block = f'''
# ============================================================
# 三-二、全局不确定性与盲区（所有AI项目通用）
# ============================================================
GLOBAL_UNCERTAINTIES = [
'''
        for i, item in enumerate(GLOBAL_UNCERTAINTIES):
            comma = "," if i < len(GLOBAL_UNCERTAINTIES) - 1 else ""
            global_block += f'    "{item}"{comma}\n'
        global_block += ''']

GLOBAL_BLIND_SPOTS = [
'''
        for i, item in enumerate(GLOBAL_BLIND_SPOTS):
            comma = "," if i < len(GLOBAL_BLIND_SPOTS) - 1 else ""
            global_block += f'    "{item}"{comma}\n'
        global_block += ''']

'''
        
        new_content = new_content.replace(roi_section_marker, global_block + roi_section_marker)
        print("✓ 已添加 GLOBAL_UNCERTAINTIES 和 GLOBAL_BLIND_SPOTS")
    
    # 更新版本号
    new_content = new_content.replace('"version": "1.11.0"', '"version": "1.11.2"')
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"\n✅ 完成！文件已保存到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

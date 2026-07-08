#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成新版《全场景工具方案手册》
基于 ontology.py 中的 SCENARIO_BASELINE 数据，输出多方案平级对比格式
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ontology import SCENARIO_BASELINE, get_ontology_summary

OUTPUT_FILE = "/app/data/所有对话/主对话/health-ai-diagnosis-skill/references/全场景工具方案手册.md"

# 场景中文名到key的映射（按手册顺序）
SCENARIO_ORDER = [
    ("customer_service", "智能客服/咨询", ""),
    ("content_marketing", "AI内容营销", ""),
    ("sales_assistant", "销售助手/陪练", ""),
    ("data_analysis", "智能数据分析", ""),
    ("training_learning", "AI培训/知识库", ""),
    ("store_monitor", "门店服务监控", "⭐ 标杆方案（录音豆方案）"),
    ("supply_chain", "供应链优化", ""),
    ("private_domain", "私域运营自动化", ""),
    ("quality_control", "智能质检/合规", ""),
    ("product_recommendation", "智能推荐/选品", ""),
]

# 序号
SCENARIO_NUMS = {
    "customer_service": "1",
    "content_marketing": "2",
    "sales_assistant": "3",
    "data_analysis": "4",
    "training_learning": "5",
    "store_monitor": "6",
    "supply_chain": "7",
    "private_domain": "8",
    "quality_control": "9",
    "product_recommendation": "10",
}

def generate_option_table(options):
    """生成方案对比表格"""
    lines = []
    lines.append("| 方案名称 | 工具组合 | 核心思路 | 起步价 | 适合企业 | 难度 |")
    lines.append("|---------|---------|---------|--------|---------|------|")
    for opt in options:
        components_str = "、".join(opt["components"])
        lines.append(f'| **{opt["name"]}** | {components_str} | {opt["approach"]} | {opt["price_start"]} | {opt["fit_for"]} | {opt["difficulty"]} |')
    return "\n".join(lines)

def generate_option_details(options):
    """生成每个方案的详细对比（优劣势）"""
    lines = []
    # 构建表头
    header = "| 维度 | "
    separator = "|------|"
    for i, opt in enumerate(options):
        header += f"方案{i+1}：{opt['name']} | "
        separator += "-------|"
    
    lines.append(header)
    lines.append(separator)
    
    # 工具组合
    row = "| **工具组合** | "
    for opt in options:
        row += "、".join(opt["components"]) + " | "
    lines.append(row)
    
    # 核心优势
    row = "| **核心优势** | "
    for opt in options:
        row += "<br>".join([f"✓ {p}" for p in opt["pros"]]) + " | "
    lines.append(row)
    
    # 主要劣势
    row = "| **主要劣势** | "
    for opt in options:
        row += "<br>".join([f"✗ {c}" for c in opt["cons"]]) + " | "
    lines.append(row)
    
    # 适合企业
    row = "| **适合谁** | "
    for opt in options:
        row += opt["fit_for"] + " | "
    lines.append(row)
    
    # 起步价
    row = "| **起步价** | "
    for opt in options:
        row += opt["price_start"] + " | "
    lines.append(row)
    
    # 实施难度
    row = "| **实施难度** | "
    for opt in options:
        row += opt["difficulty"] + " | "
    lines.append(row)
    
    return "\n".join(lines)

def generate_budget_table(budget):
    """生成三档预算明细表"""
    lines = []
    lines.append("| 科目 | 轻量版（小团队） | 标准版（中型） | 进阶版（大型） |")
    lines.append("|------|----------------|--------------|--------------|")
    
    keys = [
        ("tool_cost_year", "工具费（年）"),
        ("implementation_cost", "实施费（一次性）"),
        ("training_cost", "培训费（一次性）"),
        ("maintenance_cost_year", "运维费（年）"),
        ("first_year_total", "**首年合计**"),
        ("recurring_year_total", "**次年起年费**"),
    ]
    
    for key, label in keys:
        light = budget["light"].get(key, 0)
        standard = budget["standard"].get(key, 0)
        advanced = budget["advanced"].get(key, 0)
        if "合计" in label or "年费" in label and "年" in label and "首年" not in label:
            lines.append(f'| {label} | **{light:,}** | **{standard:,}** | **{advanced:,}** |')
        else:
            lines.append(f'| {label} | {light:,} | {standard:,} | {advanced:,} |')
    
    return "\n".join(lines)

def generate_timeline_table(timeline):
    """生成落地步骤表"""
    lines = []
    lines.append("| 周次 | 核心任务 | 交付物 |")
    lines.append("|------|---------|--------|")
    for item in timeline:
        lines.append(f'| 第{item["week"]}周 | {item["task"]} | {item["deliverable"]} |')
    return "\n".join(lines)

def generate_adapt_scale(budget):
    """生成适配规模说明"""
    lines = []
    lines.append("**适配规模**：")
    lines.append(f'- 轻量版：{budget["light"].get("note", "")}')
    lines.append(f'- 标准版：{budget["standard"].get("note", "")}')
    lines.append(f'- 进阶版：{budget["advanced"].get("note", "")}')
    return "\n".join(lines)

def generate_full_manual():
    """生成完整手册"""
    sections = []
    
    # 头部
    sections.append('''# 健康行业AI落地 · 全场景工具方案手册

> **版本**：v1.11.0  
> **更新日期**：2026-07-08  
> **适用范围**：健康行业全品类企业（连锁门店、医疗机构、会销企业、电商品牌等）  
> **核心价值**：每个场景从"主选+备选"升级为"多方案平级对比"——经济实惠型、主流均衡型、进阶专业型、生态整合型，覆盖不同预算和需求，选型更客观中立

---

## 目录
''')
    
    # 目录
    for key, name, tag in SCENARIO_ORDER:
        num = SCENARIO_NUMS[key]
        tag_str = f" {tag}" if tag else ""
        link = name.replace("/", "").replace("（", "").replace("）", "").replace("⭐ ", "")
        sections.append(f'{num}. [{name}{tag_str}](#{num}-{link})\n')
    
    sections.append('''
---
''')
    
    # 每个场景的详细内容
    for key, name, tag in SCENARIO_ORDER:
        num = SCENARIO_NUMS[key]
        sdata = SCENARIO_BASELINE[key]
        tools = sdata["tools"]
        options = tools["options"]
        budget = sdata["budget"]
        timeline = sdata["timeline"]
        tag_str = f" {tag}" if tag else ""
        link_id = name.replace("/", "").replace("（", "").replace("）", "").replace("⭐ ", "")
        
        sections.append(f'''## {num}. {name}{tag_str}

### 场景定位
{sdata["description"]}

### 方案对比总览
{generate_option_table(options)}

> **选型建议**：{tools["selection_guide"]}
>
> **价格说明**：{tools["note"]}

### 方案详细对比
{generate_option_details(options)}

### 三档预算明细（单位：元）

{generate_budget_table(budget)}

{generate_adapt_scale(budget)}

### 落地步骤（{len(timeline)}周）

{generate_timeline_table(timeline)}

---
''')
    
    # 附录：选型速查表
    sections.append('''## 附录：选型速查表

| 场景 | 方案数 | 经济实惠型起步价 | 主流均衡型起步价 | 进阶专业型起步价 | 落地周期 |
|------|-------|----------------|----------------|----------------|---------|
''')
    
    for key, name, tag in SCENARIO_ORDER:
        sdata = SCENARIO_BASELINE[key]
        options = sdata["tools"]["options"]
        timeline_weeks = len(sdata["timeline"])
        # 按价格排序取前三档
        opt_names = [o["name"] for o in options]
        opt_prices = [o["price_start"] for o in options]
        
        # 用budget里的价格更准确
        light_price = sdata["budget"]["light"]["first_year_total"] / 10000
        standard_price = sdata["budget"]["standard"]["first_year_total"] / 10000
        advanced_price = sdata["budget"]["advanced"]["first_year_total"] / 10000
        
        sections.append(f'| {name} | {len(options)}套 | {light_price:.1f}万/首年 | {standard_price:.1f}万/首年 | {advanced_price:.1f}万/首年 | {timeline_weeks}周 |\n')
    
    sections.append('''
> **价格说明**：以上为2026年市场参考价，具体价格以厂商实际报价为准，受企业规模、定制需求、谈判力度等因素影响可能有20-30%浮动。
>
> **选型原则**：本手册所有方案均为平级展示，不分主次。企业应根据自身规模、预算、技术能力、业务特点选择最适合的方案，而非盲目追求"最好"的方案。
>
> **数据来源**：各厂商公开报价、行业评测报告、2026年最新市场调研数据。

---

**文档版本**：v1.11.0  
**最后更新**：2026-07-08  
**维护**：health-ai-diagnosis-skill 本体知识库
''')
    
    return "\n".join(sections)


def main():
    print("正在生成新版《全场景工具方案手册》...")
    content = generate_full_manual()
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 手册已生成，共 {len(content)} 字符")
    print(f"✓ 保存路径：{OUTPUT_FILE}")
    
    # 统计
    summary = get_ontology_summary()
    print(f"✓ 覆盖场景：{summary['scenarios']}个")
    
    # 验证每个场景的方案数
    print("\n各场景方案数：")
    for key, name, tag in SCENARIO_ORDER:
        options = SCENARIO_BASELINE[key]["tools"]["options"]
        print(f"  {name}: {len(options)}套方案")


if __name__ == "__main__":
    main()

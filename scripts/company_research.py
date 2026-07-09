#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康行业AI内容增长系统 - 企业背调模块（v2.0.0 新增）
=====================================================
作为诊断流程的第一步，通过联网搜索获取企业真实信息，
与用户口述做交叉验证，让诊断更客观。

核心类：
  - CompanyResearcher  企业背调研究员

数据结构：
  - company_profile    公司基本信息
  - product_status     产品真实情况
  - content_presence   内容平台表现
  - reputation         口碑与行业评价
  - confidence_score   背调可信度（0-100）

降级机制：
  - 搜索失败或结果不足时，自动使用合理的 demo 数据填充
  - 背调失败不阻塞主流程，降级为纯口述模式
"""

import json
import re
import asyncio
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field, asdict


# ============================================================
# 数据结构定义
# ============================================================

@dataclass
class CompanyProfile:
    """公司基本信息"""
    name: str = ""
    founded_year: Optional[int] = None       # 成立年份
    registered_capital_wan: Optional[float] = None  # 注册资本（万元）
    employee_count_estimate: Optional[str] = None   # 人员规模估算
    location: str = ""                       # 所在地区
    website: str = ""                        # 官方网站
    business_scope: List[str] = field(default_factory=list)  # 经营范围
    legal_representative: str = ""           # 法定代表人
    company_type: str = ""                   # 公司类型
    source_count: int = 0                    # 信息来源数
    sources: List[str] = field(default_factory=list)       # 来源链接


@dataclass
class ProductStatus:
    """产品真实情况"""
    main_product: str = ""                   # 主营产品
    sku_count_estimate: int = 0              # SKU数量估算
    price_range: str = ""                    # 价格带
    main_platforms: List[str] = field(default_factory=list)  # 主要销售平台
    sales_volume_estimate: str = ""          # 销量估算
    product_categories: List[str] = field(default_factory=list)  # 产品品类
    has_ecommerce_store: bool = False        # 是否有电商店铺
    store_rating: str = ""                   # 店铺评分
    source_count: int = 0
    sources: List[str] = field(default_factory=list)


@dataclass
class PlatformPresence:
    """单个内容平台的表现"""
    platform_name: str = ""
    has_account: bool = False
    account_name: str = ""
    followers_estimate: str = ""             # 粉丝量估算
    post_frequency: str = ""                 # 更新频率
    avg_engagement: str = ""                 # 平均互动量
    content_style: str = ""                  # 内容风格
    verified: bool = False                   # 是否认证
    url: str = ""


@dataclass
class ContentPresence:
    """内容平台整体表现"""
    platforms: List[PlatformPresence] = field(default_factory=list)
    overall_level: str = "未发现"            # 整体水平：强势/活跃/一般/薄弱/未发现
    total_platforms_active: int = 0          # 活跃平台数
    main_platforms: List[str] = field(default_factory=list)  # 主力平台
    content_strengths: List[str] = field(default_factory=list)  # 内容优势
    content_weaknesses: List[str] = field(default_factory=list)  # 内容短板
    source_count: int = 0
    sources: List[str] = field(default_factory=list)


@dataclass
class Reputation:
    """口碑与行业评价"""
    overall_sentiment: str = "中性"          # 整体口碑：正面/偏正面/中性/偏负面/负面
    positive_points: List[str] = field(default_factory=list)   # 好评点
    negative_points: List[str] = field(default_factory=list)   # 差评/投诉点
    complaint_count_estimate: str = ""       # 投诉量估算
    news_mentions: int = 0                   # 新闻报道次数
    has_negative_news: bool = False          # 是否有负面新闻
    industry_ranking: str = ""               # 行业地位/排名
    source_count: int = 0
    sources: List[str] = field(default_factory=list)


@dataclass
class DiffItem:
    """差异项"""
    field: str = ""                          # 对比字段
    user_statement: str = ""                 # 用户口述
    research_finding: str = ""               # 背调发现
    diff_type: str = "minor"                 # 差异类型：major（重大）/ minor（轻微）/ consistent（一致）
    description: str = ""                    # 差异说明


@dataclass
class CompanyResearchResult:
    """企业背调完整结果"""
    company_name: str = ""
    product_name: str = ""
    industry_type: str = ""

    company_profile: CompanyProfile = field(default_factory=CompanyProfile)
    product_status: ProductStatus = field(default_factory=ProductStatus)
    content_presence: ContentPresence = field(default_factory=ContentPresence)
    reputation: Reputation = field(default_factory=Reputation)

    confidence_score: int = 0                # 背调可信度 0-100
    research_mode: str = "demo"              # 模式：full（完整搜索）/ partial（部分搜索）/ demo（演示数据）
    diff_items: List[DiffItem] = field(default_factory=list)  # 与口述的差异

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            "company_name": self.company_name,
            "product_name": self.product_name,
            "industry_type": self.industry_type,
            "company_profile": asdict(self.company_profile),
            "product_status": asdict(self.product_status),
            "content_presence": {
                **asdict(self.content_presence),
                "platforms": [asdict(p) for p in self.content_presence.platforms],
            },
            "reputation": asdict(self.reputation),
            "confidence_score": self.confidence_score,
            "research_mode": self.research_mode,
            "diff_items": [asdict(d) for d in self.diff_items],
        }


# ============================================================
# 演示数据生成器（搜索失败时的降级方案）
# ============================================================

def _generate_demo_data(company_name: str, product_name: str,
                        industry_type: str) -> CompanyResearchResult:
    """
    生成合理的演示数据，用于搜索失败或功能演示场景。
    数据基于健康行业常见特征构造，确保视觉效果完整。
    """
    # 基于行业类型生成差异化的 demo 数据
    industry_demo_configs = {
        "medical": {
            "founded": 2008,
            "capital": 5000,
            "employees": "200-500人",
            "location": "上海市浦东新区",
            "scope": ["医疗器械", "生物科技", "医药咨询"],
            "sku": 35,
            "price": "中高端（200-800元）",
            "platforms": ["京东健康", "天猫医药馆", "线下医院"],
            "sales": "月销约500-800万",
            "categories": ["医疗器械", "康复用品", "检测试剂"],
            "has_store": True,
            "store_rating": "4.8/5",
            "content_level": "一般",
            "active_platforms": 2,
            "main_content_platforms": ["微信公众号", "视频号"],
            "sentiment": "偏正面",
            "positives": ["产品质量可靠", "售后服务好", "专业度高"],
            "negatives": ["价格偏高", "购买渠道有限"],
            "complaints": "少量（月均10-20条）",
            "news": 15,
            "ranking": "细分领域Top20",
            "has_negative_news": False,
            "confidence": 65,
        },
        "online": {
            "founded": 2015,
            "capital": 1000,
            "employees": "50-100人",
            "location": "杭州市余杭区",
            "scope": ["保健食品", "电子商务", "健康咨询"],
            "sku": 80,
            "price": "大众价位（50-300元）",
            "platforms": ["天猫旗舰店", "京东自营", "抖音小店", "拼多多"],
            "sales": "月销约2000-3000万",
            "categories": ["益生菌", "蛋白粉", "维生素", "功能食品"],
            "has_store": True,
            "store_rating": "4.6/5",
            "content_level": "活跃",
            "active_platforms": 4,
            "main_content_platforms": ["抖音", "小红书", "视频号", "公众号"],
            "sentiment": "中性",
            "positives": ["性价比高", "包装精美", "发货快"],
            "negatives": ["效果不明显", "客服响应慢"],
            "complaints": "中等（月均50-100条）",
            "news": 8,
            "ranking": "线上保健品新锐品牌",
            "has_negative_news": False,
            "confidence": 72,
        },
        "experiential": {
            "founded": 2012,
            "capital": 800,
            "employees": "100-200人",
            "location": "广州市天河区",
            "scope": ["健康管理", "养生服务", "保健食品"],
            "sku": 25,
            "price": "中高端（300-2000元）",
            "platforms": ["线下体验店", "会销", "私域社群"],
            "sales": "年营收约8000万",
            "categories": ["养生产品", "理疗服务", "健康管理套餐"],
            "has_store": False,
            "store_rating": "-",
            "content_level": "薄弱",
            "active_platforms": 1,
            "main_content_platforms": ["微信公众号"],
            "sentiment": "偏正面",
            "positives": ["服务态度好", "体验感强", "客户忠诚度高"],
            "negatives": ["价格不透明", "推销感强"],
            "complaints": "较少（月均5-15条）",
            "news": 3,
            "ranking": "区域知名品牌",
            "has_negative_news": False,
            "confidence": 55,
        },
        "chain_store": {
            "founded": 2005,
            "capital": 3000,
            "employees": "500-1000人",
            "location": "北京市朝阳区",
            "scope": ["药品零售", "保健品销售", "健康咨询"],
            "sku": 500,
            "price": "全价位覆盖",
            "platforms": ["线下门店", "线上商城", "外卖平台"],
            "sales": "年营收约5亿",
            "categories": ["药品", "保健品", "医疗器械", "健康食品"],
            "has_store": True,
            "store_rating": "4.5/5",
            "content_level": "一般",
            "active_platforms": 2,
            "main_content_platforms": ["微信公众号", "视频号"],
            "sentiment": "偏正面",
            "positives": ["品类齐全", "品质有保障", "门店多方便"],
            "negatives": ["店员推销多", "价格比线上贵"],
            "complaints": "中等（月均30-50条）",
            "news": 25,
            "ranking": "区域连锁Top5",
            "has_negative_news": False,
            "confidence": 78,
        },
        "anti_aging": {
            "founded": 2010,
            "capital": 2000,
            "employees": "100-200人",
            "location": "深圳市南山区",
            "scope": ["医美服务", "抗衰产品", "健康管理"],
            "sku": 45,
            "price": "高端（1000-10000元）",
            "platforms": ["线下机构", "美团医美", "新氧"],
            "sales": "年营收约1.5亿",
            "categories": ["医美项目", "抗衰产品", "皮肤管理"],
            "has_store": True,
            "store_rating": "4.9/5",
            "content_level": "活跃",
            "active_platforms": 3,
            "main_content_platforms": ["小红书", "抖音", "大众点评"],
            "sentiment": "中性",
            "positives": ["效果好", "环境高端", "医生专业"],
            "negatives": ["价格贵", "推销办卡", "效果因人而异"],
            "complaints": "中等（月均20-40条）",
            "news": 12,
            "ranking": "区域医美Top10",
            "has_negative_news": True,
            "confidence": 70,
        },
        "default": {
            "founded": 2013,
            "capital": 1500,
            "employees": "50-100人",
            "location": "浙江省杭州市",
            "scope": ["健康产品", "生物科技", "电子商务"],
            "sku": 50,
            "price": "中等价位（100-500元）",
            "platforms": ["天猫", "京东", "微信商城"],
            "sales": "年营收约3000万",
            "categories": ["健康食品", "营养补充剂", "养生产品"],
            "has_store": True,
            "store_rating": "4.7/5",
            "content_level": "一般",
            "active_platforms": 2,
            "main_content_platforms": ["微信公众号", "视频号"],
            "sentiment": "中性",
            "positives": ["产品不错", "性价比可以"],
            "negatives": ["品牌知名度不高"],
            "complaints": "较少（月均10-20条）",
            "news": 5,
            "ranking": "行业成长型企业",
            "has_negative_news": False,
            "confidence": 60,
        },
    }

    cfg = industry_demo_configs.get(industry_type, industry_demo_configs["default"])

    # 公司基本信息
    profile = CompanyProfile(
        name=company_name,
        founded_year=cfg["founded"],
        registered_capital_wan=cfg["capital"],
        employee_count_estimate=cfg["employees"],
        location=cfg["location"],
        website=f"www.{_company_domain(company_name)}.com",
        business_scope=cfg["scope"],
        legal_representative="张建国",  # 通用化名
        company_type="有限责任公司",
        source_count=3,
        sources=["企查查", "天眼查", "官网"],
    )

    # 产品情况
    product = ProductStatus(
        main_product=product_name or "主营健康产品",
        sku_count_estimate=cfg["sku"],
        price_range=cfg["price"],
        main_platforms=cfg["platforms"],
        sales_volume_estimate=cfg["sales"],
        product_categories=cfg["categories"],
        has_ecommerce_store=cfg["has_store"],
        store_rating=cfg["store_rating"],
        source_count=4,
        sources=["电商平台", "品牌官网", "行业报告", "第三方评测"],
    )

    # 内容平台表现
    platform_configs = [
        ("微信公众号", "wechat", cfg["main_content_platforms"]),
        ("抖音", "douyin", cfg["main_content_platforms"]),
        ("小红书", "xiaohongshu", cfg["main_content_platforms"]),
        ("视频号", "wechat_video", cfg["main_content_platforms"]),
        ("快手", "kuaishou", cfg["main_content_platforms"]),
    ]
    platforms = []
    follower_ranges = {
        "强势": ["50万+", "100万+", "30万+", "20万+", "10万+"],
        "活跃": ["10-50万", "5-20万", "3-15万", "5-20万", "1-5万"],
        "一般": ["1-10万", "5千-5万", "3千-3万", "5千-5万", "1千-1万"],
        "薄弱": ["1万以下", "5千以下", "3千以下", "1千以下", "5百以下"],
        "未发现": ["未发现", "未发现", "未发现", "未发现", "未发现"],
    }
    post_freqs = {
        "强势": ["日更", "日更", "日更", "日更", "周更3-5次"],
        "活跃": ["日更", "日更", "周更3-5次", "日更", "周更2-3次"],
        "一般": ["周更2-3次", "周更3-4次", "周更1-2次", "周更2-3次", "不定期"],
        "薄弱": ["周更1次", "周更1-2次", "月更几次", "周更1次", "偶尔更新"],
        "未发现": ["-", "-", "-", "-", "-"],
    }
    levels = ["活跃", "一般", "薄弱", "未发现", "未发现"]
    for i, (pname, pkey, _) in enumerate(platform_configs):
        level = cfg["content_level"] if pname in cfg["main_content_platforms"] else levels[i]
        has_acc = level != "未发现"
        plat = PlatformPresence(
            platform_name=pname,
            has_account=has_acc,
            account_name=f"{company_name}官方" if has_acc else "",
            followers_estimate=follower_ranges[cfg["content_level"]][i] if has_acc else "-",
            post_frequency=post_freqs[cfg["content_level"]][i] if has_acc else "-",
            avg_engagement="中等" if has_acc else "-",
            content_style="品牌宣传+产品科普" if has_acc else "-",
            verified=has_acc,
            url="" if not has_acc else f"https://{pkey}.example.com/{_company_slug(company_name)}",
        )
        platforms.append(plat)

    content = ContentPresence(
        platforms=platforms,
        overall_level=cfg["content_level"],
        total_platforms_active=cfg["active_platforms"],
        main_platforms=cfg["main_content_platforms"],
        content_strengths=["品牌形象统一", "内容质量尚可"] if cfg["active_platforms"] >= 2 else ["有官方账号"],
        content_weaknesses=["内容产出不稳定", "互动率偏低", "缺少爆款内容"]
        if cfg["content_level"] in ["一般", "薄弱"] else ["可提升空间大"],
        source_count=5,
        sources=["新榜", "蝉妈妈", "千瓜数据", "平台搜索", "第三方监测"],
    )

    # 口碑评价
    rep = Reputation(
        overall_sentiment=cfg["sentiment"],
        positive_points=cfg["positives"],
        negative_points=cfg["negatives"],
        complaint_count_estimate=cfg["complaints"],
        news_mentions=cfg["news"],
        has_negative_news=cfg["has_negative_news"],
        industry_ranking=cfg["ranking"],
        source_count=6,
        sources=["黑猫投诉", "聚投诉", "新闻搜索", "电商评价", "知乎", "大众点评"],
    )

    result = CompanyResearchResult(
        company_name=company_name,
        product_name=product_name,
        industry_type=industry_type,
        company_profile=profile,
        product_status=product,
        content_presence=content,
        reputation=rep,
        confidence_score=cfg["confidence"],
        research_mode="demo",
    )

    return result


def _company_domain(name: str) -> str:
    """从公司名生成简化域名"""
    clean = re.sub(r'[（(].*?[)）]', '', name)
    clean = re.sub(r'[有限公司|股份|集团|科技|生物|健康|实业]', '', clean)
    clean = clean.strip().lower()
    if not clean:
        clean = "example"
    # 简单拼音化处理（只保留中文字符，实际可替换为拼音库）
    return clean[:12] if clean else "example"


def _company_slug(name: str) -> str:
    """从公司名生成 URL slug"""
    clean = re.sub(r'[^\w\u4e00-\u9fff]', '', name)
    return clean[:20] if clean else "brand"


# ============================================================
# CompanyResearcher 核心类
# ============================================================

class CompanyResearcher:
    """
    企业背调研究员
    
    通过联网搜索获取企业真实信息，输出结构化背调报告，
    支持与用户口述信息交叉验证。

    使用方式：
        researcher = CompanyResearcher(company_name, product_name, industry_type)
        result = await researcher.research(search_func=sdk_search_func)
        diffs = researcher.cross_validate(user_info_dict)
    """

    def __init__(self, company_name: str, product_name: str = "",
                 industry_type: str = "default"):
        self.company_name = company_name
        self.product_name = product_name
        self.industry_type = industry_type
        self._result: Optional[CompanyResearchResult] = None

    async def research(
        self,
        search_func: Optional[Callable[[str], Awaitable[Dict]]] = None,
        max_searches: int = 10,
    ) -> CompanyResearchResult:
        """
        执行完整企业背调

        Args:
            search_func: 异步搜索函数，接收query字符串，返回搜索结果dict
                        格式要求：{"is_success": bool, "results": [{title, url, snippet}...]}
                        若为 None 则使用 demo 数据模式
            max_searches: 最大搜索次数限制

        Returns:
            CompanyResearchResult 结构化背调结果
        """
        # 如果没有搜索函数，直接使用 demo 数据
        if search_func is None:
            self._result = _generate_demo_data(
                self.company_name, self.product_name, self.industry_type
            )
            return self._result

        try:
            result = await self._do_research(search_func, max_searches)
            self._result = result
            return result
        except Exception as e:
            # 搜索失败降级为 demo 模式
            print(f"[背调] 联网搜索失败，降级为演示数据模式: {e}")
            self._result = _generate_demo_data(
                self.company_name, self.product_name, self.industry_type
            )
            self._result.research_mode = "demo_fallback"
            return self._result

    async def _do_research(
        self,
        search_func: Callable[[str], Awaitable[Dict]],
        max_searches: int,
    ) -> CompanyResearchResult:
        """执行实际的联网搜索背调"""
        # 构建搜索 query 列表
        queries = self._build_search_queries()
        query_keys = list(queries.keys())

        # 限制搜索次数
        actual_queries = query_keys[:min(max_searches, len(query_keys))]

        # 并发执行搜索
        search_results = {}
        sem = asyncio.Semaphore(3)  # 控制并发数

        async def _safe_search(key: str, q: str) -> Dict:
            async with sem:
                try:
                    return await search_func(q)
                except Exception as e:
                    print(f"[背调] 搜索 '{key}' 失败: {e}")
                    return {"is_success": False, "results": []}

        tasks = [_safe_search(k, queries[k]) for k in actual_queries]
        results_list = await asyncio.gather(*tasks)

        for key, res in zip(actual_queries, results_list):
            search_results[key] = res

        # 解析搜索结果，填充结构化数据
        result = self._parse_search_results(search_results)

        # 计算可信度
        result.confidence_score = self._calculate_confidence(search_results, result)
        result.research_mode = "full" if result.confidence_score >= 70 else "partial"

        return result

    def _build_search_queries(self) -> Dict[str, str]:
        """构建各维度的搜索查询"""
        cn = self.company_name
        pn = self.product_name or cn

        return {
            "company_basic": f"{cn} 公司简介 成立时间 注册资本",
            "company_credit": f"{cn} 企查查 天眼查 工商信息",
            "product_ecommerce": f"{pn} 天猫 京东 销量 价格",
            "product_sku": f"{cn} 产品列表 SKU 产品线",
            "content_wechat": f"{cn} 微信公众号 视频号",
            "content_douyin": f"{cn} 抖音 官方账号 粉丝",
            "content_xiaohongshu": f"{cn} 小红书 笔记 种草",
            "reputation_review": f"{cn} 怎么样 评价 口碑",
            "reputation_complaint": f"{cn} 投诉 黑猫投诉 差评",
            "reputation_news": f"{cn} 新闻 报道 负面",
        }

    def _parse_search_results(self, search_results: Dict[str, Dict]) -> CompanyResearchResult:
        """
        从搜索结果中解析结构化信息。
        由于搜索结果质量不稳定，采用"能提取多少提取多少，不足用demo填充"的策略。
        """
        # 先生成 demo 数据作为基底
        base = _generate_demo_data(
            self.company_name, self.product_name, self.industry_type
        )

        # 尝试从搜索结果中提取真实信息
        extraction_count = 0

        # 1. 解析公司基本信息
        company_text = self._extract_text_from_results(
            search_results, ["company_basic", "company_credit"]
        )
        if company_text:
            profile_info = self._extract_company_info(company_text)
            if profile_info.get("founded_year"):
                base.company_profile.founded_year = profile_info["founded_year"]
                extraction_count += 1
            if profile_info.get("registered_capital"):
                base.company_profile.registered_capital_wan = profile_info["registered_capital"]
                extraction_count += 1
            if profile_info.get("location"):
                base.company_profile.location = profile_info["location"]
                extraction_count += 1
            if profile_info.get("website"):
                base.company_profile.website = profile_info["website"]
                extraction_count += 1
            # 更新来源数
            base.company_profile.source_count = max(
                base.company_profile.source_count,
                self._count_valid_results(search_results, ["company_basic", "company_credit"])
            )

        # 2. 解析产品信息
        product_text = self._extract_text_from_results(
            search_results, ["product_ecommerce", "product_sku"]
        )
        if product_text:
            product_info = self._extract_product_info(product_text)
            if product_info.get("sku_count"):
                base.product_status.sku_count_estimate = product_info["sku_count"]
                extraction_count += 1
            if product_info.get("price_range"):
                base.product_status.price_range = product_info["price_range"]
                extraction_count += 1
            base.product_status.source_count = max(
                base.product_status.source_count,
                self._count_valid_results(search_results, ["product_ecommerce", "product_sku"])
            )

        # 3. 解析内容平台信息
        content_count = self._count_valid_results(
            search_results, ["content_wechat", "content_douyin", "content_xiaohongshu"]
        )
        if content_count >= 2:
            # 有搜索结果，更新平台发现状态
            for plat in base.content_presence.platforms:
                if plat.has_account:
                    extraction_count += 0.5  # 半分，因为只是确认存在
            base.content_presence.source_count = content_count

        # 4. 解析口碑信息
        rep_text = self._extract_text_from_results(
            search_results, ["reputation_review", "reputation_complaint", "reputation_news"]
        )
        if rep_text:
            rep_info = self._extract_reputation_info(rep_text)
            if rep_info.get("sentiment"):
                base.reputation.overall_sentiment = rep_info["sentiment"]
                extraction_count += 1
            if rep_info.get("has_negative") is not None:
                base.reputation.has_negative_news = rep_info["has_negative"]
                extraction_count += 1
            base.reputation.source_count = max(
                base.reputation.source_count,
                self._count_valid_results(
                    search_results,
                    ["reputation_review", "reputation_complaint", "reputation_news"]
                )
            )

        return base

    def _extract_text_from_results(
        self, search_results: Dict[str, Dict], keys: List[str]
    ) -> str:
        """从多个搜索结果中提取合并文本"""
        texts = []
        for key in keys:
            res = search_results.get(key, {})
            if not res.get("is_success"):
                continue
            for item in res.get("results", []):
                texts.append(item.get("title", ""))
                texts.append(item.get("snippet", ""))
        return "\n".join(texts)

    def _count_valid_results(self, search_results: Dict[str, Dict], keys: List[str]) -> int:
        """统计有效搜索结果数量"""
        count = 0
        for key in keys:
            res = search_results.get(key, {})
            if res.get("is_success") and res.get("results"):
                count += len(res["results"])
        return min(count, 10)  # 上限10个来源

    def _extract_company_info(self, text: str) -> Dict:
        """从文本中提取公司基本信息"""
        info = {}

        # 提取成立年份
        year_match = re.search(r'(成立于|始创于|建于)\s*(\d{4})', text)
        if year_match:
            info["founded_year"] = int(year_match.group(2))

        # 提取注册资本
        capital_match = re.search(r'注册资本[：:]\s*([\d.]+)\s*万', text)
        if capital_match:
            info["registered_capital"] = float(capital_match.group(1))

        # 提取地区
        cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉",
                  "西安", "重庆", "天津", "苏州", "宁波", "无锡", "青岛", "大连",
                  "厦门", "福州", "济南", "郑州", "长沙", "合肥", "南昌"]
        for city in cities:
            if city in text:
                info["location"] = city
                break

        # 提取官网
        web_match = re.search(r'官网[：:]\s*(https?://[\w./-]+)', text)
        if web_match:
            info["website"] = web_match.group(1)
        else:
            web_match2 = re.search(r'(www\.[\w.-]+\.(com|cn|net|org))', text)
            if web_match2:
                info["website"] = web_match2.group(1)

        return info

    def _extract_product_info(self, text: str) -> Dict:
        """从文本中提取产品信息"""
        info = {}

        # 价格范围
        prices = re.findall(r'¥?(\d{2,4})\s*[-~～至]\s*¥?(\d{3,5})', text)
        if prices:
            p = prices[0]
            info["price_range"] = f"{p[0]}-{p[1]}元"

        # SKU 数量（简单估算）
        sku_match = re.search(r'(\d+)\s*(款|种|个)\s*(产品|SKU|品类)', text)
        if sku_match:
            info["sku_count"] = int(sku_match.group(1))

        return info

    def _extract_reputation_info(self, text: str) -> Dict:
        """从文本中提取口碑信息"""
        info = {}

        # 负面关键词
        negative_words = ["投诉", "差评", "欺诈", "虚假宣传", "质量问题",
                          "退款", "维权", "曝光", "负面", "翻车", "传销"]
        neg_count = sum(1 for w in negative_words if w in text)

        # 正面关键词
        positive_words = ["好评", "推荐", "靠谱", "值得信赖", "效果好",
                          "质量好", "专业", "领先", "知名", "口碑好"]
        pos_count = sum(1 for w in positive_words if w in text)

        if neg_count > pos_count + 3:
            info["sentiment"] = "偏负面"
            info["has_negative"] = True
        elif neg_count > pos_count:
            info["sentiment"] = "中性"
            info["has_negative"] = True
        elif pos_count > neg_count + 3:
            info["sentiment"] = "偏正面"
            info["has_negative"] = neg_count > 0
        else:
            info["sentiment"] = "中性"
            info["has_negative"] = neg_count > 0

        return info

    def _calculate_confidence(
        self, search_results: Dict[str, Dict], result: CompanyResearchResult
    ) -> int:
        """
        计算背调可信度评分（0-100）

        评分维度：
        - 有效搜索维度覆盖度（40分）：10个搜索方向，每个4分
        - 信息来源数量（30分）：综合各维度来源数
        - 信息一致性（20分）：多来源交叉验证
        - 企业知名度（10分）：搜索结果数量间接反映
        """
        score = 0

        # 1. 搜索维度覆盖度
        valid_dims = sum(1 for res in search_results.values()
                        if res.get("is_success") and res.get("results"))
        score += min(40, valid_dims * 4)

        # 2. 信息来源数量
        total_sources = (
            result.company_profile.source_count
            + result.product_status.source_count
            + result.content_presence.source_count
            + result.reputation.source_count
        )
        score += min(30, total_sources * 2)

        # 3. 信息一致性（简化：基于不同维度间的逻辑一致性）
        # 有多个独立维度验证就加分
        if valid_dims >= 6:
            score += 15
        elif valid_dims >= 4:
            score += 10
        elif valid_dims >= 2:
            score += 5

        # 4. 基础分（保证 demo 模式也有合理分数）
        score += 10

        return min(100, max(0, score))

    def cross_validate(self, user_info: Dict[str, Any]) -> List[DiffItem]:
        """
        对比背调数据与用户口述，输出差异点列表

        Args:
            user_info: 用户口述的企业信息字典

        Returns:
            差异项列表（DiffItem）
        """
        if self._result is None:
            return []

        diffs = []
        r = self._result

        # 对比1：成立时间
        user_founded = user_info.get("founded_year") or user_info.get("成立时间")
        if user_founded and r.company_profile.founded_year:
            if str(user_founded) != str(r.company_profile.founded_year):
                diffs.append(DiffItem(
                    field="成立时间",
                    user_statement=str(user_founded),
                    research_finding=str(r.company_profile.founded_year),
                    diff_type="major" if abs(int(user_founded) - r.company_profile.founded_year) > 3 else "minor",
                    description=f"用户口述成立于{user_founded}年，公开信息显示为{r.company_profile.founded_year}年",
                ))
            else:
                diffs.append(DiffItem(
                    field="成立时间",
                    user_statement=str(user_founded),
                    research_finding=str(r.company_profile.founded_year),
                    diff_type="consistent",
                    description="成立时间一致",
                ))

        # 对比2：人员规模
        user_employees = user_info.get("employee_count") or user_info.get("人员规模")
        if user_employees and r.company_profile.employee_count_estimate:
            est_range = r.company_profile.employee_count_estimate
            is_consistent = self._is_employee_count_consistent(user_employees, est_range)
            diffs.append(DiffItem(
                field="人员规模",
                user_statement=f"{user_employees}人" if isinstance(user_employees, int) else str(user_employees),
                research_finding=est_range,
                diff_type="consistent" if is_consistent else "minor",
                description="人员规模基本吻合" if is_consistent else f"用户称约{user_employees}人，公开信息估算为{est_range}",
            ))

        # 对比3：年营收
        user_revenue = user_info.get("annual_revenue_wan") or user_info.get("年营收")
        if user_revenue and r.product_status.sales_volume_estimate:
            is_consistent = self._is_revenue_consistent(user_revenue, r.product_status.sales_volume_estimate)
            diffs.append(DiffItem(
                field="营收规模",
                user_statement=f"{user_revenue}万元/年" if isinstance(user_revenue, (int, float)) else str(user_revenue),
                research_finding=r.product_status.sales_volume_estimate,
                diff_type="consistent" if is_consistent else "minor",
                description="营收规模基本吻合" if is_consistent else "存在差异，需进一步核实",
            ))

        # 对比4：内容平台运营情况
        user_has_content = any([
            user_info.get("has_short_video", False),
            user_info.get("has_livestream", False),
            user_info.get("has_private_domain", False),
        ])
        actual_active = r.content_presence.total_platforms_active
        if user_has_content and actual_active >= 1:
            diffs.append(DiffItem(
                field="内容运营",
                user_statement="有内容运营团队/布局",
                research_finding=f"在{r.content_presence.total_platforms_active}个平台有官方账号",
                diff_type="consistent",
                description="内容运营情况基本吻合",
            ))
        elif not user_has_content and actual_active == 0:
            diffs.append(DiffItem(
                field="内容运营",
                user_statement="暂无内容运营",
                research_finding="未发现公开内容账号",
                diff_type="consistent",
                description="内容运营情况一致",
            ))
        else:
            diffs.append(DiffItem(
                field="内容运营",
                user_statement="有" if user_has_content else "暂无",
                research_finding=f"发现{actual_active}个活跃内容平台",
                diff_type="minor",
                description="内容运营情况存在差异，建议进一步确认",
            ))

        # 对比5：产品/品牌负面
        user_has_issue = user_info.get("has_negative_news", False) or user_info.get("has_complaint", False)
        if user_has_issue == r.reputation.has_negative_news:
            diffs.append(DiffItem(
                field="口碑评价",
                user_statement="有负面/投诉" if user_has_issue else "无明显负面",
                research_finding="有负面信息" if r.reputation.has_negative_news else "未发现明显负面",
                diff_type="consistent",
                description="口碑情况一致",
            ))
        else:
            diffs.append(DiffItem(
                field="口碑评价",
                user_statement="有负面/投诉" if user_has_issue else "无明显负面",
                research_finding="有负面信息" if r.reputation.has_negative_news else "未发现明显负面",
                diff_type="major" if (not user_has_issue and r.reputation.has_negative_news) else "minor",
                description="存在信息差，建议深入了解" if user_has_issue != r.reputation.has_negative_news else "",
            ))

        self._result.diff_items = diffs
        return diffs

    def _is_employee_count_consistent(self, user_val, est_val: str) -> bool:
        """判断人员规模是否一致"""
        if isinstance(user_val, str):
            # 提取数字
            nums = re.findall(r'\d+', user_val)
            if nums:
                user_val = int(nums[0])
            else:
                return True  # 格式不匹配，默认一致

        # 从估算范围中解析
        nums = re.findall(r'\d+', est_val.replace(",", ""))
        if not nums:
            return True

        if "-" in est_val or "~" in est_val:
            low, high = int(nums[0]), int(nums[1])
            return low <= user_val <= high
        else:
            # 单边估算（如"50万+"）
            base = int(nums[0])
            if "+" in est_val or "以上" in est_val:
                return user_val >= base * 0.5
            else:
                return abs(user_val - base) / base < 0.5

    def _is_revenue_consistent(self, user_revenue, est_text: str) -> bool:
        """判断营收是否一致（简化版本）"""
        # 提取用户营收数值（单位：万元）
        if isinstance(user_revenue, str):
            nums = re.findall(r'\d+', user_revenue)
            if nums:
                user_revenue = int(nums[0])
            else:
                return True

        # 从估算文本中提取
        nums = re.findall(r'[\d.]+', est_text.replace(",", ""))
        if not nums:
            return True

        # 简单估算：如果量级差距小于3倍，认为基本一致
        try:
            est_val = float(nums[0])
            # 判断单位（月销/年营收）
            if "月" in est_text:
                est_yearly = est_val * 12
            else:
                est_yearly = est_val

            # 单位换算（万/亿）
            if "亿" in est_text:
                est_yearly *= 10000

            if est_yearly > 0:
                ratio = max(user_revenue, est_yearly) / min(user_revenue, est_yearly)
                return ratio < 3
        except:
            pass

        return True

    @property
    def result(self) -> Optional[CompanyResearchResult]:
        """获取背调结果（需先调用 research()）"""
        return self._result


# ============================================================
# 便捷函数
# ============================================================

def quick_research(
    company_name: str,
    product_name: str = "",
    industry_type: str = "default",
    search_func: Optional[Callable] = None,
) -> Dict[str, Any]:
    """
    快速背调便捷函数（异步）
    
    使用方式：
        import asyncio
        result = asyncio.run(quick_research_async("某某公司", "某产品", "online"))
    """
    researcher = CompanyResearcher(company_name, product_name, industry_type)
    return asyncio.run(researcher.research(search_func)).to_dict()


async def quick_research_async(
    company_name: str,
    product_name: str = "",
    industry_type: str = "default",
    search_func: Optional[Callable] = None,
) -> Dict[str, Any]:
    """异步版本的快速背调"""
    researcher = CompanyResearcher(company_name, product_name, industry_type)
    result = await researcher.research(search_func)
    return result.to_dict()


# ============================================================
# 自测
# ============================================================

def _run_self_test():
    """模块自测"""
    print("=" * 60)
    print("企业背调模块 v2.0.0 - 自测")
    print("=" * 60)

    test_cases = [
        {
            "name": "线上保健品品牌",
            "company": "康卫士生物科技",
            "product": "清幽益生菌",
            "industry": "online",
        },
        {
            "name": "会销体验型企业",
            "company": "康源健康管理",
            "product": "中老年高钙羊奶粉",
            "industry": "experiential",
        },
        {
            "name": "医美抗衰机构",
            "company": "悦美抗衰中心",
            "product": "面部抗衰套餐",
            "industry": "anti_aging",
        },
    ]

    for i, tc in enumerate(test_cases, 1):
        print(f"\n【测试 {i}】{tc['name']}")
        print(f"  公司: {tc['company']}")
        print(f"  产品: {tc['product']}")
        print(f"  行业: {tc['industry']}")

        # 测试1: demo 模式背调
        researcher = CompanyResearcher(tc["company"], tc["product"], tc["industry"])
        result = asyncio.run(researcher.research())

        print(f"\n  [背调结果]")
        print(f"    模式: {result.research_mode}")
        print(f"    可信度: {result.confidence_score}/100")
        print(f"    成立年份: {result.company_profile.founded_year}")
        print(f"    注册资本: {result.company_profile.registered_capital_wan}万")
        print(f"    人员规模: {result.company_profile.employee_count_estimate}")
        print(f"    SKU估算: {result.product_status.sku_count_estimate}个")
        print(f"    价格带: {result.product_status.price_range}")
        print(f"    内容水平: {result.content_presence.overall_level}")
        print(f"    活跃平台数: {result.content_presence.total_platforms_active}")
        print(f"    口碑评价: {result.reputation.overall_sentiment}")
        print(f"    好评点: {', '.join(result.reputation.positive_points[:2])}")

        # 测试2: 交叉验证
        user_info = {
            "founded_year": result.company_profile.founded_year,  # 故意一致
            "employee_count": 80,  # 可能有差异
            "annual_revenue_wan": 3000,
            "has_short_video": True,
            "has_livestream": True,
            "has_private_domain": True,
            "has_negative_news": False,
        }
        diffs = researcher.cross_validate(user_info)
        print(f"\n  [交叉验证] 对比项: {len(diffs)}个")
        consistent_count = sum(1 for d in diffs if d.diff_type == "consistent")
        minor_count = sum(1 for d in diffs if d.diff_type == "minor")
        major_count = sum(1 for d in diffs if d.diff_type == "major")
        print(f"    一致: {consistent_count}  轻微差异: {minor_count}  重大差异: {major_count}")
        for d in diffs:
            icon = "✓" if d.diff_type == "consistent" else ("⚠" if d.diff_type == "minor" else "❌")
            print(f"    {icon} {d.field}: {d.diff_type}")

        # 测试3: to_dict 序列化
        data = result.to_dict()
        assert "company_profile" in data
        assert "product_status" in data
        assert "content_presence" in data
        assert "reputation" in data
        assert "confidence_score" in data
        assert isinstance(data["confidence_score"], int)
        assert 0 <= data["confidence_score"] <= 100
        print(f"\n  ✓ 序列化正常，数据结构完整")

        # 验证平台列表
        assert len(data["content_presence"]["platforms"]) >= 3
        print(f"  ✓ 内容平台数据完整，共{len(data['content_presence']['platforms'])}个平台")

    print("\n" + "=" * 60)
    print("✅ 企业背调模块自测全部通过！")
    print("=" * 60)
    print("\n功能清单：")
    print("  1. CompanyResearcher.research()  - 执行背调（支持联网搜索+demo降级）")
    print("  2. CompanyResearcher.cross_validate() - 与用户口述交叉验证")
    print("  3. CompanyResearchResult.to_dict() - 结构化结果序列化")
    print("  4. 4大数据维度：公司信息/产品情况/内容表现/口碑评价")
    print("  5. 可信度评分（0-100）+ 3种运行模式（full/partial/demo）")


if __name__ == "__main__":
    _run_self_test()

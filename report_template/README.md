# AI内容增长诊断报告模板使用说明

## 模板概述

本模板是为**健康行业AI内容增长系统 v2.0**设计的精美单页HTML诊断报告模板，采用深蓝主色 + 青色辅色的专业科技感配色，支持响应式布局和丰富的交互动效。

### 文件位置
```
report_template/
├── demo_report.html      # 主模板文件（含完整Demo数据）
└── README.md             # 本文档
```

---

## 模板特性

- ✅ **纯单文件HTML**：所有CSS/JS内联，不依赖外部CDN，可直接打开使用
- ✅ **响应式设计**：手机端单列布局，桌面端自适应双列
- ✅ **交互动效丰富**：
  - 数字滚动动画（评分、价格）
  - 评分圆环进度动画
  - 雷达图渐入动画
  - 模块折叠展开
  - 报价档位Tab切换
  - 滚动渐入效果
- ✅ **10大核心模块**：Hero封面、总览结论、五维雷达、产品识别、信任路径、核心瓶颈、模块推荐、报价ROI、30天计划、底部CTA

---

## 数据替换接口

模板中所有业务数据统一封装在 `reportData` 对象中（位于HTML底部 `<script>` 标签内），可通过以下方式替换：

### 方式一：直接修改 reportData 对象

找到模板中的 `reportData` 对象：

```javascript
const reportData = {
  company: '康卫士 · 清幽益生菌',     // 公司/品牌名称
  date: '2026年7月9日',              // 诊断日期
  totalScore: 62,                    // 总评分(0-100)
  scoreLevel: '成长期',              // 评分等级文案
  maturityLevel: '成长',             // 成熟度等级
  conclusion: '品牌已建立基础产品认知...',  // 一句话结论
  suggestion: '建议优先落地...',           // 行动建议(支持HTML)
  radar: [                           // 五维能力数据
    { name: '产品表达', score: 68 },
    { name: '内容生产', score: 45 },
    { name: '信任构建', score: 52 },
    { name: '转化体系', score: 58 },
    { name: '团队执行', score: 70 }
  ],
  productTags: ['益生菌类', '肠胃健康', ...],  // 产品标签
  productDesc: '产品详细描述...',              // 产品描述
  strategyDirection: '内容策略方向...'         // 策略方向
};
```

修改该对象的属性值即可替换对应区域的数据。

---

### 方式二：从外部JSON加载

如果需要从动态数据源加载，可以在脚本中添加以下代码：

```javascript
// 从URL参数获取数据
async function loadReportData() {
  const urlParams = new URLSearchParams(window.location.search);
  const dataUrl = urlParams.get('data');
  if (dataUrl) {
    const res = await fetch(dataUrl);
    const json = await res.json();
    Object.assign(reportData, json);
    // 重新渲染
    renderReport();
  }
}
```

---

## 各模块数据字段说明

### 1. Hero封面区

| 字段 | 类型 | 说明 | 位置 |
|------|------|------|------|
| `company` | string | 公司/品牌名称 | `#companyName` |
| `date` | string | 诊断日期 | `#reportDate` |
| `totalScore` | number | 总评分(0-100) | `#totalScore` + 圆环动画 |
| `scoreLevel` | string | 评分等级文案 | `#scoreLevel` |

### 2. 总览结论区

| 字段 | 类型 | 说明 | 位置 |
|------|------|------|------|
| `maturityLevel` | string | 成熟度等级名称 | `#maturityLevel` |
| `conclusion` | string | 一句话结论（纯文本） | `#conclusionText` |
| `suggestion` | string | 行动建议（支持HTML标签） | `#suggestionText` |

### 3. 五维能力雷达图

| 字段 | 类型 | 说明 |
|------|------|------|
| `radar` | Array | 五维能力数组，每项含 `name`(名称) 和 `score`(分数0-100) |

> **注意**：雷达图默认5个维度，顺序为：产品表达→内容生产→信任构建→转化体系→团队执行。如需调整维度数量，需同步修改SVG中的多边形网格、轴线和标签数量。

### 4. 产品类型识别

| 字段 | 类型 | 说明 | 位置 |
|------|------|------|------|
| `productTags` | Array\<string\> | 产品标签列表 | `#productTags` |
| `productDesc` | string | 产品详细描述 | `#productDesc` |
| `strategyDirection` | string | 内容策略方向 | `#strategyDirection` |

### 5. 信任成交路径

**当前为静态HTML结构**，如需动态生成：

- 主路径步骤：`.path-step` 元素，含 `.path-step-num`（序号）、`.path-step-info h4`（标题）、`.path-step-info p`（副标题）
- 当前高亮步骤：添加 `.active` class
- 备选路径：`.alt-path-item` 元素列表

### 6. 核心瓶颈 Top3

**当前为静态HTML结构**，每个瓶颈项结构如下：

```html
<div class="bottleneck-item">
  <div class="bottleneck-header" onclick="toggleBottleneck(this)">
    <div class="severity-badge severity-high|medium|low">
      <span class="severity-rank">1</span>       <!-- 排名 -->
      <span class="severity-label">严重</span>   <!-- 级别文案 -->
    </div>
    <div class="bottleneck-title-area">
      <div class="bottleneck-title">标题</div>
      <div class="bottleneck-meta">副标题</div>
    </div>
    <div class="bottleneck-toggle">▼</div>
  </div>
  <div class="bottleneck-body">
    <div class="bottleneck-body-inner">
      <div class="bottleneck-detail symptom">     <!-- 症状 -->
        <h5>症状表现</h5><p>...</p>
      </div>
      <div class="bottleneck-detail impact">      <!-- 影响 -->
        <h5>业务影响</h5><p>...</p>
      </div>
      <div class="bottleneck-detail solution">    <!-- 解决方向 -->
        <h5>解决方向</h5><ul><li>...</li></ul>
      </div>
    </div>
  </div>
</div>
```

严重程度等级：
- `severity-high`：红色（严重）
- `severity-medium`：橙色（中等）
- `severity-low`：黄色（一般）

### 7. 7大模块推荐

**当前为静态HTML结构**，每个模块项结构：

```html
<div class="module-item [expanded]">  <!-- expanded 默认展开 -->
  <div class="module-header" onclick="toggleModule(this)">
    <div class="module-priority">1</div>  <!-- 优先级序号 -->
    <div class="module-info">
      <div class="module-name">模块名称</div>
      <div class="module-desc-short">简短描述</div>
    </div>
    <div class="module-toggle">▼</div>
  </div>
  <div class="module-body">
    <div class="module-body-inner">
      <p class="module-detail-desc">详细描述...</p>
      <div class="module-deliverables">
        <h5>📦 交付物</h5>
        <ul><li>交付物1</li><li>...</li></ul>
      </div>
    </div>
  </div>
</div>
```

### 8. 报价与ROI

**当前为静态HTML结构**，共4个档位Tab：

| Tab ID | 档位 | 价格data-target |
|--------|------|-----------------|
| `tab-basic` | 基础版 | 9800 |
| `tab-standard` | 标准版 | 19800 |
| `tab-advanced` | 进阶版 | 39800 |
| `tab-vip` | 陪跑版 | 68000 |

每个档位内容结构：
- `.price-header`：价格展示区（`.price-amount` + `.price-period`）
- `.price-metrics`：3个关键指标（ROI、覆盖模块数、回本周期）
- `.price-module-list`：包含模块标签列表

> 价格数字动画通过 `.price-num` 的 `data-target` 属性控制目标值。

### 9. 30天执行计划

**当前为静态HTML结构**，每周时间线条目：

```html
<div class="timeline-item">
  <div class="timeline-dot"></div>
  <div class="timeline-week">第 1 周</div>
  <h3 class="timeline-title">诊断与基建</h3>
  <ul class="timeline-tasks">
    <li>任务1</li>
    <li>任务2</li>
  </ul>
  <span class="timeline-deliverable">📦 交付：...</span>
</div>
```

### 10. 底部CTA区

- CTA按钮：`.cta-button`，点击触发 `openShareModal()`
- 分享弹窗：`#shareModal`，含确认/取消按钮
- 分享逻辑：修改 `confirmShare()` 函数对接实际分享接口

---

## 自定义样式指南

### 修改主色调

在CSS `:root` 变量中修改：

```css
:root {
  --primary-900: #0F172A;   /* 深蓝主色-最深 */
  --primary-700: #1E3A8A;   /* 深蓝主色 */
  --primary-600: #2563EB;   /* 蓝色强调 */
  --cyan-500: #06B6D4;      /* 青色辅色 */
  --cyan-400: #22D3EE;      /* 青色亮调 */
  --cyan-300: #67E8F9;      /* 青色最亮 */
}
```

修改这些变量即可全局更换配色方案。

### 修改圆角/阴影

```css
:root {
  --radius-lg: 16px;     /* 卡片圆角 */
  --radius-xl: 24px;     /* 大圆角 */
  --shadow-md: 0 4px 12px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 10px 25px rgba(15, 23, 42, 0.1);
}
```

---

## 动态数据接入示例

### 使用JavaScript渲染瓶颈列表

```javascript
function renderBottlenecks(bottlenecks) {
  const container = document.getElementById('bottleneckList');
  const severityMap = {
    high: { class: 'severity-high', label: '严重' },
    medium: { class: 'severity-medium', label: '中等' },
    low: { class: 'severity-low', label: '一般' }
  };
  
  container.innerHTML = bottlenecks.map((b, i) => `
    <div class="bottleneck-item fade-in ${i === 0 ? 'expanded' : ''}">
      <div class="bottleneck-header" onclick="toggleBottleneck(this)">
        <div class="severity-badge ${severityMap[b.severity].class}">
          <span class="severity-rank">${i + 1}</span>
          <span class="severity-label">${severityMap[b.severity].label}</span>
        </div>
        <div class="bottleneck-title-area">
          <div class="bottleneck-title">${b.title}</div>
          <div class="bottleneck-meta">${b.subtitle}</div>
        </div>
        <div class="bottleneck-toggle">▼</div>
      </div>
      <div class="bottleneck-body">
        <div class="bottleneck-body-inner">
          <div class="bottleneck-detail symptom">
            <h5>症状表现</h5><p>${b.symptom}</p>
          </div>
          <div class="bottleneck-detail impact">
            <h5>业务影响</h5><p>${b.impact}</p>
          </div>
          <div class="bottleneck-detail solution">
            <h5>解决方向</h5>
            <ul>${b.solutions.map(s => `<li>${s}</li>`).join('')}</ul>
          </div>
        </div>
      </div>
    </div>
  `).join('');
}
```

---

## 技术栈说明

- **原生HTML5**：语义化结构
- **原生CSS3**：CSS变量、Flex/Grid布局、动画、渐变
- **原生JavaScript (ES6+)**：无框架依赖，DOM操作 + IntersectionObserver
- **SVG**：雷达图、评分圆环，矢量图形保证清晰度
- **零外部依赖**：所有资源内联，离线可用

---

## 浏览器兼容性

| 浏览器 | 最低版本 | 说明 |
|--------|----------|------|
| Chrome | 80+ | 完全支持 |
| Safari | 14+ | 完全支持 |
| Firefox | 75+ | 完全支持 |
| Edge | 80+ | 完全支持 |
| 微信内置浏览器 | 最新版 | 完全支持 |

> 不支持IE系列浏览器。

---

## 常见问题

### Q1：如何修改品牌名称和Logo？

当前模板使用文字标题，如需添加Logo，在 `.hero-content` 中插入图片即可：
```html
<img src="data:image/svg+xml,..." alt="Logo" style="height:40px;">
```

### Q2：如何添加更多瓶颈项/模块？

复制对应HTML结构，修改序号和内容即可。注意保持class名称一致以确保动画和交互正常。

### Q3：如何调整动画速度？

在CSS中找到对应的 `transition` 或 `animation` 属性，调整时间值即可。
常见动画位置：
- 评分圆环：`.score-ring-progress` 的 `transition`
- 雷达图：`animateRadar()` 函数中的 `setTimeout` 延迟和transition时间
- 折叠展开：`.bottleneck-body` 和 `.module-body` 的 `max-height` transition

### Q4：如何对接分享功能？

修改 `confirmShare()` 函数，替换为实际的分享API调用：
```javascript
async function confirmShare() {
  // 调用分享接口
  await fetch('/api/share', {
    method: 'POST',
    body: JSON.stringify({ reportId: 'xxx', target: 'fanzong' })
  });
  closeShareModal();
  alert('分享成功！');
}
```

### Q5：模板文件太大，如何优化？

- 移除不需要的模块（保留核心结构即可）
- 压缩CSS/JS（可使用在线工具或构建工具）
- 将SVG转为更精简的格式

---

## 更新日志

### v1.0.0 (2026-07-09)
- 初始版本发布
- 完成10大核心模块设计
- 支持响应式布局和丰富动效
- 内置康卫士·清幽益生菌Demo数据

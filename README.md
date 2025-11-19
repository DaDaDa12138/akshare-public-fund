# AkShare Public Fund - 公募基金数据可视化平台

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.4-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于 [AkShare](https://github.com/akfamily/akshare) 开源金融数据接口库开发的公募基金数据可视化平台，提供 **22,958+ 只公募基金**的实时数据查询、净值分析、持仓明细、收益率统计和风险指标计算。

## ✨ 核心功能

### 📊 基金数据分析
- **基金搜索与查询** - 支持基金代码/名称模糊搜索，快速定位目标基金
- **实时净值估算** - 提供盘中实时估值（非交易时段显示最新净值）
- **历史净值走势** - 可视化展示任意时间段的净值变化趋势
- **收益率统计** - 自动计算近1月/3月/6月/1年/3年/成立来收益率
- **季度持仓明细** - 展示股票/债券/现金配置及前10大重仓股
- **历史分红记录** - 查询基金历史分红派息情况
- **风险指标** - 最大回撤、年化波动率、夏普比率等风险评估指标

### 📈 市场数据
- **基金排行榜** - 按收益率/规模/评级多维度排序
- **基金公司排名** - 基金公司管理规模和产品数量统计
- **基金对比** - 支持多只基金净值走势对比分析
- **货币基金专区** - 货币市场基金收益率排行
- **场内基金行情** - ETF/LOF 实时市价和溢折价率

### 🌐 另类数据（v1.4.0+）
集成 **25+ 个另类数据接口**，包括：
- **汽车销量** - 中国乘联会市场数据、厂商排名、车型分类
- **空气质量** - 全国城市空气质量实时监测与排名
- **电影票房** - 实时票房、日/周/月/年度排行榜
- **财富排行** - 财富500强、福布斯、新财富、胡润榜

### 🔧 实用工具
- **数据导出** - 支持 CSV/Excel 格式导出分析结果
- **收藏夹** - 本地收藏关注基金，快速访问
- **缓存管理** - 多层缓存优化（内存 + SQLite），支持手动清理

---

## 🛠️ 技术栈

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11 | 编程语言 |
| **FastAPI** | Latest | RESTful API 框架 |
| **AkShare** | 1.17+ | 金融数据源（开源） |
| **AKTools** | 0.0.91 | AkShare HTTP 服务包装 |
| **SQLite** | 3.x | 数据持久化与缓存 |
| **APScheduler** | Latest | 定时任务调度（自动更新数据） |

### 前端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | 3.4 | 渐进式JavaScript框架 |
| **TypeScript** | Latest | 类型安全 |
| **Element Plus** | Latest | UI 组件库 |
| **ECharts** | 5.x | 数据可视化图表 |
| **Pinia** | Latest | Vue 状态管理 |
| **Vue Router** | Latest | 路由管理 |
| **Vite** | Latest | 构建工具 |

### 部署方案
- **Docker Compose** - 容器化部署，一键启动
- **Nginx** - 反向代理与静态资源服务

---

## 🚀 快速开始

### 前置要求
- Docker 20.10+
- Docker Compose 1.29+

或本地开发环境：
- Python 3.11+
- Node.js 16+

### 使用 Docker Compose（推荐）

#### 1. 克隆仓库
```bash
git clone https://github.com/YOUR_USERNAME/akshare-public-fund.git
cd akshare-public-fund
```

#### 2. 启动服务
```bash
docker compose up -d
```

服务启动后将自动完成：
- 安装后端 Python 依赖
- 初始化 SQLite 数据库
- 构建前端生产版本
- 启动 FastAPI 后端（端口 8080）
- 启动 Nginx 前端服务（端口 9095）

#### 3. 访问应用
- **前端界面**: http://localhost:9095
- **后端 API 文档**: http://localhost:8080/docs （Swagger UI）
- **后端 ReDoc 文档**: http://localhost:8080/redoc

#### 4. 查看日志
```bash
# 查看所有服务日志
docker compose logs -f

# 仅查看后端日志
docker compose logs -f backend

# 仅查看前端日志
docker compose logs -f frontend
```

#### 5. 停止服务
```bash
docker compose down
```

---

### 本地开发

#### 后端开发
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器（支持热重载）
python main.py

# 访问 http://localhost:8080/docs
```

**环境变量配置**（可选）:
```bash
export LOG_LEVEL=DEBUG          # 日志级别
export DB_PATH=./db/akshare.db  # 数据库路径
```

#### 前端开发
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（支持热重载）
npm run dev
# 访问 http://localhost:5173

# 生产构建
npm run build

# 预览构建产物
npm run preview
```

**开发时 API 代理配置** (vite.config.ts):
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
    }
  }
}
```

---

## 📂 项目结构

```
akshare-public-fund/
├── backend/                    # 后端服务
│   ├── main.py                # FastAPI 应用主程序 (~2800行)
│   ├── requirements.txt       # Python 依赖
│   ├── Dockerfile             # 后端容器构建文件
│   ├── db/                    # 数据库模块
│   │   ├── database.py        # 数据库管理（9张缓存表）
│   │   ├── scheduler.py       # APScheduler 定时任务
│   │   ├── cache_helper.py    # 多层缓存助手
│   │   └── __init__.py
│   ├── middleware/            # 中间件
│   │   ├── error_handler.py   # 统一错误处理
│   │   └── __init__.py
│   ├── utils/                 # 工具类
│   │   ├── logger.py          # 结构化日志
│   │   ├── export_utils.py    # 数据导出（CSV/Excel）
│   │   ├── api_cache.py       # API 响应缓存
│   │   └── __init__.py
│   └── scripts/               # 辅助脚本
│       ├── test_alternative_apis.py  # 另类数据接口测试
│       └── init_dividend_data.py     # 初始化分红数据
│
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── main.ts           # Vue 入口文件
│   │   ├── App.vue           # 根组件
│   │   ├── api/              # API 请求封装
│   │   │   ├── fund.ts       # 基金数据 API
│   │   │   ├── alternative.ts # 另类数据 API
│   │   │   ├── cache.ts      # 缓存管理 API
│   │   │   └── fallback.ts   # 错误降级策略
│   │   ├── views/            # 页面组件 (13个)
│   │   │   ├── FundDetail.vue       # 基金详情页
│   │   │   ├── FundRanking.vue      # 基金排行榜
│   │   │   ├── AlternativeData.vue  # 另类数据
│   │   │   └── ...
│   │   ├── components/       # 可复用组件 (16个)
│   │   │   ├── alternative/  # 另类数据子组件 (10个)
│   │   │   ├── FundCharts.vue
│   │   │   └── ...
│   │   ├── router/           # Vue Router 配置
│   │   │   └── index.ts
│   │   ├── stores/           # Pinia 状态管理
│   │   │   ├── fund.ts       # 基金数据状态
│   │   │   └── favorites.ts  # 收藏夹状态
│   │   ├── types/            # TypeScript 类型定义
│   │   │   ├── fund.ts
│   │   │   └── alternative.ts
│   │   ├── utils/            # 工具函数
│   │   │   ├── favorites.ts
│   │   │   └── exportExcel.ts
│   │   ├── composables/      # Composition API
│   │   │   └── useTheme.ts
│   │   └── styles/
│   │       └── global.css
│   ├── public/
│   │   └── favicon.svg
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── nginx.conf            # Nginx 配置
│   └── Dockerfile            # 前端容器构建文件
│
├── docs/                      # API 参考文档
│   ├── akshare_alternative_data_api.md  # 另类数据接口详解
│   └── AKSHARE_API_REFERENCE.md        # AkShare 基金接口详解
│
├── docker-compose.yml         # Docker Compose 配置
├── .gitignore
├── start.sh                   # 快速启动脚本
├── DEPLOYMENT.md              # 详细部署文档
├── LICENSE                    # MIT 开源协议
└── README.md                  # 项目文档（本文件）
```

---

## 📊 数据源说明

所有金融数据来自开源项目 **[AkShare](https://github.com/akfamily/akshare)**，这是一个专注于提供免费金融数据接口的 Python 库。

### 主要数据接口

| 接口名称 | 功能描述 | 缓存策略 |
|---------|---------|---------|
| `fund_open_fund_info_em` | 基金基本信息 | 30分钟 |
| `fund_open_fund_daily_em` | 实时净值 | 5分钟 |
| `fund_open_fund_rank_em` | 基金排行榜 | 10分钟 |
| `fund_individual_basic_info_xq` | 雪球基金详情 | 30分钟 |
| `fund_portfolio_hold_em` | 季度持仓明细 | 6小时 |
| `fund_individual_detail_info_xq` | 行业/资产配置 | 6小时 |
| `fund_fh_em` | 历史分红 | 24小时 |
| `fund_value_estimation_em` | 实时估值 | 实时更新 |
| `car_*` / `air_*` / `movie_*` | 另类数据（25个接口） | 10分钟 |

完整接口文档参考：
- [基金数据接口](docs/AKSHARE_API_REFERENCE.md)
- [另类数据接口](docs/akshare_alternative_data_api.md)

---

## 🔧 开发指南

### 数据库管理

后端使用 SQLite 存储缓存数据，包含 **9 张缓存表**：

```bash
# 进入后端容器
docker exec -it akshare-backend bash

# 打开数据库
sqlite3 /app/db/akshare.db

# 查看所有表
.tables

# 查看缓存数据量
SELECT COUNT(*) FROM fund_net_value_history;

# 查看最新缓存时间
SELECT fund_code, cache_time FROM fund_basic_info_cache
ORDER BY cache_time DESC LIMIT 10;

# 退出
.exit
```

**数据库表说明**：
- `fund_value_estimation` - 实时估值缓存
- `fund_net_value_history` - 历史净值缓存（支持激进缓存策略）
- `fund_holdings_cache` - 持仓数据缓存
- `fund_dividend` - 分红记录缓存
- `fund_rating_all` - 基金评级缓存
- `fund_basic_info_cache` - 基本信息缓存
- `fund_daily_nav_cache` - 实时净值缓存
- `fund_ranking_cache` - 排行榜缓存
- `fund_risk_indicators_xq` - 雪球风险指标缓存

### 添加新的 API 接口

#### 后端 (FastAPI)

在 `backend/main.py` 中添加新路由：

```python
@app.get("/api/new_feature")
async def get_new_feature():
    try:
        # 调用 AkShare 接口
        df = ak.some_akshare_interface()

        # 转换为 JSON
        result = df.to_dict('records')

        return {"data": result}
    except Exception as e:
        logger.error(f"获取数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

如果需要缓存，使用 `CacheHelper`:

```python
from db.cache_helper import cache_helper

data = cache_helper.get_or_fetch(
    cache_key="new_feature_cache",
    fetch_func=lambda: ak.some_akshare_interface(),
    ttl=600  # 10分钟缓存
)
```

#### 前端 (Vue 3)

1. **添加类型定义** (`frontend/src/types/fund.ts`):
```typescript
export interface NewFeatureData {
  id: string;
  name: string;
  value: number;
}
```

2. **添加 API 调用** (`frontend/src/api/fund.ts`):
```typescript
export const fetchNewFeature = async (): Promise<NewFeatureData[]> => {
  const response = await fetch('/api/new_feature');
  const data = await response.json();
  return data.data;
};
```

3. **创建/修改页面组件** (`frontend/src/views/NewFeature.vue`):
```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { fetchNewFeature } from '@/api/fund';

const data = ref([]);

onMounted(async () => {
  data.value = await fetchNewFeature();
});
</script>

<template>
  <div>
    <h2>新功能</h2>
    <ul>
      <li v-for="item in data" :key="item.id">
        {{ item.name }}: {{ item.value }}
      </li>
    </ul>
  </div>
</template>
```

4. **添加路由** (`frontend/src/router/index.ts`):
```typescript
{
  path: '/new-feature',
  name: 'NewFeature',
  component: () => import('@/views/NewFeature.vue')
}
```

### 性能优化建议

1. **后端优化**
   - 对高频接口启用缓存（使用 `CacheHelper`）
   - 使用 APScheduler 预加载热门基金数据
   - 对慢查询添加数据库索引
   - 启用 SQLite WAL 模式（已默认开启）

2. **前端优化**
   - 使用虚拟滚动处理大列表（参考 `FundChart.vue`）
   - 图表组件按需加载（使用 `defineAsyncComponent`）
   - 实施防抖节流（搜索框、滚动事件）
   - 启用 Gzip 压缩（Nginx 已配置）

3. **网络优化**
   - 并行请求（使用 `Promise.all`）
   - 实施请求降级策略（参考 `api/fallback.ts`）
   - 合理设置缓存 TTL

---

## 🧪 测试

### 后端 API 测试

```bash
# 测试另类数据接口
docker exec -it akshare-backend python scripts/test_alternative_apis.py

# 手动测试单个接口
curl http://localhost:8080/api/fund_open_fund_info_em?symbol=000001
```

### 前端测试

```bash
cd frontend

# 运行 Lint 检查
npm run lint

# 类型检查
npm run type-check

# 构建测试
npm run build
```

---

## 📝 已知问题

| 问题描述 | 影响范围 | 状态 |
|---------|---------|------|
| AkShare `fund_rating_all` 接口报错 | 无法显示基金评级 | ⏸️ 上游问题 |
| AkShare `fund_fh_em` 响应慢 (>30s) | 分红数据加载慢 | ⏸️ 上游问题 |
| ~30% 基金无最新持仓数据 | 显示 "-" | ✅ 已兼容处理 |

---

## 📄 许可证

本项目采用 **MIT License** 开源协议，详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- **[AkShare](https://github.com/akfamily/akshare)** - 感谢提供免费的金融数据接口
- **[AKTools](https://github.com/zaihuazhao/aktools)** - AkShare HTTP 服务封装
- **[FastAPI](https://fastapi.tiangolo.com/)** - 现代化的 Python Web 框架
- **[Vue.js](https://vuejs.org/)** - 渐进式 JavaScript 框架
- **[ECharts](https://echarts.apache.org/)** - 强大的数据可视化库

---

## 📧 联系方式

- **GitHub Issues**: [提交问题](https://github.com/YOUR_USERNAME/akshare-public-fund/issues)
- **Pull Requests**: 欢迎贡献代码

---

## 🗺️ 路线图

- [ ] 支持基金定投计算器
- [ ] 添加基金经理详情页
- [ ] 实现基金回测功能
- [ ] 集成基金净值预测（AI模型）
- [ ] 支持数据库切换（PostgreSQL/MySQL）
- [ ] 移动端适配优化
- [ ] 支持国际化（英文版）

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！⭐**

Made with ❤️ by AkShare Community

</div>

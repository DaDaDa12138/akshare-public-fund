<template>
  <div class="fund-detail">
    <div class="container">
      <!-- 返回按钮 -->
      <el-button @click="goBack" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <!-- 详情内容 -->
      <div v-else-if="fundData" class="detail-content">
        <!-- 基金标题 -->
        <div class="fund-title card">
          <div class="title-content">
            <div class="title-left">
              <h1>{{ fundData.基金简称 || fundData.基金全称 }}</h1>
              <div class="fund-code">{{ route.params.code }}</div>
              <el-tag v-if="fundData.基金类型" type="info" size="large">
                {{ fundData.基金类型 }}
              </el-tag>
            </div>
            <div class="title-right">
              <el-button
                :type="favoritesStore.isFavorite(route.params.code as string) ? 'warning' : 'default'"
                :icon="favoritesStore.isFavorite(route.params.code as string) ? 'StarFilled' : 'Star'"
                @click="toggleFavorite"
                size="large"
              >
                {{ favoritesStore.isFavorite(route.params.code as string) ? '已收藏' : '收藏' }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 基本信息 -->
        <div class="info-section card">
          <h3 class="section-title">基本信息</h3>

          <!-- 核心指标区（突出显示） -->
          <div class="key-metrics">
            <!-- 净值指标 -->
            <div class="metric-group">
              <div class="metric-card">
                <div class="metric-label">单位净值</div>
                <div class="metric-value primary">
                  {{ fundData?.单位净值 || '-' }}
                </div>
                <div class="metric-sub">昨日: {{ fundData?.前一日单位净值 || '-' }}</div>
              </div>
              <div class="metric-card">
                <div class="metric-label">累计净值</div>
                <div class="metric-value primary">
                  {{ fundData?.累计净值 || '-' }}
                </div>
                <div class="metric-sub">昨日: {{ fundData?.前一日累计净值 || '-' }}</div>
              </div>
            </div>

            <!-- 涨跌指标 -->
            <div class="metric-group">
              <div class="metric-card">
                <div class="metric-label">日增长值</div>
                <div
                  class="metric-value"
                  :class="getValueColor(fundData?.日增长值)"
                >
                  {{ formatGrowthValue(fundData?.日增长值) }}
                </div>
              </div>
              <div class="metric-card">
                <div class="metric-label">日增长率</div>
                <div
                  class="metric-value"
                  :class="getValueColor(fundData?.日增长率)"
                >
                  {{ formatGrowthRate(fundData?.日增长率) }}
                </div>
              </div>
            </div>

            <!-- 实时估值 (如果有) -->
            <div class="metric-group" v-if="valueEstimation">
              <div class="metric-card">
                <div class="metric-label">实时估值</div>
                <div class="metric-value primary">
                  {{ valueEstimation.估算值 || '-' }}
                </div>
                <div class="metric-sub">{{ valueEstimation.估算时间 || '' }}</div>
              </div>
              <div class="metric-card">
                <div class="metric-label">估算涨幅</div>
                <div
                  class="metric-value"
                  :class="getEstimationColor(valueEstimation.估算增长率)"
                >
                  {{ formatEstimationRate(valueEstimation.估算增长率) }}
                </div>
                <div class="metric-sub" v-if="valueEstimation.估算偏差">
                  偏差: {{ valueEstimation.估算偏差 }}
                </div>
              </div>
            </div>
          </div>

          <!-- 详细信息区 -->
          <div class="detail-info">
            <el-row :gutter="16">
              <el-col :xs="24" :sm="12" :md="8">
                <div class="info-item">
                  <div class="info-label">基金代码</div>
                  <div class="info-value">{{ fundData?.基金代码 || '-' }}</div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8">
                <div class="info-item">
                  <div class="info-label">基金简称</div>
                  <div class="info-value">{{ fundData?.基金简称 || '-' }}</div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8">
                <div class="info-item">
                  <div class="info-label">基金类型</div>
                  <div class="info-value">{{ fundData?.基金类型 || '-' }}</div>
                </div>
              </el-col>

              <!-- 雪球数据 -->
              <el-col :xs="24" :sm="12" :md="8" v-if="getBasicInfoItem('基金经理')">
                <div class="info-item">
                  <div class="info-label">基金经理</div>
                  <div class="info-value">{{ getBasicInfoItem('基金经理') }}</div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" v-if="getBasicInfoItem('基金公司')">
                <div class="info-item">
                  <div class="info-label">基金公司</div>
                  <div class="info-value">{{ getBasicInfoItem('基金公司') }}</div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" v-if="getBasicInfoItem('最新规模')">
                <div class="info-item">
                  <div class="info-label">基金规模</div>
                  <div class="info-value">{{ getBasicInfoItem('最新规模') }}</div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" v-if="getBasicInfoItem('成立时间')">
                <div class="info-item">
                  <div class="info-label">成立日期</div>
                  <div class="info-value">{{ getBasicInfoItem('成立时间') }}</div>
                </div>
              </el-col>

              <!-- 交易状态 -->
              <el-col :xs="24" :sm="12" :md="8" v-if="fundData?.申购状态">
                <div class="info-item">
                  <div class="info-label">申购状态</div>
                  <div class="info-value">
                    <el-tag :type="fundData.申购状态 === '开放' ? 'success' : 'info'" size="small">
                      {{ fundData.申购状态 }}
                    </el-tag>
                  </div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" v-if="fundData?.赎回状态">
                <div class="info-item">
                  <div class="info-label">赎回状态</div>
                  <div class="info-value">
                    <el-tag :type="fundData.赎回状态 === '开放' ? 'success' : 'info'" size="small">
                      {{ fundData.赎回状态 }}
                    </el-tag>
                  </div>
                </div>
              </el-col>

              <!-- ETF 特殊字段 -->
              <el-col :xs="24" :sm="12" :md="8" v-if="isETF && fundData?.市价">
                <div class="info-item">
                  <div class="info-label">市价</div>
                  <div class="info-value">{{ fundData.市价 }}</div>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" v-if="isETF && fundData?.折价率">
                <div class="info-item">
                  <div class="info-label">折价率</div>
                  <div
                    class="info-value"
                    :class="getValueColor(fundData.折价率)"
                  >
                    {{ formatDiscountRate(fundData.折价率) }}
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>

        <!-- 费率信息 -->
        <div class="fee-section card">
          <h3 class="section-title">费率信息</h3>
          <el-row :gutter="16">
            <el-col :xs="24" :sm="12" :md="6" v-for="(item, key) in feeInfo" :key="key">
              <div class="fee-item">
                <div class="fee-label">{{ key }}</div>
                <div class="fee-value">{{ item }}</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 基金评级 -->
        <div class="rating-section card" v-if="fundRating">
          <h3 class="section-title">基金评级 ⭐</h3>
          <el-row :gutter="16">
            <el-col :xs="24" :sm="12" :md="6">
              <div class="rating-item">
                <div class="rating-label">5星评级家数</div>
                <div class="rating-value highlight">{{ fundRating['5星评级家数'] || 0 }} 家</div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6" v-if="fundRating.上海证券">
              <div class="rating-item">
                <div class="rating-label">上海证券</div>
                <div class="rating-value">
                  <el-rate v-model="fundRating.上海证券" disabled show-score text-color="#ff9900" />
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6" v-if="fundRating.招商证券">
              <div class="rating-item">
                <div class="rating-label">招商证券</div>
                <div class="rating-value">
                  <el-rate v-model="fundRating.招商证券" disabled show-score text-color="#ff9900" />
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6" v-if="fundRating.济安金信">
              <div class="rating-item">
                <div class="rating-label">济安金信</div>
                <div class="rating-value">
                  <el-rate v-model="fundRating.济安金信" disabled show-score text-color="#ff9900" />
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6" v-if="fundRating.晨星评级">
              <div class="rating-item">
                <div class="rating-label">晨星评级</div>
                <div class="rating-value">
                  <el-rate v-model="fundRating.晨星评级" disabled show-score text-color="#ff9900" />
                </div>
              </div>
            </el-col>
          </el-row>
          <div class="rating-note">
            💡 评级数据来自东方财富,星级越高代表综合评价越好
          </div>
        </div>

        <!-- 基金分红记录 -->
        <div class="dividend-section card" v-if="dividendData.length > 0">
          <h3 class="section-title">分红记录 💰</h3>

          <!-- 分红统计信息 -->
          <div class="dividend-stats">
            <div class="stat-item">
              <div class="stat-label">累计分红</div>
              <div class="stat-value">{{ dividendStats.total.toFixed(4) }} 元</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">分红次数</div>
              <div class="stat-value">{{ dividendStats.count }} 次</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">平均分红</div>
              <div class="stat-value">{{ dividendStats.average.toFixed(4) }} 元</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">最大分红</div>
              <div class="stat-value">{{ dividendStats.max.toFixed(4) }} 元</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">最近分红</div>
              <div class="stat-value">{{ dividendStats.latest }}</div>
            </div>
          </div>

          <!-- 分红趋势图表 -->
          <div class="dividend-chart-container" v-if="dividendData.length > 1">
            <div ref="dividendChartRef" class="dividend-chart"></div>
          </div>

          <!-- 年份筛选 -->
          <div class="dividend-filter">
            <el-radio-group v-model="selectedYear" size="small">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button v-for="year in dividendYears" :key="year" :label="year">{{ year }}</el-radio-button>
            </el-radio-group>
            <el-button size="small" type="primary" plain @click="exportDividendData" style="margin-left: 10px">
              <i class="el-icon-download"></i> 导出Excel
            </el-button>
          </div>

          <!-- 分红数据表格 -->
          <el-table :data="filteredDividendData" stripe style="width: 100%" max-height="400">
            <el-table-column prop="除息日期" label="除息日期" width="120" sortable />
            <el-table-column prop="分红" label="每份分红(元)" width="130" align="right" sortable>
              <template #default="scope">
                <span class="dividend-amount">{{ scope.row.分红?.toFixed(4) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="权益登记日" label="权益登记日" width="120" />
            <el-table-column prop="分红发放日" label="分红发放日" width="120" />
          </el-table>

          <div class="dividend-note">
            💡 数据来源：东方财富，每周自动更新一次 | 共 {{ filteredDividendData.length }} 条记录
          </div>
        </div>

        <!-- 持仓信息 -->
        <div class="holding-section card" v-if="allHoldings.length > 0">
          <div class="section-header">
            <h3 class="section-title">股票持仓明细</h3>
            <!-- 持仓集中度统计 -->
            <div v-if="holdingsStats" class="holdings-stats">
              <el-tag type="info" size="large">总持仓数: {{ holdingsStats.总持仓数 }}</el-tag>
              <el-tag type="warning" size="large">TOP10集中度: {{ holdingsStats.TOP10集中度 }}</el-tag>
              <el-tag type="success" size="large">TOP20集中度: {{ holdingsStats.TOP20集中度 }}</el-tag>
              <el-tag type="primary" size="large">持仓总市值: {{ holdingsStats.持仓总市值 }}</el-tag>
            </div>
          </div>

          <el-table :data="displayedHoldings" stripe style="width: 100%">
            <el-table-column type="index" label="排名" width="70" align="center" />
            <el-table-column prop="股票代码" label="股票代码" width="100" />
            <el-table-column prop="股票名称" label="股票名称" min-width="120" />
            <el-table-column prop="占净值比例" label="占净值比例" width="110" align="right">
              <template #default="{ row }">
                <span class="percentage">{{ row.占净值比例 }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="持股数" label="持股数(万股)" width="120" align="right">
              <template #default="{ row }">
                <span>{{ row.持股数 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="持仓市值" label="持仓市值(万元)" width="130" align="right">
              <template #default="{ row }">
                <span>{{ row.持仓市值 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="季度" label="季度" min-width="180" />
          </el-table>

          <!-- 显示更多按钮 -->
          <div class="load-more-section" v-if="allHoldings.length > holdingsLimit">
            <el-button-group>
              <el-button
                @click="holdingsLimit = 10"
                :type="holdingsLimit === 10 ? 'primary' : ''"
              >
                TOP 10
              </el-button>
              <el-button
                @click="holdingsLimit = 20"
                :type="holdingsLimit === 20 ? 'primary' : ''"
              >
                TOP 20
              </el-button>
              <el-button
                @click="holdingsLimit = 50"
                :type="holdingsLimit === 50 ? 'primary' : ''"
              >
                TOP 50
              </el-button>
              <el-button
                @click="holdingsLimit = allHoldings.length"
                :type="holdingsLimit === allHoldings.length ? 'primary' : ''"
              >
                全部 ({{ allHoldings.length }})
              </el-button>
            </el-button-group>
          </div>
        </div>

        <!-- 债券持仓明细 -->
        <div class="bond-holding-section card" v-if="bondHoldings.length > 0">
          <div class="section-header">
            <h3 class="section-title">债券持仓明细</h3>
            <div class="bond-holdings-controls">
              <!-- 季度选择器 -->
              <el-select
                v-model="selectedBondQuarter"
                placeholder="选择季度"
                size="default"
                style="width: 220px"
                @change="handleBondQuarterChange"
              >
                <el-option
                  v-for="quarter in bondQuarters"
                  :key="quarter"
                  :label="quarter.replace('债券投资明细', '')"
                  :value="quarter"
                />
              </el-select>
              <!-- 统计信息 -->
              <div v-if="bondHoldingsStats" class="bond-stats">
                <el-tag type="info" size="large">持仓数: {{ bondHoldingsStats.总持仓数 }}</el-tag>
                <el-tag type="warning" size="large">TOP5占比: {{ bondHoldingsStats.TOP5占比 }}</el-tag>
                <el-tag type="primary" size="large">总市值: {{ bondHoldingsStats.总市值 }}</el-tag>
              </div>
            </div>
          </div>

          <el-table :data="displayedBondHoldings" stripe style="width: 100%">
            <el-table-column type="index" label="排名" width="70" align="center" />
            <el-table-column prop="债券代码" label="债券代码" width="120" />
            <el-table-column prop="债券名称" label="债券名称" min-width="150" />
            <el-table-column prop="占净值比例" label="占净值比例" width="120" align="right">
              <template #default="{ row }">
                <span class="percentage">{{ row.占净值比例.toFixed(2) }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="持仓市值" label="持仓市值(万元)" width="140" align="right">
              <template #default="{ row }">
                <span>{{ row.持仓市值.toFixed(2) }}</span>
              </template>
            </el-table-column>
          </el-table>

          <!-- 显示更多按钮 -->
          <div class="load-more-section" v-if="filteredBondHoldings.length > bondHoldingsLimit">
            <el-button-group>
              <el-button
                @click="bondHoldingsLimit = 5"
                :type="bondHoldingsLimit === 5 ? 'primary' : ''"
              >
                TOP 5
              </el-button>
              <el-button
                @click="bondHoldingsLimit = 10"
                :type="bondHoldingsLimit === 10 ? 'primary' : ''"
              >
                TOP 10
              </el-button>
              <el-button
                @click="bondHoldingsLimit = filteredBondHoldings.length"
                :type="bondHoldingsLimit === filteredBondHoldings.length ? 'primary' : ''"
              >
                全部 ({{ filteredBondHoldings.length }})
              </el-button>
            </el-button-group>
          </div>

          <div class="bond-note">
            💡 数据来源：东方财富季度报告 | 自动缓存加速
          </div>
        </div>

        <!-- 重仓股票持仓（东方财富） -->
        <div class="portfolio-hold-section card" v-if="portfolioHoldData.length > 0">
          <h3 class="section-title">📊 重仓股票持仓（东方财富）</h3>

          <el-table :data="displayedPortfolioHold" stripe style="width: 100%">
            <el-table-column type="index" label="序号" width="70" align="center" />
            <el-table-column prop="股票代码" label="股票代码" width="100" align="center" />
            <el-table-column prop="股票名称" label="股票名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="占净值比例" label="占净值比例" width="120" align="right" sortable>
              <template #default="{ row }">
                <span class="percentage-value">{{ row.占净值比例.toFixed(2) }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="持股数" label="持股数(万股)" width="130" align="right">
              <template #default="{ row }">
                <span>{{ row.持股数.toLocaleString() }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="持仓市值" label="持仓市值(万元)" width="140" align="right">
              <template #default="{ row }">
                <span>{{ row.持仓市值.toLocaleString() }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="季度" label="季度" width="180" align="center" />
          </el-table>

          <div class="portfolio-actions" v-if="portfolioHoldData.length > 10">
            <el-button
              type="primary"
              text
              @click="portfolioHoldExpanded = !portfolioHoldExpanded"
            >
              {{ portfolioHoldExpanded ? '收起' : `查看全部 (${portfolioHoldData.length}条)` }}
              <el-icon><component :is="portfolioHoldExpanded ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
            </el-button>
          </div>

          <div class="portfolio-note">
            💡 数据来源：东方财富 | 最近一个季度的重仓股票数据
          </div>
        </div>

        <!-- 持仓变动（东方财富） -->
        <div class="portfolio-change-section card" v-if="portfolioChangeData.length > 0">
          <h3 class="section-title">🔄 持仓变动明细（东方财富）</h3>

          <el-table :data="displayedPortfolioChange" stripe style="width: 100%">
            <el-table-column type="index" label="序号" width="70" align="center" />
            <el-table-column prop="股票代码" label="股票代码" width="100" align="center" />
            <el-table-column prop="股票名称" label="股票名称" min-width="150" show-overflow-tooltip />
            <el-table-column prop="本期累计买入金额" label="买入金额(万元)" width="140" align="right" sortable>
              <template #default="{ row }">
                <span class="buy-amount">{{ row.本期累计买入金额.toLocaleString() }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="占期初基金资产净值比例" label="占净值比例" width="120" align="right" sortable>
              <template #default="{ row }">
                <span class="percentage-value">{{ row.占期初基金资产净值比例.toFixed(2) }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="季度" label="季度" width="180" align="center" />
          </el-table>

          <div class="portfolio-actions" v-if="portfolioChangeData.length > 10">
            <el-button
              type="primary"
              text
              @click="portfolioChangeExpanded = !portfolioChangeExpanded"
            >
              {{ portfolioChangeExpanded ? '收起' : `查看全部 (${portfolioChangeData.length}条)` }}
              <el-icon><component :is="portfolioChangeExpanded ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
            </el-button>
          </div>

          <div class="portfolio-note">
            💡 数据来源：东方财富 | 显示本期累计买入的股票及金额
          </div>
        </div>

        <!-- 收益率统计 -->
        <div class="return-rate-section card">
          <h3 class="section-title">收益率统计</h3>
          <div class="return-rate-grid">
            <div
              v-for="item in returnRates"
              :key="item.period"
              class="return-rate-item"
            >
              <div class="rate-period">{{ item.period }}</div>
              <div class="rate-value" v-if="item.loading">
                <el-icon class="is-loading"><Loading /></el-icon>
              </div>
              <div
                v-else-if="item.rate !== null"
                class="rate-value"
                :class="{
                  'rate-positive': item.rate > 0,
                  'rate-negative': item.rate < 0,
                  'rate-neutral': item.rate === 0
                }"
              >
                {{ item.rate > 0 ? '+' : '' }}{{ item.rate.toFixed(2) }}%
              </div>
              <div v-else class="rate-value rate-unavailable">-</div>
            </div>
          </div>
        </div>

        <!-- 业绩与风险分析 -->
        <div class="performance-section card">
          <h3 class="section-title">业绩与风险分析</h3>
          <div v-if="metricsLoading" class="metrics-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在计算指标...</span>
          </div>
          <div v-else class="metrics-grid">
            <!-- 最大回撤 -->
            <div class="metric-item">
              <div class="metric-label">最大回撤</div>
              <div class="metric-value" v-if="performanceMetrics.最大回撤 !== null">
                <span class="value-negative">-{{ performanceMetrics.最大回撤.toFixed(2) }}%</span>
              </div>
              <div class="metric-value" v-else>-</div>
              <div class="metric-desc">历史最大跌幅</div>
            </div>

            <!-- 年化收益率 -->
            <div class="metric-item">
              <div class="metric-label">年化收益率</div>
              <div class="metric-value" v-if="performanceMetrics.年化收益率 !== null">
                <span :class="{
                  'value-positive': performanceMetrics.年化收益率 > 0,
                  'value-negative': performanceMetrics.年化收益率 < 0
                }">
                  {{ performanceMetrics.年化收益率 > 0 ? '+' : '' }}{{ performanceMetrics.年化收益率.toFixed(2) }}%
                </span>
              </div>
              <div class="metric-value" v-else>-</div>
              <div class="metric-desc">成立以来年化</div>
            </div>

            <!-- 波动率 -->
            <div class="metric-item">
              <div class="metric-label">波动率</div>
              <div class="metric-value" v-if="performanceMetrics.波动率 !== null">
                <span>{{ performanceMetrics.波动率.toFixed(2) }}%</span>
              </div>
              <div class="metric-value" v-else>-</div>
              <div class="metric-desc">年化标准差</div>
            </div>

            <!-- 夏普比率 -->
            <div class="metric-item">
              <div class="metric-label">夏普比率</div>
              <div class="metric-value" v-if="performanceMetrics.夏普比率 !== null">
                <span :class="{
                  'value-positive': performanceMetrics.夏普比率 > 1,
                  'value-warning': performanceMetrics.夏普比率 <= 1 && performanceMetrics.夏普比率 > 0,
                  'value-negative': performanceMetrics.夏普比率 <= 0
                }">
                  {{ performanceMetrics.夏普比率.toFixed(2) }}
                </span>
              </div>
              <div class="metric-value" v-else>-</div>
              <div class="metric-desc">风险调整收益</div>
            </div>
          </div>

          <!-- 指标说明 -->
          <div class="metrics-note">
            <el-tag size="small" type="info">最大回撤越小越好</el-tag>
            <el-tag size="small" type="info">波动率越小风险越低</el-tag>
            <el-tag size="small" type="info">夏普比率 &gt; 1 表现较好</el-tag>
          </div>

          <!-- 雪球风险指标详情表格 -->
          <div v-if="xqAnalysisData.length > 0" class="xq-analysis-table" style="margin-top: 20px;">
            <h4 style="margin-bottom: 10px; font-size: 14px; color: #606266;">
              多周期风险指标对比
              <el-tag size="small" type="success" style="margin-left: 8px;">雪球数据</el-tag>
            </h4>
            <el-table :data="xqAnalysisData" size="small" stripe border>
              <el-table-column prop="周期" label="周期" width="100" align="center" />
              <el-table-column prop="年化波动率" label="年化波动率" width="120" align="center">
                <template #default="scope">
                  <span v-if="scope.row.年化波动率 !== null && scope.row.年化波动率 !== undefined">
                    {{ scope.row.年化波动率.toFixed(2) }}%
                  </span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="年化夏普比率" label="年化夏普比率" width="120" align="center">
                <template #default="scope">
                  <span v-if="scope.row.年化夏普比率 !== null && scope.row.年化夏普比率 !== undefined"
                    :class="{
                      'value-positive': scope.row.年化夏普比率 > 1,
                      'value-warning': scope.row.年化夏普比率 <= 1 && scope.row.年化夏普比率 > 0,
                      'value-negative': scope.row.年化夏普比率 <= 0
                    }">
                    {{ scope.row.年化夏普比率.toFixed(2) }}
                  </span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="最大回撤" label="最大回撤" width="120" align="center">
                <template #default="scope">
                  <span v-if="scope.row.最大回撤 !== null && scope.row.最大回撤 !== undefined" class="value-negative">
                    {{ scope.row.最大回撤.toFixed(2) }}%
                  </span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="较同类风险收益比" label="较同类风险收益比" width="140" align="center">
                <template #default="scope">
                  <span v-if="scope.row.较同类风险收益比 !== null && scope.row.较同类风险收益比 !== undefined">
                    {{ scope.row.较同类风险收益比.toFixed(0) }}%
                  </span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="较同类抗风险波动" label="较同类抗风险波动" width="140" align="center">
                <template #default="scope">
                  <span v-if="scope.row.较同类抗风险波动 !== null && scope.row.较同类抗风险波动 !== undefined">
                    {{ scope.row.较同类抗风险波动.toFixed(0) }}%
                  </span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
            </el-table>
            <div style="margin-top: 8px; font-size: 12px; color: #909399;">
              <el-icon><InfoFilled /></el-icon>
              较同类百分比：数值越大表示在同类基金中排名越靠前
            </div>
          </div>
        </div>

        <!-- 行业分布 -->
        <div v-if="industryData.length > 0" class="industry-section card">
          <h3 class="section-title">行业分布（TOP10）</h3>
          <div ref="industryChartRef" class="industry-chart"></div>
        </div>

        <!-- 资产配置 -->
        <div v-if="assetAllocation.length > 0" class="asset-section card">
          <h3 class="section-title">资产配置</h3>
          <div ref="assetChartRef" class="asset-chart"></div>
        </div>

        <!-- 净值走势 -->
        <div class="chart-section card">
          <h3 class="section-title">净值走势</h3>
          <div ref="chartRef" class="mini-chart"></div>
        </div>

        <!-- 历史净值完整数据（新增） -->
        <div v-if="netValueHistory.length > 0" class="net-value-history-section card">
          <h3 class="section-title">历史净值完整数据</h3>

          <!-- 指标类型切换 -->
          <div class="indicator-selector">
            <el-radio-group v-model="selectedIndicator" @change="changeIndicator">
              <el-radio-button label="单位净值走势">单位净值</el-radio-button>
              <el-radio-button label="累计净值走势">累计净值</el-radio-button>
              <el-radio-button label="累计收益率走势">累计收益率</el-radio-button>
              <el-radio-button label="同类排名走势">同类排名</el-radio-button>
              <el-radio-button label="同类排名百分比">同类排名%</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 时间范围选择器（新增） -->
          <div class="timerange-selector">
            <span class="selector-label">时间范围:</span>
            <el-radio-group v-model="selectedTimeRange" size="small" @change="updateNetValueChart">
              <el-radio-button label="1M">近1月</el-radio-button>
              <el-radio-button label="3M">近3月</el-radio-button>
              <el-radio-button label="6M">近6月</el-radio-button>
              <el-radio-button label="1Y">近1年</el-radio-button>
              <el-radio-button label="ALL">全部</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 历史净值图表 -->
          <div ref="netValueHistoryChartRef" class="net-value-history-chart"></div>

          <!-- 数据统计 -->
          <div class="data-stats">
            <el-row :gutter="16">
              <el-col :xs="12" :sm="6">
                <div class="stat-item">
                  <div class="stat-label">数据总量</div>
                  <div class="stat-value">{{ netValueHistory.length }} 条</div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="6">
                <div class="stat-item">
                  <div class="stat-label">起始日期</div>
                  <div class="stat-value">{{ netValueHistory[netValueHistory.length - 1]?.净值日期 }}</div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="6">
                <div class="stat-item">
                  <div class="stat-label">最新日期</div>
                  <div class="stat-value">{{ filteredNetValueHistory[0]?.净值日期 }}</div>
                </div>
              </el-col>
              <el-col :xs="12" :sm="6">
                <div class="stat-item">
                  <div class="stat-label">数据来源</div>
                  <div class="stat-value">东方财富网</div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 数据表格 -->
          <el-table
            :data="paginatedNetValueHistory"
            stripe
            style="width: 100%; margin-top: 16px"
            max-height="500"
          >
            <el-table-column prop="净值日期" label="净值日期" width="120" fixed />
            <el-table-column v-if="selectedIndicator === '单位净值走势'" prop="单位净值" label="单位净值" width="120">
              <template #default="{ row }">
                {{ row.单位净值?.toFixed(4) || '-' }}
              </template>
            </el-table-column>
            <el-table-column v-if="selectedIndicator === '累计净值走势'" prop="累计净值" label="累计净值" width="120">
              <template #default="{ row }">
                {{ row.累计净值?.toFixed(4) || '-' }}
              </template>
            </el-table-column>
            <el-table-column v-if="selectedIndicator === '累计收益率走势'" prop="累计收益率" label="累计收益率(%)" width="140">
              <template #default="{ row }">
                {{ row.累计收益率?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column v-if="selectedIndicator === '同类排名走势'" prop="同类排名" label="同类排名" width="120">
              <template #default="{ row }">
                {{ row.同类排名 || '-' }}
              </template>
            </el-table-column>
            <el-table-column v-if="selectedIndicator === '同类排名百分比'" prop="同类排名百分比" label="同类排名百分比(%)" width="160">
              <template #default="{ row }">
                {{ row.同类排名百分比?.toFixed(2) || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="日增长率" label="日增长率" width="120">
              <template #default="{ row }">
                <span :style="{ color: row.日增长率 > 0 ? '#f56c6c' : row.日增长率 < 0 ? '#67c23a' : '#909399' }">
                  {{ row.日增长率 !== undefined && row.日增长率 !== null ? row.日增长率.toFixed(2) + '%' : '-' }}
                </span>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页器 -->
          <el-pagination
            v-if="filteredNetValueHistory.length > 0"
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            :total="filteredNetValueHistory.length"
            layout="total, sizes, prev, pager, next, jumper"
            style="margin-top: 16px; justify-content: center;"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button type="primary" size="large" @click="viewFullChart">
            查看完整走势图
          </el-button>
        </div>

        <!-- 增强信息：申购赎回状态、基金评级、分红历史 -->
        <FundEnhancedInfo :fund-code="route.params.code as string" />
      </div>

      <!-- 错误状态 -->
      <div v-else class="error-state card">
        <el-result
          icon="warning"
          title="加载失败"
          sub-title="无法获取基金详情，请稍后重试"
        >
          <template #extra>
            <el-button type="primary" @click="loadData">重新加载</el-button>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFundStore } from '@/stores/fund'
import { useFavoritesStore } from '@/stores/favorites'
import FundEnhancedInfo from '@/components/FundEnhancedInfo.vue'
import {
  getFundHoldings,
  getFundHistData,
  getFundDailyData,
  getETFFundDaily,
  getFundBasicInfoXQ,
  getFundAnalysisXQ,
  getFundRiskIndicators,
  getFundIndustryAllocation,
  getFundAssetAllocationXQ,
  getFundValueEstimation,
  getFundRating,
  getFundDividend,
  getFundBondHoldings,
  getFundPortfolioHold,
  getFundPortfolioChange,
  getFundNetValueHistory
} from '@/api/fund'
import { ArrowLeft, Loading, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import type {
  FundOverview,
  FundHolding,
  FundBasicInfoXQ,
  FundAnalysisXQ,
  IndustryAllocation,
  AssetAllocationXQ,
  FundValueEstimation,
  FundRating,
  FundDividend,
  FundNetValueHistoryRecord,
  FundRiskIndicator
} from '@/types/fund'

const route = useRoute()
const router = useRouter()
const favoritesStore = useFavoritesStore()

// 请求控制器(用于取消进行中的请求)
let abortController: AbortController | null = null

// 状态
const loading = ref(false)
const fundData = ref<FundOverview | null>(null)
const holdings = ref<FundHolding[]>([])
const allHoldings = ref<FundHolding[]>([])  // 全部持仓数据
const holdingsLimit = ref(10)  // 显示的持仓数量
const chartRef = ref<HTMLElement>()
let chartInstance: ECharts | null = null

// 雪球数据（基本信息是 key-value 对数组）
const basicInfoXQ = ref<FundBasicInfoXQ[]>([])
const industryData = ref<IndustryAllocation[]>([])
const assetAllocation = ref<AssetAllocationXQ[]>([])

// 实时估值
const valueEstimation = ref<FundValueEstimation | null>(null)

// 债券持仓数据
interface BondHoldingData {
  序号: number
  债券代码: string
  债券名称: string
  占净值比例: number
  持仓市值: number
  季度: string
}
const bondHoldings = ref<BondHoldingData[]>([])
const bondQuarters = ref<string[]>([])
const selectedBondQuarter = ref<string>('')
const bondHoldingsLimit = ref(10)

// 持仓分析数据（来自东方财富）
import type { FundPortfolioHoldData, FundPortfolioChangeData } from '@/api/fund'
const portfolioHoldData = ref<FundPortfolioHoldData[]>([])  // 重仓股票持仓
const portfolioChangeData = ref<FundPortfolioChangeData[]>([])  // 持仓变动
const portfolioHoldExpanded = ref(false)  // 重仓股票持仓展开状态
const portfolioChangeExpanded = ref(false)  // 持仓变动展开状态

// 控制显示数量的计算属性
const displayedPortfolioHold = computed(() => {
  if (portfolioHoldExpanded.value) {
    return portfolioHoldData.value
  }
  return portfolioHoldData.value.slice(0, 10)
})

const displayedPortfolioChange = computed(() => {
  if (portfolioChangeExpanded.value) {
    return portfolioChangeData.value
  }
  return portfolioChangeData.value.slice(0, 10)
})

// 图表引用
const industryChartRef = ref<HTMLElement>()
const assetChartRef = ref<HTMLElement>()
const dividendChartRef = ref<HTMLElement>()
let industryChartInstance: ECharts | null = null
let assetChartInstance: ECharts | null = null
let dividendChartInstance: ECharts | null = null

// 收益率数据
interface ReturnRateData {
  period: string
  rate: number | null
  loading: boolean
}
const returnRates = ref<ReturnRateData[]>([
  { period: '近1月', rate: null, loading: false },
  { period: '近3月', rate: null, loading: false },
  { period: '近6月', rate: null, loading: false },
  { period: '近1年', rate: null, loading: false },
  { period: '近3年', rate: null, loading: false },
  { period: '今年来', rate: null, loading: false },
  { period: '成立来', rate: null, loading: false }
])

// 检测是否为场内基金
const isETF = computed(() => {
  if (!fundData.value) return false
  const type = fundData.value.基金类型 || ''
  const name = fundData.value.基金简称 || ''
  return (
    type.includes('ETF') ||
    type.includes('LOF') ||
    type.includes('场内') ||
    name.includes('ETF') ||
    name.includes('LOF')
  )
})

// 业绩和风险指标
interface PerformanceMetrics {
  最大回撤: number | null
  年化收益率: number | null
  波动率: number | null
  夏普比率: number | null
  贝塔系数: number | null
}
const performanceMetrics = ref<PerformanceMetrics>({
  最大回撤: null,
  年化收益率: null,
  波动率: null,
  夏普比率: null,
  贝塔系数: null
})
const metricsLoading = ref(false)

// 雪球风险指标（来自API）
const xqAnalysisData = ref<FundAnalysisXQ[]>([])

// 基金评级
const fundRating = ref<FundRating | null>(null)

// 基金分红记录
const dividendData = ref<FundDividend[]>([])

// 历史净值数据
const netValueHistory = ref<FundNetValueHistoryRecord[]>([])
const netValueHistoryChartRef = ref<HTMLElement>()
let netValueHistoryChartInstance: ECharts | null = null
const selectedIndicator = ref<string>('单位净值走势')  // 当前选择的净值类型
const selectedTimeRange = ref<string>("ALL")  // 时间范围选择，默认显示全部数据

// 表格分页
const currentPage = ref(1)
const pageSize = ref(20)

// 根据时间范围过滤历史净值数据（必须在 paginatedNetValueHistory 之前定义）
const filteredNetValueHistory = computed(() => {
  if (selectedTimeRange.value === "ALL" || netValueHistory.value.length === 0) {
    return netValueHistory.value
  }

  const now = new Date()
  const cutoffDate = new Date()

  switch (selectedTimeRange.value) {
    case "1M":
      cutoffDate.setMonth(now.getMonth() - 1)
      break
    case "3M":
      cutoffDate.setMonth(now.getMonth() - 3)
      break
    case "6M":
      cutoffDate.setMonth(now.getMonth() - 6)
      break
    case "1Y":
      cutoffDate.setFullYear(now.getFullYear() - 1)
      break
  }

  return netValueHistory.value.filter(item => {
    const itemDate = new Date(item.净值日期)
    return itemDate >= cutoffDate
  })
})

// 分页后的历史净值数据
const paginatedNetValueHistory = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredNetValueHistory.value.slice(start, end)
})

// 分页事件处理函数
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1  // 重置到第一页
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

// 当过滤条件改变时，重置页码到第一页
watch(selectedTimeRange, () => {
  currentPage.value = 1
})

const dividendLoading = ref(false)
const selectedYear = ref<string>('all')  // 年份筛选

// 分红统计数据（计算属性）
const dividendStats = computed(() => {
  if (dividendData.value.length === 0) {
    return {
      total: 0,
      count: 0,
      average: 0,
      max: 0,
      latest: '-'
    }
  }

  const dividends = dividendData.value.map(d => d.分红 || 0)
  const total = dividends.reduce((sum, val) => sum + val, 0)
  const count = dividends.length
  const average = count > 0 ? total / count : 0
  const max = Math.max(...dividends)

  // 找到最近的分红日期
  const latestRecord = dividendData.value.reduce((latest, current) => {
    const currentDate = current.除息日期 || ''
    const latestDate = latest.除息日期 || ''
    return currentDate > latestDate ? current : latest
  }, dividendData.value[0])

  return {
    total,
    count,
    average,
    max,
    latest: latestRecord?.除息日期 || '-'
  }
})

// 提取所有分红年份（计算属性）
const dividendYears = computed(() => {
  if (dividendData.value.length === 0) return []

  const years = new Set<string>()
  dividendData.value.forEach(d => {
    if (d.除息日期) {
      const year = d.除息日期.substring(0, 4)
      years.add(year)
    }
  })

  return Array.from(years).sort((a, b) => b.localeCompare(a))  // 降序排列
})

// 按年份筛选分红数据（计算属性）
const filteredDividendData = computed(() => {
  if (selectedYear.value === 'all') {
    return dividendData.value
  }

  return dividendData.value.filter(d => {
    if (!d.除息日期) return false
    return d.除息日期.startsWith(selectedYear.value)
  })
})

// 监听筛选数据变化，重新渲染图表
watch(filteredDividendData, () => {
  nextTick(() => {
    renderDividendChart()
  })
})

// 监听图表容器ref变化，确保首次渲染
watch(dividendChartRef, (newVal) => {
  if (newVal && filteredDividendData.value.length > 0) {
    nextTick(() => {
      renderDividendChart()
      console.log('[基金分红] 图表容器就绪，执行首次渲染')
    })
  }
})

// 基本信息
const basicInfo = computed(() => {
  if (!fundData.value) return {}

  const info: Record<string, any> = {}

  // 基础信息
  if (fundData.value.基金全称) info['基金全称'] = fundData.value.基金全称
  if (fundData.value.基金代码) info['基金代码'] = fundData.value.基金代码
  if (fundData.value.基金类型) info['基金类型'] = fundData.value.基金类型

  // 最新净值数据
  if (fundData.value.单位净值) {
    info['单位净值（今日）'] = fundData.value.单位净值
  }
  if (fundData.value.累计净值) {
    info['累计净值（今日）'] = fundData.value.累计净值
  }

  // 前一日净值数据（用于对比）
  if (fundData.value.前一日单位净值) {
    info['单位净值（昨日）'] = fundData.value.前一日单位净值
  }
  if (fundData.value.前一日累计净值) {
    info['累计净值（昨日）'] = fundData.value.前一日累计净值
  }

  // 涨跌数据
  if (fundData.value.日增长值) {
    const value = parseFloat(fundData.value.日增长值)
    info['日增长值'] = value >= 0 ? `+${value}元` : `${value}元`
  }
  if (fundData.value.日增长率) {
    const rate = parseFloat(fundData.value.日增长率)
    info['日增长率'] = rate >= 0 ? `+${rate}%` : `${rate}%`
  }

  // 实时估值（来自数据库）
  if (valueEstimation.value) {
    if (valueEstimation.value.估算值) {
      info['实时估值'] = valueEstimation.value.估算值
    }
    if (valueEstimation.value.估算增长率) {
      // 估算增长率已包含 %，直接使用
      const rateStr = valueEstimation.value.估算增长率
      const rate = parseFloat(rateStr)
      info['估算涨幅'] = rate >= 0 ? `+${rateStr}` : rateStr
    }
    if (valueEstimation.value.估算时间) {
      info['估算时间'] = valueEstimation.value.估算时间
    }
    if (valueEstimation.value.估算偏差) {
      info['估算偏差'] = valueEstimation.value.估算偏差
    }
  }

  // 交易状态
  if (fundData.value.申购状态) info['申购状态'] = fundData.value.申购状态
  if (fundData.value.赎回状态) info['赎回状态'] = fundData.value.赎回状态

  // 场内基金特殊字段
  if (isETF.value) {
    if (fundData.value.市价) {
      info['市价'] = fundData.value.市价
    }
    if (fundData.value.折价率) {
      const discountRate = parseFloat(fundData.value.折价率)
      info['折价率'] = discountRate >= 0 ? `+${discountRate}%` : `${discountRate}%`
    }
  }

  // 雪球数据（基金经理、公司、规模）
  // 从 key-value 对数组中提取信息
  if (basicInfoXQ.value && basicInfoXQ.value.length > 0) {
    const findItem = (itemName: string) => {
      const item = basicInfoXQ.value.find(kv => kv.item === itemName)
      return item?.value
    }

    const manager = findItem('基金经理')
    const company = findItem('基金公司')
    const scale = findItem('最新规模')
    const establishDate = findItem('成立时间')

    if (manager) info['基金经理'] = manager
    if (company) info['基金公司'] = company
    if (scale) info['基金规模'] = scale
    if (establishDate) info['成立日期'] = establishDate
  }

  return info
})

// 费率信息
const feeInfo = computed(() => {
  if (!fundData.value) return {}

  const info: Record<string, any> = {}

  // 只显示有值的字段
  if (fundData.value.手续费) {
    info['手续费'] = fundData.value.手续费
  }

  // 如果没有任何费率信息，返回提示
  if (Object.keys(info).length === 0) {
    info['提示'] = '详细费率信息请访问基金公司官网查询'
  }

  return info
})

// 辅助函数:从雪球数据中获取指定项
const getBasicInfoItem = (itemName: string) => {
  if (!basicInfoXQ.value || basicInfoXQ.value.length === 0) return null
  const item = basicInfoXQ.value.find(kv => kv.item === itemName)
  return item?.value || null
}

// 辅助函数:根据数值返回颜色类名(红涨绿跌)
const getValueColor = (value: any) => {
  if (!value) return ''
  const numValue = parseFloat(String(value).replace(/[+%元]/g, ''))
  if (isNaN(numValue)) return ''
  if (numValue > 0) return 'positive'  // 红色
  if (numValue < 0) return 'negative'  // 绿色
  return ''
}

// 辅助函数:根据估算增长率返回颜色类名
const getEstimationColor = (value: any) => {
  if (!value) return ''
  const numValue = parseFloat(String(value).replace(/[+%]/g, ''))
  if (isNaN(numValue)) return ''
  if (numValue > 0) return 'positive'  // 红色
  if (numValue < 0) return 'negative'  // 绿色
  return ''
}

// 格式化增长值
const formatGrowthValue = (value: any) => {
  if (!value) return '-'
  const numValue = parseFloat(String(value))
  if (isNaN(numValue)) return value
  return numValue >= 0 ? `+${numValue}元` : `${numValue}元`
}

// 格式化增长率
const formatGrowthRate = (value: any) => {
  if (!value) return '-'
  const numValue = parseFloat(String(value))
  if (isNaN(numValue)) return value
  return numValue >= 0 ? `+${numValue}%` : `${numValue}%`
}

// 格式化估算涨幅
const formatEstimationRate = (value: any) => {
  if (!value) return '-'
  // 估算增长率已经包含百分号,直接处理符号
  const numValue = parseFloat(String(value).replace(/%/g, ''))
  if (isNaN(numValue)) return value
  return numValue >= 0 ? `+${value}` : value
}

// 格式化折价率
const formatDiscountRate = (value: any) => {
  if (!value) return '-'
  const numValue = parseFloat(String(value))
  if (isNaN(numValue)) return value
  return numValue >= 0 ? `+${numValue}%` : `${numValue}%`
}

// 持仓集中度分析
const holdingsStats = computed(() => {
  if (allHoldings.value.length === 0) return null

  const top10 = allHoldings.value.slice(0, 10)
  const top20 = allHoldings.value.slice(0, 20)

  // 计算集中度
  const top10Ratio = top10.reduce((sum, h) => sum + (parseFloat(h.占净值比例) || 0), 0)
  const top20Ratio = top20.reduce((sum, h) => sum + (parseFloat(h.占净值比例) || 0), 0)

  // 计算总市值
  const totalMarketValue = allHoldings.value.reduce((sum, h) => sum + (parseFloat(h.持仓市值) || 0), 0)

  return {
    总持仓数: allHoldings.value.length,
    TOP10集中度: top10Ratio.toFixed(2) + '%',
    TOP20集中度: top20Ratio.toFixed(2) + '%',
    持仓总市值: totalMarketValue.toFixed(2) + '万元'
  }
})

// 显示的持仓数据（根据limit）
const displayedHoldings = computed(() => {
  return allHoldings.value.slice(0, holdingsLimit.value)
})

// 债券持仓按季度过滤
const filteredBondHoldings = computed(() => {
  if (!selectedBondQuarter.value || bondHoldings.value.length === 0) {
    return bondHoldings.value
  }
  return bondHoldings.value.filter(h => h.季度 === selectedBondQuarter.value)
})

// 显示的债券持仓数据
const displayedBondHoldings = computed(() => {
  return filteredBondHoldings.value.slice(0, bondHoldingsLimit.value)
})

// 债券持仓统计信息
const bondHoldingsStats = computed(() => {
  if (filteredBondHoldings.value.length === 0) return null

  const holdings = filteredBondHoldings.value
  const top5Ratio = holdings.slice(0, 5).reduce((sum, h) => sum + h.占净值比例, 0)
  const totalMarketValue = holdings.reduce((sum, h) => sum + h.持仓市值, 0)

  return {
    总持仓数: holdings.length,
    TOP5占比: top5Ratio.toFixed(2) + '%',
    总市值: totalMarketValue.toFixed(2) + '万元'
  }
})

// 处理债券季度变更
function handleBondQuarterChange(quarter: string) {
  selectedBondQuarter.value = quarter
  bondHoldingsLimit.value = 10 // 重置显示数量
}

// 加载数据
onMounted(() => {
  loadData()
})

// 清理
onBeforeUnmount(() => {
  // 🛡️ 取消进行中的请求
  if (abortController) {
    abortController.abort()
    console.log('[请求去重] 组件卸载，取消请求')
  }

  // 清理图表实例
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  if (industryChartInstance) {
    industryChartInstance.dispose()
    industryChartInstance = null
  }
  if (assetChartInstance) {
    assetChartInstance.dispose()
    assetChartInstance = null
  }
  if (dividendChartInstance) {
    dividendChartInstance.dispose()
    dividendChartInstance = null
  }
})

// 加载所有数据
const loadData = async () => {
  const startTime = performance.now() // 性能监控

  // 🛡️ 请求去重:取消上一次进行中的请求
  if (abortController) {
    abortController.abort()
    console.log('[请求去重] 取消上一次请求')
  }

  // 创建新的请求控制器
  abortController = new AbortController()
  const currentController = abortController

  loading.value = true

  try {
    const code = route.params.code as string
    const fundStore = useFundStore()

    // 🚀 阶段1: 并行加载所有基础数据（消除串行阻塞）
    const [
      fundListResult,
      dailyDataResult,
      histDataResult,        // 提前加载历史数据
      holdingsResult,
      xqBasicResult,         // 并行加载雪球基本信息
      xqAnalysisResult,      // 并行加载雪球风险指标（新增）
      xqIndustryResult,      // 并行加载行业分布
      xqAssetResult,         // 并行加载资产配置
      valueEstimationResult, // 并行加载实时估值
      fundRatingResult,      // 并行加载基金评级
      dividendResult,        // 并行加载基金分红记录
      bondHoldingsResult,    // 并行加载债券持仓数据
      portfolioHoldResult,   // 并行加载重仓股票持仓
      portfolioChangeResult, // 并行加载持仓变动
      netValueHistoryResult  // 并行加载历史净值数据（新增）
    ] = await Promise.allSettled([
      fundStore.loadFundList(),
      getFundDailyData(),
      getFundHistData(code, '单位净值走势'),
      getFundHoldings(code),
      getFundBasicInfoXQ(code),
      getFundRiskIndicators(code),  // 雪球风险指标（来自后端API）
      getFundIndustryAllocation(code),
      getFundAssetAllocationXQ(code),
      getFundValueEstimation(code),  // 实时估值
      getFundRating(code),  // 基金评级(当前基金)
      getFundDividend(code),  // 基金分红记录
      getFundBondHoldings(code),  // 债券持仓数据
      getFundPortfolioHold(code),  // 重仓股票持仓（东方财富）
      getFundPortfolioChange(code),  // 持仓变动（东方财富）
      getFundNetValueHistory(code, selectedIndicator.value)  // 历史净值数据（新增）
    ])

    // 从基金列表中查找基金信息
    const fundInfo = fundStore.fundList.find(f => f.基金代码 === code)

    // 从每日数据中查找基金信息
    let dailyInfo = null
    if (dailyDataResult.status === 'fulfilled') {
      dailyInfo = dailyDataResult.value.find(f => f.基金代码 === code)
    }

    if (fundInfo) {
      // 获取最新日期和前一日的净值字段
      let unitNetValue = null
      let accumulatedNetValue = null
      let prevUnitNetValue = null
      let prevAccumulatedNetValue = null

      if (dailyInfo) {
        // 获取所有日期相关的字段
        const dateKeys = Object.keys(dailyInfo).filter(key => key.includes('-'))

        // 查找最新日期和前一日期的字段（按日期降序排序）
        const unitKeys = dateKeys.filter(key => key.includes('单位净值')).sort().reverse()
        const accKeys = dateKeys.filter(key => key.includes('累计净值')).sort().reverse()

        // 最新日期的净值
        unitNetValue = unitKeys[0] ? dailyInfo[unitKeys[0]] : null
        accumulatedNetValue = accKeys[0] ? dailyInfo[accKeys[0]] : null

        // 前一日的净值
        prevUnitNetValue = unitKeys[1] ? dailyInfo[unitKeys[1]] : null
        prevAccumulatedNetValue = accKeys[1] ? dailyInfo[accKeys[1]] : null
      }

      // 组合多个数据源的信息
      fundData.value = {
        基金代码: fundInfo.基金代码,
        基金简称: fundInfo.基金简称,
        基金类型: fundInfo.基金类型,
        基金全称: fundInfo.基金简称,
        // 最新净值数据
        单位净值: unitNetValue,
        累计净值: accumulatedNetValue,
        // 前一日净值数据
        前一日单位净值: prevUnitNetValue,
        前一日累计净值: prevAccumulatedNetValue,
        // 涨跌数据
        日增长值: dailyInfo?.日增长值,
        日增长率: dailyInfo?.日增长率,
        // 交易状态
        申购状态: dailyInfo?.申购状态,
        赎回状态: dailyInfo?.赎回状态,
        手续费: dailyInfo?.手续费
      }

      // 判断是否为场内基金
      const type = fundInfo.基金类型 || ''
      const name = fundInfo.基金简称 || ''
      const isETF = type.includes('ETF') ||
        type.includes('LOF') ||
        type.includes('场内') ||
        name.includes('ETF') ||
        name.includes('LOF')

      // 处理持仓数据
      if (holdingsResult.status === 'fulfilled') {
        allHoldings.value = holdingsResult.value
      } else {
        allHoldings.value = []
      }

      // 🎯 条件加载 ETF 数据（仅当基金类型为 ETF/LOF 时）
      if (isETF) {
        try {
          const etfData = await getETFFundDaily()
          const etfInfo = etfData.find((f: any) => f.基金代码 === code)
          if (etfInfo) {
            fundData.value.市价 = etfInfo.市价
            fundData.value.折价率 = etfInfo.折价率
          }
        } catch (e) {
          // ETF数据加载失败 - silent fail
          console.warn('Failed to load ETF data:', e)
        }
      }

      // 🚀 阶段2: 基于已加载数据进行同步处理（无需再次API调用）

      // 处理雪球基本信息
      if (xqBasicResult.status === 'fulfilled') {
        basicInfoXQ.value = xqBasicResult.value
      }

      // 处理行业分布
      if (xqIndustryResult.status === 'fulfilled' && xqIndustryResult.value && xqIndustryResult.value.length > 0) {
        industryData.value = xqIndustryResult.value
        console.log('[行业分布] 加载成功:', industryData.value.length, '条记录')
      } else if (xqIndustryResult.status === 'rejected') {
        console.log('[行业分布] 该基金暂无行业分布数据或加载失败')
        industryData.value = []
      } else {
        console.log('[行业分布] 该基金暂无行业分布数据')
        industryData.value = []
      }

      // 处理资产配置
      if (xqAssetResult.status === 'fulfilled' && xqAssetResult.value && xqAssetResult.value.length > 0) {
        assetAllocation.value = xqAssetResult.value
      }

      // 处理实时估值（可能为 null，表示该基金无估值数据）
      if (valueEstimationResult.status === 'fulfilled' && valueEstimationResult.value) {
        valueEstimation.value = valueEstimationResult.value
      }

      // 处理基金评级（API返回单个基金的评级数据）
      if (fundRatingResult.status === 'fulfilled' && fundRatingResult.value) {
        const response = fundRatingResult.value
        if (response.success && response.data) {
          fundRating.value = response.data
          console.log('[基金评级] 找到评级数据:', response.data)
        } else {
          console.log('[基金评级] 该基金暂无评级数据')
          fundRating.value = null
        }
      } else {
        console.log('[基金评级] 评级数据加载失败')
        fundRating.value = null
      }

      // 处理基金分红记录
      if (dividendResult.status === 'fulfilled' && dividendResult.value) {
        dividendData.value = dividendResult.value
        dividendLoading.value = false
        console.log('[基金分红] 加载成功:', dividendData.value.length, '条记录')
        // 图表渲染由 watch(dividendChartRef) 自动处理
      } else {
        dividendData.value = []
        dividendLoading.value = false
        console.log('[基金分红] 该基金暂无分红记录或加载失败')
      }

      // 处理历史净值数据（新增）
      if (netValueHistoryResult.status === 'fulfilled' && netValueHistoryResult.value) {
        const response = netValueHistoryResult.value
        if (response.success && response.data && response.data.length > 0) {
          netValueHistory.value = response.data
          console.log('[历史净值] 加载成功:', netValueHistory.value.length, '条记录')
          // 加载成功后初始化图表 - 使用双重nextTick确保DOM完全渲染
          nextTick(() => {
            nextTick(() => {
              if (netValueHistoryChartRef.value) {
                initNetValueHistoryChart()
                console.log('[历史净值] 图表初始化完成')
              } else {
                console.warn('[历史净值] 图表容器未就绪,延迟100ms后重试')
                setTimeout(() => {
                  if (netValueHistoryChartRef.value) {
                    initNetValueHistoryChart()
                    console.log('[历史净值] 图表初始化完成(延迟)')
                  }
                }, 100)
              }
            })
          })
        } else {
          netValueHistory.value = []
          console.log('[历史净值] 该基金暂无历史净值数据')
        }
      } else {
        netValueHistory.value = []
        console.log('[历史净值] 历史净值数据加载失败')
      }

      // 处理债券持仓数据
      if (bondHoldingsResult.status === 'fulfilled' && bondHoldingsResult.value) {
        const bondResponse = bondHoldingsResult.value
        if (bondResponse.success && bondResponse.data && bondResponse.data.length > 0) {
          bondHoldings.value = bondResponse.data
          bondQuarters.value = bondResponse.quarters || []
          // 默认选择最新季度
          if (bondQuarters.value.length > 0) {
            selectedBondQuarter.value = bondQuarters.value[0]
          }
          console.log('[债券持仓] 加载成功:', bondHoldings.value.length, '条记录，', bondQuarters.value.length, '个季度')
        } else {
          bondHoldings.value = []
          bondQuarters.value = []
          console.log('[债券持仓] 该基金暂无债券持仓数据')
        }
      } else {
        bondHoldings.value = []
        bondQuarters.value = []
        console.log('[债券持仓] 债券持仓数据加载失败')
      }

      // 处理持仓分析数据 - 重仓股票持仓（东方财富）
      if (portfolioHoldResult.status === 'fulfilled' && portfolioHoldResult.value) {
        const holdResponse = portfolioHoldResult.value
        if (holdResponse.success && holdResponse.data && holdResponse.data.length > 0) {
          portfolioHoldData.value = holdResponse.data
          console.log('[持仓分析] 重仓股票加载成功:', portfolioHoldData.value.length, '条记录')
        } else {
          portfolioHoldData.value = []
          console.log('[持仓分析] 该基金暂无重仓股票数据')
        }
      } else {
        portfolioHoldData.value = []
        console.log('[持仓分析] 重仓股票数据加载失败')
      }

      // 处理持仓分析数据 - 持仓变动（东方财富）
      if (portfolioChangeResult.status === 'fulfilled' && portfolioChangeResult.value) {
        const changeResponse = portfolioChangeResult.value
        if (changeResponse.success && changeResponse.data && changeResponse.data.length > 0) {
          portfolioChangeData.value = changeResponse.data
          console.log('[持仓分析] 持仓变动加载成功:', portfolioChangeData.value.length, '条记录')
        } else {
          portfolioChangeData.value = []
          console.log('[持仓分析] 该基金暂无持仓变动数据')
        }
      } else {
        portfolioChangeData.value = []
        console.log('[持仓分析] 持仓变动数据加载失败')
      }

      // 处理历史净值数据并同步计算收益率和指标
      if (histDataResult.status === 'fulfilled' && histDataResult.value && histDataResult.value.length > 0) {
        const histData = histDataResult.value

        // 同步计算收益率（基于已加载的数据，不再重复API调用）
        // ✅ 收益率总是需要前端计算（API不提供多周期收益率数据）
        calculateReturnRatesSync(histData)

        // 同步计算业绩指标（基于已加载的数据）
        // ⚠️ 总是需要前端计算年化收益率（雪球API不提供该指标）
        calculatePerformanceMetricsSync(histData)
      }

      // 处理雪球风险指标（来自后端API，优先使用）
      // 🔄 雪球数据会覆盖前端计算的部分指标（最大回撤、波动率、夏普比率）
      if (xqAnalysisResult.status === 'fulfilled' && xqAnalysisResult.value?.success && xqAnalysisResult.value.data?.length > 0) {
        xqAnalysisData.value = xqAnalysisResult.value.data

        // 使用雪球API的近1年数据覆盖部分 performanceMetrics
        const oneYearData = xqAnalysisResult.value.data.find(item => item.周期 === '近1年')
        if (oneYearData) {
          performanceMetrics.value.最大回撤 = oneYearData.最大回撤 ?? null
          performanceMetrics.value.波动率 = oneYearData.年化波动率 ?? null
          performanceMetrics.value.夏普比率 = oneYearData.年化夏普比率 ?? null
          // ⚠️ 年化收益率由前端计算，不覆盖
        }
        console.log('[数据源] 使用后端缓存的雪球风险指标数据 (source:', xqAnalysisResult.value.source, ')')
      }
    } else {
      fundData.value = {
        基金代码: code,
        基金简称: `基金 ${code}`,
        基金类型: '未知'
      }
    }

    // 🚀 阶段3: 渲染图表（在 DOM 更新后）
    // 等待 DOM 更新
    await nextTick()

    // 🎨 使用 requestAnimationFrame 在下一帧渲染图表（与浏览器刷新率同步）
    requestAnimationFrame(() => {
      // 渲染历史净值图表
      if (histDataResult.status === 'fulfilled' && histDataResult.value && histDataResult.value.length > 0) {
        renderChart(histDataResult.value.slice(-90))
      }

      // 渲染行业分布图表
      if (industryData.value.length > 0) {
        renderIndustryChart()
      }

      // 渲染资产配置图表
      if (assetAllocation.value.length > 0) {
        renderAssetChart()
      }
    })

  } catch (error) {
    // 如果是请求被取消,不显示错误
    if (error instanceof Error && error.name === 'AbortError') {
      console.log('[请求去重] 请求已被取消')
      return
    }
    console.error('Failed to load fund detail:', error)
    fundData.value = null
  } finally {
    // 只有当前请求才清除loading状态
    if (abortController === currentController) {
      loading.value = false

      // 性能监控
      const totalTime = performance.now() - startTime
      console.log(`[性能优化] 基金详情页总加载时间: ${totalTime.toFixed(0)}ms`)
    }
  }
}

// 加载雪球数据
const loadXueqiuData = async (code: string) => {
  try {
    // 并行加载雪球 API 数据
    const [basicResult, industryResult, assetResult] = await Promise.allSettled([
      getFundBasicInfoXQ(code),
      getFundIndustryAllocation(code),
      getFundAssetAllocationXQ(code)
    ])

    // 处理基本信息
    if (basicResult.status === 'fulfilled') {
      basicInfoXQ.value = basicResult.value
    }

    // 处理行业分布数据
    if (industryResult.status === 'fulfilled' && industryResult.value && industryResult.value.length > 0) {
      industryData.value = industryResult.value
      // 渲染行业分布图表
      await nextTick()
      renderIndustryChart()
    }

    // 处理资产配置数据
    if (assetResult.status === 'fulfilled' && assetResult.value && assetResult.value.length > 0) {
      assetAllocation.value = assetResult.value
      // 渲染资产配置图表
      await nextTick()
      renderAssetChart()
    }
  } catch (error) {
    // 雪球数据加载失败 - silent fail
    console.warn('Failed to load Xueqiu data:', error)
  }
}

// 同步计算收益率（基于已加载的历史数据，避免重复API调用）
const calculateReturnRatesSync = (histData: any[]) => {
  try {
    if (!histData || histData.length === 0) {
      returnRates.value.forEach(item => {
        item.rate = null
        item.loading = false
      })
      return
    }

    // 按日期排序（从旧到新）
    const sortedData = [...histData].sort((a, b) =>
      new Date(a.净值日期).getTime() - new Date(b.净值日期).getTime()
    )

    const latestData = sortedData[sortedData.length - 1]
    const latestValue = latestData?.单位净值

    if (!latestValue) {
      returnRates.value.forEach(item => {
        item.rate = null
        item.loading = false
      })
      return
    }

    // 计算不同时间段的收益率
    const calculateReturn = (daysAgo: number): number | null => {
      if (sortedData.length <= daysAgo) {
        // 如果数据不足，使用最早的数据
        const baseValue = sortedData[0]?.单位净值
        if (!baseValue) return null
        return ((latestValue - baseValue) / baseValue) * 100
      }
      const baseValue = sortedData[sortedData.length - 1 - daysAgo]?.单位净值
      if (!baseValue) return null
      return ((latestValue - baseValue) / baseValue) * 100
    }

    // 近1月 (约21个交易日)
    returnRates.value[0].rate = calculateReturn(21)
    returnRates.value[0].loading = false

    // 近3月 (约63个交易日)
    returnRates.value[1].rate = calculateReturn(63)
    returnRates.value[1].loading = false

    // 近6月 (约126个交易日)
    returnRates.value[2].rate = calculateReturn(126)
    returnRates.value[2].loading = false

    // 近1年 (约250个交易日)
    returnRates.value[3].rate = calculateReturn(250)
    returnRates.value[3].loading = false

    // 近3年 (约750个交易日)
    returnRates.value[4].rate = calculateReturn(750)
    returnRates.value[4].loading = false

    // 今年来 (从今年1月1日开始)
    const currentYear = new Date().getFullYear()
    const yearStartIndex = sortedData.findIndex(d =>
      new Date(d.净值日期).getFullYear() === currentYear
    )
    if (yearStartIndex !== -1) {
      const yearStartValue = sortedData[yearStartIndex]?.单位净值
      if (yearStartValue) {
        returnRates.value[5].rate = ((latestValue - yearStartValue) / yearStartValue) * 100
      }
    }
    returnRates.value[5].loading = false

    // 成立来 (从最早数据开始)
    const firstValue = sortedData[0]?.单位净值
    if (firstValue) {
      returnRates.value[6].rate = ((latestValue - firstValue) / firstValue) * 100
    }
    returnRates.value[6].loading = false

  } catch (e) {
    // Silent fail
    console.warn('同步计算收益率失败:', e)
    returnRates.value.forEach(item => {
      item.rate = null
      item.loading = false
    })
  }
}

// 同步计算业绩和风险指标（基于已加载的历史数据）
const calculatePerformanceMetricsSync = (histData: any[]) => {
  metricsLoading.value = true
  try {
    if (!histData || histData.length < 30) {
      // 数据不足，无法计算
      metricsLoading.value = false
      return
    }

    // 按日期排序（从旧到新）
    const sortedData = [...histData].sort((a, b) =>
      new Date(a.净值日期).getTime() - new Date(b.净值日期).getTime()
    )

    // 提取净值数组
    const values = sortedData.map(d => d.单位净值)
    const n = values.length

    // 1. 计算最大回撤 (Maximum Drawdown)
    let maxDrawdown = 0
    let peak = values[0]
    for (let i = 1; i < n; i++) {
      if (values[i] > peak) {
        peak = values[i]
      }
      const drawdown = (peak - values[i]) / peak * 100
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown
      }
    }
    performanceMetrics.value.最大回撤 = maxDrawdown

    // 2. 计算年化收益率
    const firstValue = values[0]
    const lastValue = values[n - 1]
    const totalDays = (new Date(sortedData[n - 1].净值日期).getTime() - new Date(sortedData[0].净值日期).getTime()) / (1000 * 60 * 60 * 24)
    const years = totalDays / 365
    if (years > 0) {
      performanceMetrics.value.年化收益率 = (Math.pow(lastValue / firstValue, 1 / years) - 1) * 100
    }

    // 3. 计算日收益率序列
    const dailyReturns: number[] = []
    for (let i = 1; i < n; i++) {
      dailyReturns.push((values[i] - values[i - 1]) / values[i - 1] * 100)
    }

    // 4. 计算波动率（年化标准差）
    const meanReturn = dailyReturns.reduce((sum, r) => sum + r, 0) / dailyReturns.length
    const variance = dailyReturns.reduce((sum, r) => sum + Math.pow(r - meanReturn, 2), 0) / dailyReturns.length
    const stdDev = Math.sqrt(variance)
    // 假设每年250个交易日
    performanceMetrics.value.波动率 = stdDev * Math.sqrt(250)

    // 5. 计算夏普比率 (Sharpe Ratio)
    // 假设无风险利率为3%
    const riskFreeRate = 3
    if (performanceMetrics.value.年化收益率 && performanceMetrics.value.波动率 && performanceMetrics.value.波动率 > 0) {
      performanceMetrics.value.夏普比率 = (performanceMetrics.value.年化收益率 - riskFreeRate) / performanceMetrics.value.波动率
    }

    metricsLoading.value = false
  } catch (e) {
    console.warn('同步计算业绩指标失败:', e)
    metricsLoading.value = false
  }
}

// 渲染迷你图表
const renderChart = (data: any[]) => {
  if (!chartRef.value) {
    return
  }

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const dates = data.map(item => item.净值日期)
  const values = data.map(item => parseFloat(item.单位净值 || '0'))

  const option = {
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#d2d2d7' } },
      axisLabel: { color: '#86868b', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: { lineStyle: { color: '#d2d2d7' } },
      axisLabel: { color: '#86868b', fontSize: 12 },
      splitLine: { lineStyle: { color: '#f5f5f7' } }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#d2d2d7',
      textStyle: { color: '#1d1d1f' }
    },
    series: [
      {
        type: 'line',
        data: values,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#0071e3', width: 2 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(0, 113, 227, 0.3)' },
              { offset: 1, color: 'rgba(0, 113, 227, 0.05)' }
            ]
          }
        }
      }
    ]
  }

  chartInstance.setOption(option)

  window.addEventListener('resize', () => chartInstance?.resize())
}

// 渲染行业分布饼图
const renderIndustryChart = () => {
  if (!industryChartRef.value || industryData.value.length === 0) {
    return
  }

  if (!industryChartInstance) {
    industryChartInstance = echarts.init(industryChartRef.value)
  }

  // 取 TOP10 行业
  const top10 = industryData.value.slice(0, 10)
  const chartData = top10.map(item => ({
    name: item.行业类别 || '未知',  // ⚠️ 注意：字段名是 "行业类别"
    value: item.占净值比例 || 0  // 已经是数字类型，无需 parseFloat
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}% ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: { color: '#1d1d1f' }
    },
    series: [
      {
        name: '行业分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: chartData
      }
    ]
  }

  industryChartInstance.setOption(option)
  window.addEventListener('resize', () => industryChartInstance?.resize())
}

// 渲染资产配置饼图
const renderAssetChart = () => {
  if (!assetChartRef.value || assetAllocation.value.length === 0) {
    return
  }

  if (!assetChartInstance) {
    assetChartInstance = echarts.init(assetChartRef.value)
  }

  const chartData = assetAllocation.value.map(item => ({
    name: item.资产类型 || '未知',
    value: item.仓位占比 || 0  // ⚠️ 注意：字段名是 "仓位占比"，已经是数字类型
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}% ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: { color: '#1d1d1f' }
    },
    series: [
      {
        name: '资产配置',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: chartData
      }
    ]
  }

  assetChartInstance.setOption(option)
  window.addEventListener('resize', () => assetChartInstance?.resize())
}

// 历史净值图表初始化函数（新增）
const initNetValueHistoryChart = () => {
  // 更严格的DOM和数据检查
  if (!netValueHistoryChartRef.value) {
    console.warn('[历史净值图表] DOM容器未准备好')
    return
  }

  if (netValueHistory.value.length === 0) {
    console.warn('[历史净值图表] 暂无数据')
    return
  }

  // 确保容器有实际尺寸
  const container = netValueHistoryChartRef.value as HTMLElement
  if (!container.offsetWidth || !container.offsetHeight) {
    console.warn('[历史净值图表] 容器尺寸为0,延迟初始化')
    setTimeout(() => initNetValueHistoryChart(), 200)
    return
  }

  // 初始化或复用ECharts实例
  if (!netValueHistoryChartInstance) {
    netValueHistoryChartInstance = echarts.init(container)
    console.log('[历史净值图表] ECharts实例创建完成')
  }

  // 准备图表数据（按日期升序排列）
  const sortedData = [...filteredNetValueHistory.value].sort((a, b) =>
    new Date(a.净值日期).getTime() - new Date(b.净值日期).getTime()
  )

  const dates = sortedData.map(item => item.净值日期)
  const values = sortedData.map(item => {
    // 根据当前选择的指标类型获取对应的值
    if (selectedIndicator.value === '单位净值走势') {
      return item.单位净值
    } else if (selectedIndicator.value === '累计净值走势') {
      return item.累计净值
    } else if (selectedIndicator.value === '累计收益率走势') {
      return item.累计收益率
    } else if (selectedIndicator.value === '同类排名走势') {
      return item.同类排名
    } else if (selectedIndicator.value === '同类排名百分比') {
      return item.同类排名百分比
    }
    return item.单位净值
  })

  // 获取Y轴名称
  const getYAxisName = () => {
    if (selectedIndicator.value === '单位净值走势' || selectedIndicator.value === '累计净值走势') {
      return '净值(元)'
    } else if (selectedIndicator.value === '累计收益率走势' || selectedIndicator.value === '同类排名百分比') {
      return '百分比(%)'
    } else if (selectedIndicator.value === '同类排名走势') {
      return '排名'
    }
    return '净值(元)'
  }

  const option = {
    title: {
      text: selectedIndicator.value,
      left: 'center',
      textStyle: {
        color: '#1d1d1f',
        fontSize: 16,
        fontWeight: 500
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const param = params[0]
        return `${param.name}<br/>${param.seriesName}: ${param.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        color: '#86868b',
        rotate: 45
      },
      axisLine: {
        lineStyle: { color: '#d2d2d7' }
      }
    },
    yAxis: {
      type: 'value',
      name: getYAxisName(),
      nameTextStyle: {
        color: '#86868b'
      },
      scale: true,  // 启用自适应刻度,不从0开始
      axisLabel: {
        color: '#86868b'
      },
      axisLine: {
        lineStyle: { color: '#d2d2d7' }
      },
      splitLine: {
        lineStyle: { color: '#f5f5f7' }
      }
    },
    series: [
      {
        name: selectedIndicator.value.replace('走势', ''),
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#0071e3'
        },
        itemStyle: {
          color: '#0071e3'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(0, 113, 227, 0.3)' },
              { offset: 1, color: 'rgba(0, 113, 227, 0.05)' }
            ]
          }
        },
        data: values
      }
    ]
  }

  netValueHistoryChartInstance.setOption(option)
  window.addEventListener('resize', () => netValueHistoryChartInstance?.resize())
}

// 切换历史净值指标类型（新增）
const changeIndicator = async (indicator: string) => {
  selectedIndicator.value = indicator
  const code = route.params.code as string

  try {
    const response = await getFundNetValueHistory(code, indicator)
    if (response.success && response.data && response.data.length > 0) {
      netValueHistory.value = response.data
      nextTick(() => {
        initNetValueHistoryChart()
      })
    } else {
      netValueHistory.value = []
      ElMessage.warning(`暂无${indicator}数据`)
    }
  } catch (error) {
    console.error('切换指标失败:', error)
    ElMessage.error('切换指标失败')
  }
}

// 更新图表(时间范围变化时调用)
const updateNetValueChart = () => {
  nextTick(() => {
    initNetValueHistoryChart()
  })
}

// 导出分红数据到Excel
const exportDividendData = () => {
  if (filteredDividendData.value.length === 0) {
    console.warn('没有可导出的分红数据')
    return
  }

  try {
    // 准备CSV数据
    const headers = ['除息日期', '每份分红(元)', '权益登记日', '分红发放日']
    const rows = filteredDividendData.value.map(item => [
      item.除息日期 || '',
      item.分红?.toFixed(4) || '0.0000',
      item.权益登记日 || '',
      item.分红发放日 || ''
    ])

    // 构建CSV内容（使用UTF-8 BOM以确保Excel正确显示中文）
    const BOM = '\uFEFF'
    let csvContent = BOM + headers.join(',') + '\n'
    rows.forEach(row => {
      csvContent += row.join(',') + '\n'
    })

    // 创建Blob并下载
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)

    const fundCode = route.params.code as string
    const fundName = fundData.value?.基金简称 || fundCode
    const yearSuffix = selectedYear.value === 'all' ? '全部' : selectedYear.value
    const filename = `${fundName}_分红记录_${yearSuffix}.csv`

    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    console.log(`[Excel导出] 导出成功: ${filename}，共 ${filteredDividendData.value.length} 条记录`)
  } catch (error) {
    console.error('[Excel导出] 导出失败:', error)
  }
}

// 渲染分红趋势图表
const renderDividendChart = () => {
  if (!dividendChartRef.value || filteredDividendData.value.length === 0) {
    return
  }

  if (!dividendChartInstance) {
    dividendChartInstance = echarts.init(dividendChartRef.value)
  }

  // 按除息日期排序（从旧到新）
  const sortedData = [...filteredDividendData.value].sort((a, b) => {
    const dateA = a.除息日期 || ''
    const dateB = b.除息日期 || ''
    return dateA.localeCompare(dateB)
  })

  // 准备图表数据
  const dates = sortedData.map(item => item.除息日期 || '')
  const dividends = sortedData.map(item => item.分红 || 0)

  const option = {
    title: {
      text: '历史分红趋势',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 600,
        color: '#1d1d1f'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#d2d2d7',
      borderWidth: 1,
      textStyle: { color: '#1d1d1f' },
      formatter: (params: any) => {
        const data = params[0]
        return `${data.axisValue}<br/>每份分红: ${data.value.toFixed(4)} 元`
      }
    },
    grid: {
      left: '50px',
      right: '30px',
      top: '60px',
      bottom: '50px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#d2d2d7' } },
      axisLabel: {
        color: '#86868b',
        fontSize: 11,
        rotate: dates.length > 10 ? 45 : 0
      },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '分红(元)',
      nameTextStyle: {
        color: '#86868b',
        fontSize: 12
      },
      axisLine: { show: false },
      axisLabel: {
        color: '#86868b',
        fontSize: 11,
        formatter: (value: number) => value.toFixed(2)
      },
      splitLine: { lineStyle: { color: '#f5f5f7', type: 'dashed' } }
    },
    series: [{
      type: 'bar',
      data: dividends,
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#007aff' },
            { offset: 1, color: '#5ac8fa' }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '60%',
      label: {
        show: dividends.length <= 10,
        position: 'top',
        formatter: (params: any) => params.value.toFixed(2),
        fontSize: 10,
        color: '#86868b'
      }
    }]
  }

  dividendChartInstance.setOption(option)
  window.addEventListener('resize', () => dividendChartInstance?.resize())
}

// 返回
const goBack = () => {
  router.back()
}

// 查看完整走势图
const viewFullChart = () => {
  router.push(`/chart?fund=${route.params.code}`)
}

// 切换收藏状态
const toggleFavorite = () => {
  const code = route.params.code as string
  const name = fundData.value?.基金简称 || fundData.value?.基金全称 || code
  const success = favoritesStore.toggleFavorite(code, name)
  if (success) {
    if (favoritesStore.isFavorite(code)) {
      ElMessage.success(`已添加收藏：${name}`)
    } else {
      ElMessage.info(`已取消收藏：${name}`)
    }
  }
}
</script>

<style scoped>
.fund-detail {
  min-height: 100vh;
  padding-bottom: var(--spacing-3xl);
}

.back-btn {
  margin-bottom: var(--spacing-lg);
}

.loading-container {
  padding: var(--spacing-2xl);
}

.detail-content {
  animation: fadeIn var(--transition-base) ease;
}

.fund-title {
  padding: var(--spacing-2xl);
  margin-bottom: var(--spacing-lg);
}

.title-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-lg);
}

.title-left {
  flex: 1;
  text-align: center;
}

.title-right {
  flex-shrink: 0;
}

.fund-title h1 {
  margin-bottom: var(--spacing-sm);
}

.fund-code {
  font-size: 21px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
}

.info-section,
.fee-section,
.rating-section,
.holding-section,
.return-rate-section,
.chart-section {
  margin-bottom: var(--spacing-lg);
}

.section-title {
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--color-border);
}

.info-item,
.fee-item,
.rating-item {
  padding: var(--spacing-md);
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-md);
}

/* 核心指标区域 */
.key-metrics {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-2xl);
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, var(--color-bg-tertiary) 0%, var(--color-bg-secondary) 100%);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
}

.metric-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.metric-card {
  padding: var(--spacing-md);
  background-color: var(--color-bg-primary);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
}

.metric-label {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: var(--spacing-xs);
  font-variant-numeric: tabular-nums;
}

.metric-value.primary {
  color: var(--color-primary);
}

.metric-value.positive {
  color: #f56c6c;  /* 红色 - 上涨 */
}

.metric-value.negative {
  color: #67c23a;  /* 绿色 - 下跌 */
}

.metric-sub {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

/* 详细信息区域 */
.detail-info {
  margin-top: var(--spacing-lg);
}

.detail-info .info-item {
  min-height: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.info-label,
.fee-label,
.rating-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.info-value,
.fee-value,
.rating-value {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.rating-value.highlight {
  color: var(--color-warning);
  font-size: 18px;
  font-weight: 600;
}

.rating-note {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-info-light);
  border-left: 3px solid var(--color-info);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--color-text-secondary);
}

/* 基金分红样式 */
.dividend-section {
  margin-top: var(--spacing-lg);
}

.dividend-amount {
  color: var(--color-accent);
  font-weight: 600;
  font-size: 14px;
}

.dividend-note {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-info-light);
  border-left: 3px solid var(--color-info);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--color-text-secondary);
}

/* 分红统计卡片样式 */
.dividend-stats {
  display: flex;
  justify-content: space-around;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-radius: var(--radius-md);
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-accent);
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
}

/* 分红趋势图表样式 */
.dividend-chart-container {
  margin-bottom: var(--spacing-lg);
}

.dividend-chart {
  width: 100%;
  height: 300px;
}

/* 分红筛选器样式 */
.dividend-filter {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
}

.percentage {
  color: var(--color-accent);
  font-weight: 500;
}

.mini-chart {
  width: 100%;
  height: 300px;
  margin-top: var(--spacing-md);
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

/* 持仓集中度统计样式 */
.section-header {
  margin-bottom: var(--spacing-lg);
}

.holdings-stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

.load-more-section {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

/* 债券持仓样式 */
.bond-holding-section {
  margin-top: var(--spacing-xl);
}

.bond-holdings-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.bond-stats {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.bond-note {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--color-text-secondary);
  text-align: center;
}

/* 收益率统计样式 */
.return-rate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--spacing-md);
}

.return-rate-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius);
  transition: all 0.3s ease;
}

.return-rate-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rate-period {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.rate-value {
  font-size: 24px;
  font-weight: 600;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
}

.rate-positive {
  color: #f56c6c;
}

.rate-negative {
  color: #67c23a;
}

.rate-neutral {
  color: var(--color-text-secondary);
}

.rate-unavailable {
  color: var(--color-text-tertiary);
  font-size: 20px;
}

/* 业绩与风险分析样式 */
.performance-section {
  margin-bottom: var(--spacing-lg);
}

.metrics-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-2xl);
  color: var(--color-text-secondary);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-lg);
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius);
  transition: all 0.3s ease;
}

.metric-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
  font-weight: 500;
}

.metric-value {
  font-size: 28px;
  font-weight: 600;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  margin-bottom: var(--spacing-xs);
}

.metric-desc {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.value-positive {
  color: #f56c6c;
}

.value-negative {
  color: #67c23a;
}

.value-warning {
  color: #e6a23c;
}

.metrics-note {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius);
}

.error-state {
  margin-top: var(--spacing-2xl);
}

/* 行业分布和资产配置图表 */
.industry-section,
.asset-section {
  margin-bottom: var(--spacing-lg);
}

.industry-chart,
.asset-chart,
.net-value-history-chart {
  width: 100%;
  height: 400px;
}

/* 历史净值样式（新增） */
.net-value-history-section {
  margin-top: 24px;
}

.indicator-selector {
  margin: 16px 0;
  display: flex;
  justify-content: center;
}

.timerange-selector {
  margin: 12px 0 16px 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

.timerange-selector .selector-label {
  font-size: 14px;
  color: #1d1d1f;
  font-weight: 500;
}

.data-stats {
  margin: 24px 0;
  padding: 16px;
  background: #f5f5f7;
  border-radius: 12px;
}

.stat-item {
  text-align: center;
  padding: 8px 0;
}

.stat-label {
  font-size: 13px;
  color: #86868b;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 16px;
  font-weight: 500;
  color: #1d1d1f;
}

@media (max-width: 734px) {
  .fund-title h1 {
    font-size: 24px;
  }

  .fund-code {
    font-size: 17px;
  }

  .mini-chart {
    height: 250px;
  }

  .industry-chart,
  .asset-chart,
  .net-value-history-chart {
    height: 300px;
  }

  .indicator-selector {
    overflow-x: auto;
  }
}

.portfolio-hold-section,
.portfolio-change-section {
  margin-bottom: var(--spacing-xl);
}

.portfolio-note {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  font-size: 14px;
  text-align: center;
}

.portfolio-actions {
  text-align: center;
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
}

.percentage-value {
  color: var(--color-accent);
  font-weight: 600;
}

.buy-amount {
  color: var(--color-success);
  font-weight: 600;
}
</style>

import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'search',
      component: () => import('@/views/FundSearch.vue'),
      meta: { title: '基金搜索' }
    },
    {
      path: '/chart',
      name: 'chart',
      component: () => import('@/views/FundChart.vue'),
      meta: { title: '净值走势' }
    },
    {
      path: '/ranking',
      name: 'ranking',
      component: () => import('@/views/FundRanking.vue'),
      meta: { title: '基金排行' }
    },
    {
      path: '/detail/:code',
      name: 'detail',
      component: () => import('@/views/FundDetail.vue'),
      meta: { title: '基金详情' }
    },
    {
      path: '/compare',
      name: 'compare',
      component: () => import('@/views/FundCompare.vue'),
      meta: { title: '基金对比' }
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: () => import('@/views/FundFavorites.vue'),
      meta: { title: '自选基金' }
    },
    {
      path: '/money',
      name: 'money',
      component: () => import('@/views/MoneyFund.vue'),
      meta: { title: '货币基金' }
    },
    {
      path: '/dividend',
      name: 'dividend',
      component: () => import('@/views/DividendRank.vue'),
      meta: { title: '分红排行' }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/DataAdmin.vue'),
      meta: { title: '数据管理' }
    },
    {
      path: '/purchase-status',
      name: 'purchase-status',
      component: () => import('@/views/FundPurchaseStatus.vue'),
      meta: { title: '申购赎回状态' }
    },
    {
      path: '/company-ranking',
      name: 'company-ranking',
      component: () => import('@/views/CompanyRanking.vue'),
      meta: { title: '基金公司排行' }
    },
    {
      path: '/company/:name',
      name: 'company-detail',
      component: () => import('@/views/CompanyDetail.vue'),
      meta: { title: '基金公司详情' }
    },
    {
      path: '/market-trend',
      name: 'market-trend',
      component: () => import('@/views/MarketTrend.vue'),
      meta: { title: '市场趋势' }
    },
    {
      path: '/alternative',
      name: 'alternative',
      component: () => import('@/views/AlternativeData.vue'),
      meta: { title: '另类数据' }
    }
  ]
})

export default router

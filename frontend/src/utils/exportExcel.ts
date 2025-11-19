/**
 * Excel 导出工具函数
 */
import * as XLSX from 'xlsx'

/**
 * 导出数据为 Excel 文件
 *
 * @param data 要导出的数据数组
 * @param filename 文件名（不含扩展名）
 * @param sheetName 工作表名称
 */
export function exportToExcel<T extends Record<string, any>>(
  data: T[],
  filename: string = '导出数据',
  sheetName: string = 'Sheet1'
): void {
  if (!data || data.length === 0) {
    console.warn('No data to export')
    return
  }

  // 创建工作簿
  const worksheet = XLSX.utils.json_to_sheet(data)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)

  // 生成Excel文件并下载
  const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  XLSX.writeFile(workbook, `${filename}_${timestamp}.xlsx`)
}

/**
 * 导出基金排行数据为 Excel
 *
 * @param data 基金排行数据
 * @param category 基金分类
 */
export function exportFundRankToExcel(data: any[], category: string = '全部基金'): void {
  if (!data || data.length === 0) {
    console.warn('No fund data to export')
    return
  }

  // 准备导出数据 - 选择需要导出的字段并重命名
  const exportData = data.map(item => ({
    '序号': item['序号'],
    '基金代码': item['基金代码'],
    '基金简称': item['基金简称'],
    '基金类型': item['基金类型'],
    '日期': item['日期'],
    '单位净值': item['单位净值'],
    '累计净值': item['累计净值'],
    '日增长率(%)': item['日增长率'],
    '近1周(%)': item['近1周'],
    '近1月(%)': item['近1月'],
    '近3月(%)': item['近3月'],
    '近6月(%)': item['近6月'],
    '近1年(%)': item['近1年'],
    '近2年(%)': item['近2年'],
    '近3年(%)': item['近3年'],
    '今年来(%)': item['今年来'],
    '成立来(%)': item['成立来'],
    '手续费': item['手续费']
  }))

  // 导出文件
  const filename = `基金排行_${category}`
  exportToExcel(exportData, filename, category)
}

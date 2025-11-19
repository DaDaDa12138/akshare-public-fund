"""
数据导出工具模块
支持CSV和Excel格式的数据导出功能
"""
import pandas as pd
from io import BytesIO
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataExporter:
    """
    数据导出类

    支持将数据列表导出为CSV或Excel格式
    """

    @staticmethod
    def to_csv(data: List[Dict[str, Any]], filename: Optional[str] = None) -> BytesIO:
        """
        将数据导出为CSV格式

        Args:
            data: 数据列表，每个元素为字典
            filename: 文件名（可选，用于日志记录）

        Returns:
            BytesIO: CSV文件的字节流
        """
        try:
            if not data:
                logger.warning(f"导出CSV时数据为空: {filename}")
                # 返回空CSV
                return BytesIO(b"")

            # 转换为DataFrame
            df = pd.DataFrame(data)

            # 创建字节流
            output = BytesIO()

            # 导出为CSV（使用UTF-8 BOM以支持Excel正确打开中文）
            df.to_csv(output, index=False, encoding='utf-8-sig')

            # 重置指针到开头
            output.seek(0)

            logger.info(f"CSV导出成功: {filename}, 行数={len(data)}, 列数={len(df.columns)}")

            return output

        except Exception as e:
            logger.error(f"CSV导出失败: {filename}, 错误={e}", exc_info=True)
            raise

    @staticmethod
    def to_excel(data: List[Dict[str, Any]], filename: Optional[str] = None,
                 sheet_name: str = "数据") -> BytesIO:
        """
        将数据导出为Excel格式

        Args:
            data: 数据列表，每个元素为字典
            filename: 文件名（可选，用于日志记录）
            sheet_name: 工作表名称

        Returns:
            BytesIO: Excel文件的字节流
        """
        try:
            if not data:
                logger.warning(f"导出Excel时数据为空: {filename}")
                # 创建空DataFrame
                df = pd.DataFrame()
            else:
                # 转换为DataFrame
                df = pd.DataFrame(data)

            # 创建字节流
            output = BytesIO()

            # 使用openpyxl引擎导出为Excel
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=sheet_name)

                # 获取工作表对象以进行格式化
                worksheet = writer.sheets[sheet_name]

                # 自动调整列宽
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter

                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass

                    # 设置列宽（最大50，最小10）
                    adjusted_width = min(max(max_length + 2, 10), 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            # 重置指针到开头
            output.seek(0)

            logger.info(f"Excel导出成功: {filename}, 行数={len(data)}, 列数={len(df.columns) if not df.empty else 0}")

            return output

        except Exception as e:
            logger.error(f"Excel导出失败: {filename}, 错误={e}", exc_info=True)
            raise

    @staticmethod
    def generate_filename(prefix: str, extension: str) -> str:
        """
        生成带时间戳的文件名

        Args:
            prefix: 文件名前缀
            extension: 文件扩展名（不含点号）

        Returns:
            str: 生成的文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"


def export_to_csv(data: List[Dict[str, Any]], filename_prefix: str = "export") -> tuple[BytesIO, str]:
    """
    便捷函数：导出数据为CSV

    Args:
        data: 数据列表
        filename_prefix: 文件名前缀

    Returns:
        tuple: (文件字节流, 文件名)
    """
    exporter = DataExporter()
    filename = exporter.generate_filename(filename_prefix, "csv")
    file_stream = exporter.to_csv(data, filename)
    return file_stream, filename


def export_to_excel(data: List[Dict[str, Any]], filename_prefix: str = "export",
                    sheet_name: str = "数据") -> tuple[BytesIO, str]:
    """
    便捷函数：导出数据为Excel

    Args:
        data: 数据列表
        filename_prefix: 文件名前缀
        sheet_name: 工作表名称

    Returns:
        tuple: (文件字节流, 文件名)
    """
    exporter = DataExporter()
    filename = exporter.generate_filename(filename_prefix, "xlsx")
    file_stream = exporter.to_excel(data, filename, sheet_name)
    return file_stream, filename

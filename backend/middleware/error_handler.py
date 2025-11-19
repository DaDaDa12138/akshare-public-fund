"""
统一错误处理中间件
提供全局异常捕获、错误响应格式化和详细的错误日志
"""
import logging
import time
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)


class ErrorResponse:
    """统一错误响应格式"""

    @staticmethod
    def create(
        success: bool = False,
        error: str = "",
        detail: str = "",
        error_code: str = "",
        data: Any = None
    ) -> Dict[str, Any]:
        """
        创建统一的错误响应格式

        Args:
            success: 是否成功
            error: 错误消息
            detail: 详细错误信息
            error_code: 错误代码
            data: 数据

        Returns:
            统一格式的响应字典
        """
        response = {
            "success": success,
            "error": error,
            "timestamp": int(time.time())
        }

        if detail:
            response["detail"] = detail

        if error_code:
            response["error_code"] = error_code

        if data is not None:
            response["data"] = data

        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """全局错误处理中间件"""

    async def dispatch(self, request: Request, call_next: Callable):
        """
        拦截请求,捕获异常并返回统一格式的错误响应
        """
        request_id = id(request)
        start_time = time.time()

        # 记录请求信息
        logger.info(
            f"[请求开始] ID={request_id} "
            f"方法={request.method} "
            f"路径={request.url.path} "
            f"客户端={request.client.host if request.client else 'unknown'}"
        )

        try:
            response = await call_next(request)

            # 记录响应信息
            duration = (time.time() - start_time) * 1000
            logger.info(
                f"[请求完成] ID={request_id} "
                f"状态码={response.status_code} "
                f"耗时={duration:.2f}ms"
            )

            return response

        except Exception as exc:
            # 记录异常信息
            duration = (time.time() - start_time) * 1000
            error_trace = traceback.format_exc()

            logger.error(
                f"[请求失败] ID={request_id} "
                f"方法={request.method} "
                f"路径={request.url.path} "
                f"耗时={duration:.2f}ms\n"
                f"错误: {str(exc)}\n"
                f"堆栈: {error_trace}"
            )

            # 根据异常类型返回适当的HTTP状态码和错误信息
            return self._handle_exception(exc, request_id)

    def _handle_exception(self, exc: Exception, request_id: int) -> JSONResponse:
        """
        处理异常并返回JSON响应

        Args:
            exc: 异常对象
            request_id: 请求ID

        Returns:
            JSONResponse对象
        """
        # 导入时会失败,所以在这里导入
        from fastapi import HTTPException
        from pydantic import ValidationError

        # HTTPException
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse.create(
                    success=False,
                    error=exc.detail,
                    error_code=f"HTTP_{exc.status_code}",
                    detail=str(exc)
                )
            )

        # Pydantic验证错误
        if isinstance(exc, ValidationError):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=ErrorResponse.create(
                    success=False,
                    error="数据验证失败",
                    error_code="VALIDATION_ERROR",
                    detail=str(exc.errors())
                )
            )

        # 数据库相关错误
        if "sqlite3" in str(type(exc)) or "database" in str(exc).lower():
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse.create(
                    success=False,
                    error="数据库错误",
                    error_code="DATABASE_ERROR",
                    detail=str(exc)
                )
            )

        # AkShare API错误
        if "akshare" in str(exc).lower() or "网络" in str(exc):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=ErrorResponse.create(
                    success=False,
                    error="数据源暂时不可用",
                    error_code="DATA_SOURCE_ERROR",
                    detail=str(exc)
                )
            )

        # 其他未知错误
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse.create(
                success=False,
                error="服务器内部错误",
                error_code="INTERNAL_ERROR",
                detail=str(exc)
            )
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件 - 记录所有请求和响应"""

    async def dispatch(self, request: Request, call_next: Callable):
        """
        记录请求和响应详情
        """
        # 记录请求体(仅用于POST/PUT等方法)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) < 1000:  # 只记录小于1KB的请求体
                    logger.debug(f"请求体: {body.decode('utf-8')}")
                else:
                    logger.debug(f"请求体过大 ({len(body)} bytes), 已跳过记录")
            except Exception as e:
                logger.warning(f"无法读取请求体: {e}")

        # 继续处理请求
        response = await call_next(request)

        return response

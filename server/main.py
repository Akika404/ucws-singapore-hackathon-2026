import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import settings
from routes import router


def create_application() -> FastAPI:
    """创建FastAPI应用"""
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="创业助手AI - 帮助创业者完成公司注册的智能助手",
        debug=settings.DEBUG,
    )
    
    # 配置CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    application.include_router(
        router,
        prefix=settings.API_V1_PREFIX,
        tags=["创业助手AI"]
    )

    # 400：JSON解析失败 / 参数校验失败
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "请求体 JSON 解析失败或参数格式错误"}
        )

    # 404 / 405 处理
    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={"detail": "接口路径不存在"}
            )
        if exc.status_code == 405:
            return JSONResponse(
                status_code=405,
                content={"detail": "请求方法不支持"}
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    return application


app = create_application()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用创业助手AI",
        "version": settings.APP_VERSION,
        "docs_url": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

"""
Notion 集成API路由
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
import logging
from notion_client import Client
import os

from api.models.schemas import ApiResponse
from api.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# 请求模型
class NotionConnectRequest(BaseModel):
    token: str

class NotionService:
    def __init__(self, token: str):
        self.client = Client(auth=token)
    
    async def get_databases(self) -> List[dict]:
        """获取用户的 Notion 数据库列表"""
        try:
            response = self.client.search(
                filter={
                    "value": "database",
                    "property": "object"
                }
            )
            
            databases = []
            for db in response.get("results", []):
                if db.get("object") == "database":
                    databases.append({
                        "id": db["id"],
                        "title": self._get_database_title(db),
                        "url": db.get("url", ""),
                        "created_time": db.get("created_time", ""),
                        "last_edited_time": db.get("last_edited_time", ""),
                        "properties": self._get_database_properties(db)
                    })
            
            return databases
        except Exception as e:
            logger.error(f"获取 Notion 数据库失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"获取 Notion 数据库失败: {str(e)}"
            )
    
    async def get_pages(self, database_id: str) -> List[dict]:
        """获取数据库中的页面"""
        try:
            response = self.client.databases.query(database_id=database_id)
            
            pages = []
            for page in response.get("results", []):
                pages.append({
                    "id": page["id"],
                    "title": self._get_page_title(page),
                    "url": page.get("url", ""),
                    "created_time": page.get("created_time", ""),
                    "last_edited_time": page.get("last_edited_time", ""),
                    "properties": page.get("properties", {})
                })
            
            return pages
        except Exception as e:
            logger.error(f"获取 Notion 页面失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"获取 Notion 页面失败: {str(e)}"
            )
    
    def _get_database_title(self, database: dict) -> str:
        """提取数据库标题"""
        title = database.get("title", [])
        if title and isinstance(title, list) and len(title) > 0:
            return title[0].get("plain_text", "未命名数据库")
        return "未命名数据库"
    
    def _get_page_title(self, page: dict) -> str:
        """提取页面标题"""
        properties = page.get("properties", {})
        
        # 查找标题属性
        for key, value in properties.items():
            if value.get("type") == "title":
                title_list = value.get("title", [])
                if title_list:
                    return title_list[0].get("plain_text", "未命名页面")
        
        return "未命名页面"
    
    def _get_database_properties(self, database: dict) -> dict:
        """获取数据库属性结构"""
        properties = database.get("properties", {})
        result = {}
        
        for name, prop in properties.items():
            result[name] = {
                "type": prop.get("type"),
                "name": name
            }
        
        return result

@router.post("/connect", response_model=ApiResponse)
async def connect_notion(
    request: NotionConnectRequest,
    current_user: dict = Depends(get_current_user)
):
    """连接 Notion 账户"""
    try:
        # 验证 token 有效性
        notion_service = NotionService(request.token)
        databases = await notion_service.get_databases()
        
        # TODO: 将 token 存储到用户配置中（加密存储）
        # 这里暂时不存储，只返回数据库列表
        
        return ApiResponse(
            success=True,
            data={
                "message": "Notion 连接成功",
                "databases_count": len(databases),
                "databases": databases[:10]  # 只返回前10个数据库作为预览
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"连接 Notion 失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notion 连接失败，请检查 Integration Token 是否正确"
        )

@router.get("/databases", response_model=ApiResponse)
async def get_notion_databases(
    token: str = Query(..., description="Notion Integration Token"),
    current_user: dict = Depends(get_current_user)
):
    """获取 Notion 数据库列表"""
    try:
        notion_service = NotionService(token)
        databases = await notion_service.get_databases()
        
        return ApiResponse(
            success=True,
            data={
                "databases": databases,
                "total": len(databases)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取 Notion 数据库列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取数据库列表失败"
        )

@router.get("/databases/{database_id}/pages", response_model=ApiResponse)
async def get_database_pages(
    database_id: str,
    token: str = Query(..., description="Notion Integration Token"),
    current_user: dict = Depends(get_current_user)
):
    """获取数据库中的页面"""
    try:
        notion_service = NotionService(token)
        pages = await notion_service.get_pages(database_id)
        
        return ApiResponse(
            success=True,
            data={
                "pages": pages,
                "total": len(pages)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取数据库页面失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取数据库页面失败"
        )

@router.get("/setup-guide", response_model=ApiResponse)
async def get_notion_setup_guide():
    """获取 Notion 集成设置指南"""
    return ApiResponse(
        success=True,
        data={
            "guide": {
                "title": "如何设置 Notion 集成",
                "steps": [
                    {
                        "step": 1,
                        "title": "创建 Notion Integration",
                        "description": "访问 https://www.notion.so/my-integrations",
                        "action": "点击 '+ New integration' 创建新的集成"
                    },
                    {
                        "step": 2,
                        "title": "配置集成信息",
                        "description": "填写集成名称（如：SimpleTimeTracker）",
                        "action": "选择关联的工作区，然后点击 'Submit'"
                    },
                    {
                        "step": 3,
                        "title": "获取 Integration Token",
                        "description": "复制显示的 Internal Integration Token",
                        "action": "妥善保存此 Token，它以 'secret_' 开头"
                    },
                    {
                        "step": 4,
                        "title": "共享数据库",
                        "description": "在 Notion 中打开要集成的数据库",
                        "action": "点击右上角 '...' → 'Connect to' → 选择你的 Integration"
                    },
                    {
                        "step": 5,
                        "title": "测试连接",
                        "description": "在下方输入框中粘贴 Integration Token",
                        "action": "点击 '连接 Notion' 按钮测试连接"
                    }
                ]
            }
        }
    )
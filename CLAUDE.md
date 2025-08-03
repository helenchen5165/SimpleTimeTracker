# Claude Code Project Rules for SimpleTimeTracker

## 项目概览
SimpleTimeTracker - 智能时间记录与目标管理系统 (Full-Stack Web版)
- **核心功能**: 基于Claude AI的自然语言时间解析和Notion数据存储
- **架构**: React + TypeScript前端 + FastAPI Python后端
- **版本**: v2.2 (2025-07-31)

## 重要配置信息
- **后端服务**: `python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000`
- **前端服务**: `cd frontend && npm run dev` (通常端口5173/5174)
- **认证方式**: JWT + 开发模式支持mock_token_*
- **数据库**: Notion API集成，使用.env中的配置

## 关键技术细节
- **解析引擎**: 集成原有time_agent.py的SimpleTimeAgent类
- **数据映射**: Task字段存储时间格式+描述，支出项存储活动名称
- **分类逻辑**: 使用activity_mapping进行生产/投资/支出三分类
- **API设计**: RESTful接口，/v1/time-records为核心端点

## 最近更新 (2025-07-30~31)
✅ 完成Full-Stack Web架构搭建
✅ 修复解析精度问题和数据库字段映射
✅ 实现前后端完整集成
✅ 保持与原有time_agent.py的100%兼容性

## 开发规则引用
@./agent-rules/project-rules/add-to-changelog.mdc
@./agent-rules/project-rules/analyze-issue.mdc
@./agent-rules/project-rules/bug-fix.mdc
@./agent-rules/project-rules/check.mdc
@./agent-rules/project-rules/clean.mdc
@./agent-rules/project-rules/code-analysis.mdc
@./agent-rules/project-rules/commit-fast.mdc
@./agent-rules/project-rules/commit.mdc
@./agent-rules/project-rules/context-prime.mdc
@./agent-rules/project-rules/continuous-improvement.mdc
@./agent-rules/project-rules/create-command.mdc
@./agent-rules/project-rules/create-docs.mdc
@./agent-rules/project-rules/cursor-rules-meta-guide.mdc
@./agent-rules/project-rules/five.mdc
@./agent-rules/project-rules/implement-task.mdc
@./agent-rules/project-rules/mcp-inspector-debugging.mdc
@./agent-rules/project-rules/mermaid.mdc
@./agent-rules/project-rules/modern-swift.mdc
@./agent-rules/project-rules/pr-review.mdc
@./agent-rules/project-rules/safari-automation.mdc
@./agent-rules/project-rules/screenshot-automation.mdc
@./agent-rules/project-rules/update-docs.mdc
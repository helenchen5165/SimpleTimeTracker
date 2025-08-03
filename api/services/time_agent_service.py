"""
时间记录智能解析服务 - 调用原有time_agent.py
"""

import sys
import os
import logging
from datetime import datetime, timedelta, date
from typing import Optional, List, Tuple
from notion_client import Client

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 导入原有的time_agent
from time_agent import SimpleTimeAgent

from api.config.settings import get_settings
from api.models.schemas import (
    Goal, GoalCreate, GoalUpdate,
    TimeRecord, TimeRecordCreate,
    DailyReport, WeeklyReport, DailyBreakdown, CompletedGoal,
    CategoryStats, ActivityStats, GoalProgress
)

logger = logging.getLogger(__name__)

class TimeAgentService:
    """时间记录智能解析服务 - 基于原有time_agent.py"""
    
    def __init__(self):
        """初始化服务"""
        self.settings = get_settings()
        
        # 初始化原有的SimpleTimeAgent
        self.time_agent = SimpleTimeAgent()
        
        # 初始化Notion客户端（用于API查询）
        self.notion = Client(auth=self.settings.notion_token)
    
    # =============== 目标管理服务 ===============
    
    async def get_active_goals(self, current_date: date = None) -> List[Goal]:
        """获取活跃目标列表"""
        if current_date is None:
            current_date = date.today()
        
        try:
            daily_goals = self.time_agent.query_active_goals(current_date)
            goals = []
            
            for dg in daily_goals:
                # 计算实际投入时间
                actual_time = self.time_agent.calculate_goal_actual_time(dg.goal_id)
                
                goal = Goal(
                    id=dg.goal_id,
                    title=dg.title,
                    deadline=dg.date,
                    estimated_time=dg.estimated_time,
                    actual_time=actual_time,
                    progress=min(100, int(actual_time / dg.estimated_time * 100)) if dg.estimated_time > 0 else 0,
                    priority=dg.priority,
                    status=dg.status,
                    created_at=datetime.now()  # 暂时使用当前时间，后续可从Notion获取
                )
                goals.append(goal)
            
            return goals
            
        except Exception as e:
            logger.error(f"获取活跃目标失败: {e}")
            raise
    
    async def create_goal(self, goal_data: GoalCreate) -> Goal:
        """创建目标 - 直接写入Notion Goals数据库"""
        try:
            # 构建Notion Goals数据库的属性
            properties = {
                "Goal Title": {
                    "title": [
                        {
                            "text": {
                                "content": goal_data.title
                            }
                        }
                    ]
                },
                "Deadline": {
                    "date": {
                        "start": goal_data.deadline.isoformat()
                    }
                },
                "Estimated Time": {
                    "number": goal_data.estimated_time
                },
                "Priority": {
                    "select": {
                        "name": goal_data.priority
                    }
                },
                "Status": {
                    "status": {
                        "name": "Planned"
                    }
                },
                "Progress": {
                    "number": 0
                }
            }
            
            # 创建Notion页面到Goals数据库
            response = self.notion.pages.create(
                parent={"database_id": self.settings.goals_database_id},
                properties=properties
            )
            
            # 构建返回的Goal对象
            goal = Goal(
                id=response["id"],
                title=goal_data.title,
                deadline=goal_data.deadline,
                estimated_time=goal_data.estimated_time,
                actual_time=0,
                progress=0,
                priority=goal_data.priority,
                status="Planned",
                created_at=response["created_time"]
            )
            
            logger.info(f"成功创建目标到Notion: {goal.title}")
            return goal
            
        except Exception as e:
            logger.error(f"创建目标失败: {e}")
            raise
    
    async def update_goal(self, goal_id: str, goal_data: GoalUpdate) -> Goal:
        """更新目标 - 直接更新Notion Goals数据库"""
        try:
            # 构建更新的属性（只更新提供的字段）
            properties = {}
            
            if goal_data.title:
                properties["Goal Title"] = {
                    "title": [{"text": {"content": goal_data.title}}]
                }
            
            if goal_data.deadline:
                properties["Deadline"] = {
                    "date": {"start": goal_data.deadline.isoformat()}
                }
            
            if goal_data.estimated_time:
                properties["Estimated Time"] = {
                    "number": goal_data.estimated_time
                }
            
            if goal_data.priority:
                properties["Priority"] = {
                    "select": {"name": goal_data.priority}
                }
            
            if goal_data.status:
                properties["Status"] = {
                    "status": {"name": goal_data.status}
                }
            
            # 更新Notion页面
            response = self.notion.pages.update(
                page_id=goal_id,
                properties=properties
            )
            
            # 获取更新后的完整数据来构建返回对象
            updated_props = response["properties"]
            
            # 提取更新后的数据
            title = ""
            if "Goal Title" in updated_props and updated_props["Goal Title"]["title"]:
                title = updated_props["Goal Title"]["title"][0]["text"]["content"]
            
            deadline_str = ""
            if "Deadline" in updated_props and updated_props["Deadline"]["date"]:
                deadline_str = updated_props["Deadline"]["date"]["start"]
            
            estimated_time = 0
            if "Estimated Time" in updated_props and updated_props["Estimated Time"]["number"]:
                estimated_time = updated_props["Estimated Time"]["number"]
            
            priority = "Medium"
            if "Priority" in updated_props and updated_props["Priority"]["select"]:
                priority = updated_props["Priority"]["select"]["name"]
            
            status = "Planned"
            if "Status" in updated_props and updated_props["Status"]["status"]:
                notion_status = updated_props["Status"]["status"]["name"]
                # 映射Notion状态值到API枚举
                status_mapping = {
                    "Planned": "Planned",
                    "In progress": "In Progress",  # Notion中可能是小写
                    "In Progress": "In Progress",
                    "Completed": "Completed",
                    "Abandoned": "Abandoned"
                }
                status = status_mapping.get(notion_status, "Planned")
            
            # 计算实际投入时间和进度
            actual_time = self.time_agent.calculate_goal_actual_time(goal_id)
            progress = min(100, int(actual_time / estimated_time * 100)) if estimated_time > 0 else 0
            
            goal = Goal(
                id=goal_id,
                title=title,
                deadline=date.fromisoformat(deadline_str.split('T')[0]),
                estimated_time=estimated_time,
                actual_time=actual_time,
                progress=progress,
                priority=priority,
                status=status,
                created_at=response["created_time"],
                updated_at=response["last_edited_time"]
            )
            
            logger.info(f"成功更新目标: {goal.title}")
            return goal
            
        except Exception as e:
            logger.error(f"更新目标失败: {e}")
            raise
    
    async def delete_goal(self, goal_id: str) -> bool:
        """删除目标 - 归档Notion页面（Notion不支持真删除）"""
        try:
            # Notion API不支持删除页面，只能归档
            response = self.notion.pages.update(
                page_id=goal_id,
                archived=True
            )
            
            logger.info(f"成功归档目标: {goal_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除目标失败: {e}")
            return False
    
    # =============== 时间记录服务 ===============
    
    async def create_time_record(self, record_data: TimeRecordCreate) -> TimeRecord:
        """创建时间记录 - 使用原有time_agent解析"""
        try:
            # 使用原有的time_agent解析逻辑
            parsed_data = self.time_agent.parse_natural_input(record_data.input_text)
            
            if not parsed_data:
                raise ValueError(f"原有解析引擎无法解析: {record_data.input_text}")
            
            # 从原有time_agent获取活动分类
            activity = parsed_data["activity"]
            category = self.time_agent.activity_mapping.get(activity, "支出")
            
            # 尝试匹配相关目标
            current_date = parsed_data["start_time"].date()
            matched_goal = self.time_agent.find_matching_goal(parsed_data["description"], current_date)
            
            # 构建完整的解析数据
            complete_data = {
                "activity": activity,
                "description": parsed_data["description"],
                "category": category,
                "start_time": parsed_data["start_time"],
                "end_time": parsed_data["end_time"],
                "duration_minutes": parsed_data["duration"],  # 原始返回duration，我们映射为duration_minutes
                "confidence": parsed_data.get("confidence", 0.95) * 100,  # 转换为百分比
                "parsing_method": "Claude"
            }
            
            # 保存到Notion（包含目标关联）
            goal_id = matched_goal.goal_id if matched_goal else None
            notion_page = await self._save_parsed_data_to_notion(complete_data, goal_id)
            
            # 如果匹配到目标，更新目标进度
            if matched_goal:
                actual_time = self.time_agent.calculate_goal_actual_time(matched_goal.goal_id)
                self.time_agent.update_goal_progress(matched_goal.goal_id, actual_time, matched_goal.estimated_time)
            
            # 构建matched_goal信息
            matched_goal_info = None
            if matched_goal:
                # 计算更新后的进度
                updated_actual_time = self.time_agent.calculate_goal_actual_time(matched_goal.goal_id)
                progress_percentage = min(100, int(updated_actual_time / matched_goal.estimated_time * 100)) if matched_goal.estimated_time > 0 else 0
                
                matched_goal_info = {
                    "id": matched_goal.goal_id,
                    "title": matched_goal.title,
                    "progress_after": updated_actual_time,
                    "progress_percentage": progress_percentage
                }
            
            # 创建时间记录对象
            record = TimeRecord(
                id=notion_page["id"],
                start_time=complete_data["start_time"].isoformat(),
                end_time=complete_data["end_time"].isoformat(),
                duration=complete_data["duration_minutes"],
                activity=complete_data["activity"],
                category=complete_data["category"],
                description=complete_data["description"],
                confidence=int(complete_data["confidence"]),
                parsing_method=complete_data["parsing_method"],
                matched_goal=matched_goal_info,
                created_at=notion_page["created_time"]
            )
            
            logger.info(f"创建时间记录到Notion: {record.activity} ({record.duration}分钟) - {record.category}")
            
            return record
            
        except Exception as e:
            logger.error(f"创建时间记录失败: {e}")
            raise ValueError(f"解析时间记录失败: {str(e)}")
    
    async def get_time_records(
        self, 
        target_date: date = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[TimeRecord], int]:
        """获取时间记录列表"""
        try:
            if target_date is None:
                target_date = date.today()
            
            # 从Notion数据库查询数据
            records = await self._fetch_from_notion(target_date, limit, offset)
            
            total = len(records)  # TODO: 获取真实的总数
            return records, total
            
        except Exception as e:
            logger.error(f"获取时间记录失败: {e}")
            raise
    
    async def get_time_record(self, record_id: str) -> Optional[TimeRecord]:
        """获取单个时间记录"""
        try:
            # 从Notion获取单个页面
            page = self.notion.pages.retrieve(page_id=record_id)
            record = await self._convert_notion_page_to_record(page)
            return record
        except Exception as e:
            logger.error(f"获取时间记录失败: {e}")
            return None
    
    async def update_time_record(self, record_id: str, update_data: dict) -> Optional[TimeRecord]:
        """更新时间记录"""
        try:
            # 构建更新的属性
            properties = {}
            
            # 如果更新了开始和结束时间，重新计算时长和Task字段
            if 'start_time' in update_data and 'end_time' in update_data:
                start_time = update_data['start_time']
                end_time = update_data['end_time']
                
                # 计算时长
                duration = int((end_time - start_time).total_seconds() / 60)
                
                # 更新Task字段格式
                description = update_data.get('description', '')
                task_format = f"{start_time.strftime('%m%d%H%M')}{end_time.strftime('%m%d%H%M')}{description}"
                
                properties.update({
                    "Task": {
                        "title": [{"text": {"content": task_format}}]
                    },
                    "Start Time": {
                        "date": {"start": start_time.isoformat()}
                    },
                    "End Time": {
                        "date": {"start": end_time.isoformat()}
                    },
                    "Duration (Minutes)": {
                        "rich_text": [{"text": {"content": str(duration)}}]
                    }
                })
            
            # 更新活动类型
            if 'activity' in update_data:
                properties["支出项"] = {
                    "select": {"name": update_data['activity']}
                }
            
            # 更新Notion页面
            updated_page = self.notion.pages.update(
                page_id=record_id,
                properties=properties
            )
            
            # 转换为TimeRecord对象
            record = await self._convert_notion_page_to_record(updated_page)
            
            logger.info(f"成功更新时间记录: {record_id}")
            return record
            
        except Exception as e:
            logger.error(f"更新时间记录失败: {e}")
            raise
    
    async def delete_time_record(self, record_id: str) -> bool:
        """删除时间记录（归档Notion页面）"""
        try:
            # Notion不支持真删除，只能归档
            self.notion.pages.update(
                page_id=record_id,
                archived=True
            )
            
            logger.info(f"成功删除（归档）时间记录: {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除时间记录失败: {e}")
            return False
    
    # =============== 报告统计服务 ===============
    
    async def generate_daily_report(self, target_date: date = None) -> DailyReport:
        """生成日报"""
        try:
            if target_date is None:
                target_date = date.today()
            
            # 获取当日的时间记录
            records, _ = await self.get_time_records(target_date)
            
            # 计算基础统计
            total_records = len(records)
            total_duration = sum(record.duration for record in records)
            
            # 计算分类统计
            category_stats = {}
            category_duration = {}
            
            for record in records:
                category = record.category
                if category not in category_duration:
                    category_duration[category] = 0
                category_duration[category] += record.duration
            
            # 转换为百分比
            for category, duration in category_duration.items():
                percentage = (duration / total_duration * 100) if total_duration > 0 else 0
                category_stats[category] = CategoryStats(duration=duration, percentage=round(percentage, 1))
            
            # 计算活动统计
            activity_duration = {}
            for record in records:
                activity = record.activity
                if activity not in activity_duration:
                    activity_duration[activity] = 0
                activity_duration[activity] += record.duration
            
            activity_stats = [
                ActivityStats(activity=activity, duration=duration)
                for activity, duration in sorted(activity_duration.items(), key=lambda x: x[1], reverse=True)
            ]
            
            # 计算有效率（生产+投资类别的占比）
            productive_duration = category_duration.get("生产", 0) + category_duration.get("投资", 0)
            efficiency_rate = (productive_duration / total_duration * 100) if total_duration > 0 else 0
            
            # 获取目标进度
            goal_progress = []
            try:
                active_goals = await self.get_active_goals(target_date)
                for goal in active_goals:
                    if goal.actual_time > 0:  # 只显示有进度的目标
                        goal_progress.append(GoalProgress(
                            goal_id=goal.id,
                            title=goal.title,
                            progress=goal.actual_time,
                            estimated=goal.estimated_time,
                            percentage=goal.progress
                        ))
            except Exception as e:
                logger.warning(f"获取目标进度失败: {e}")
            
            report = DailyReport(
                report_date=target_date,
                total_records=total_records,
                total_duration=total_duration,
                efficiency_rate=round(efficiency_rate, 1),
                category_stats=category_stats,
                activity_stats=activity_stats,
                goal_progress=goal_progress
            )
            
            logger.info(f"生成日报成功: {target_date}, {total_records}条记录, {total_duration}分钟")
            return report
            
        except Exception as e:
            logger.error(f"生成日报失败: {e}")
            raise
    
    async def generate_weekly_report(self, week_date: date = None) -> WeeklyReport:
        """生成周报"""
        try:
            if week_date is None:
                week_date = date.today()
            
            # 计算周的开始和结束日期
            weekday = week_date.weekday()  # 0是周一，6是周日
            week_start = week_date - timedelta(days=weekday)
            week_end = week_start + timedelta(days=6)
            
            # 生成周标识
            week_str = f"{week_start.year}-W{week_start.isocalendar()[1]:02d}"
            
            # 收集一周内每日的数据
            daily_breakdown = []
            weekly_records = []
            
            for i in range(7):
                day = week_start + timedelta(days=i)
                try:
                    day_records, _ = await self.get_time_records(day)
                    daily_duration = sum(record.duration for record in day_records)
                    
                    daily_breakdown.append(DailyBreakdown(
                        breakdown_date=day,
                        duration=daily_duration
                    ))
                    
                    weekly_records.extend(day_records)
                except Exception as e:
                    logger.warning(f"获取{day}的记录失败: {e}")
                    daily_breakdown.append(DailyBreakdown(
                        breakdown_date=day,
                        duration=0
                    ))
            
            # 计算周总统计
            total_duration = sum(record.duration for record in weekly_records)
            
            # 计算分类汇总
            category_summary = {}
            category_duration = {}
            
            for record in weekly_records:
                category = record.category
                if category not in category_duration:
                    category_duration[category] = 0
                category_duration[category] += record.duration
            
            for category, duration in category_duration.items():
                percentage = (duration / total_duration * 100) if total_duration > 0 else 0
                category_summary[category] = CategoryStats(duration=duration, percentage=round(percentage, 1))
            
            # 计算有效率
            productive_duration = category_duration.get("生产", 0) + category_duration.get("投资", 0)
            efficiency_rate = (productive_duration / total_duration * 100) if total_duration > 0 else 0
            
            # 获取本周完成的目标
            completed_goals = []
            try:
                active_goals = await self.get_active_goals(week_end)
                for goal in active_goals:
                    # 检查目标是否在本周完成（简化逻辑：实际时间>=预估时间）
                    if goal.actual_time >= goal.estimated_time and goal.status == "Completed":
                        completed_goals.append(CompletedGoal(
                            title=goal.title,
                            estimated_time=goal.estimated_time,
                            actual_time=goal.actual_time
                        ))
            except Exception as e:
                logger.warning(f"获取完成目标失败: {e}")
            
            report = WeeklyReport(
                week=week_str,
                date_range=[week_start, week_end],
                total_duration=total_duration,
                efficiency_rate=round(efficiency_rate, 1),
                daily_breakdown=daily_breakdown,
                category_summary=category_summary,
                completed_goals=completed_goals
            )
            
            logger.info(f"生成周报成功: {week_str}, 总时长{total_duration}分钟")
            return report
            
        except Exception as e:
            logger.error(f"生成周报失败: {e}")
            raise
    
    # =============== 智能解析服务 (使用原有time_agent.py) ===============
    
    # =============== Notion 集成方法 ===============
    
    async def _save_parsed_data_to_notion(self, parsed_data: dict, goal_id: str = None) -> dict:
        """保存原有time_agent解析结果到Notion数据库"""
        try:
            # 按照原有time_agent.py的逻辑构建数据
            start_time = parsed_data["start_time"]
            end_time = parsed_data["end_time"]
            activity = parsed_data["activity"]
            description = parsed_data["description"]
            
            # 生成task格式: mmddHHmmmmddHHmm + description（与原有time_agent.py一致）
            task_format = f"{start_time.strftime('%m%d%H%M')}{end_time.strftime('%m%d%H%M')}{description}"
            
            # 构建Notion页面属性
            properties = {
                "Task": {
                    "title": [
                        {
                            "text": {
                                "content": task_format
                            }
                        }
                    ]
                },
                "支出项": {
                    "select": {
                        "name": activity  # 支出项存储活动名称（如：编程）
                    }
                },
                "Duration (Minutes)": {
                    "number": parsed_data["duration_minutes"]
                },
                "Start Time": {
                    "date": {
                        "start": start_time.isoformat()
                    }
                },
                "End Time": {
                    "date": {
                        "start": end_time.isoformat()
                    }
                }
                # 注意：不写入"性质"字段，由Notion函数自动计算
            }
            
            # 如果有关联目标，添加Goal关系
            if goal_id:
                properties["Goal"] = {
                    "relation": [{"id": goal_id}]
                }
            
            # 创建Notion页面
            response = self.notion.pages.create(
                parent={"database_id": self.settings.database_id},
                properties=properties
            )
            
            logger.info(f"成功保存到Notion: {response['id']}")
            return response
            
        except Exception as e:
            logger.error(f"保存到Notion失败: {e}")
            raise
    
    
    async def _fetch_from_notion(self, target_date: date, limit: int, offset: int) -> List[TimeRecord]:
        """从Notion数据库获取时间记录"""
        try:
            # 构建查询过滤器
            filter_conditions = {
                "and": [
                    {
                        "property": "Start Time",
                        "date": {
                            "on_or_after": target_date.isoformat()
                        }
                    },
                    {
                        "property": "Start Time", 
                        "date": {
                            "before": (target_date + timedelta(days=1)).isoformat()
                        }
                    }
                ]
            }
            
            # 查询Notion数据库
            response = self.notion.databases.query(
                database_id=self.settings.database_id,
                filter=filter_conditions,
                sorts=[
                    {
                        "property": "Start Time",
                        "direction": "descending"
                    }
                ],
                start_cursor=None,  # TODO: 实现分页
                page_size=limit
            )
            
            records = []
            for page in response["results"]:
                record = await self._convert_notion_page_to_record(page)
                if record:
                    records.append(record)
            
            logger.info(f"从Notion获取到 {len(records)} 条记录")
            return records
            
        except Exception as e:
            logger.error(f"从Notion获取数据失败: {e}")
            return []  # 返回空列表而不是抛出异常
    
    async def _convert_notion_page_to_record(self, page: dict) -> Optional[TimeRecord]:
        """将Notion页面转换为TimeRecord对象"""
        try:
            props = page["properties"]
            
            # 提取Task字段（格式：mmddHHmmmmddHHmm + description）
            task_content = ""
            if "Task" in props and props["Task"]["title"]:
                task_content = props["Task"]["title"][0]["text"]["content"]
            
            # 从Task字段中提取description（去掉时间格式部分）
            description = ""
            if task_content:
                # Task格式：mmddHHmmmmddHHmm + description，时间部分是16位数字
                import re
                match = re.match(r'^\d{16}(.*)$', task_content)
                if match:
                    description = match.group(1)
                else:
                    description = task_content  # 如果格式不匹配，使用原始内容
            
            # 从支出项字段获取活动名称
            activity = ""
            if "支出项" in props and props["支出项"]["select"]:
                activity = props["支出项"]["select"]["name"]
            
            # 从activity_mapping获取分类
            category = ""
            if activity:
                # 这里需要重新映射分类，因为支出项存储的是活动名称
                category = self.time_agent.activity_mapping.get(activity, "支出")
            
            # 提取时间信息
            start_time = ""
            end_time = ""
            duration = 0
            
            if "Start Time" in props and props["Start Time"]["date"]:
                start_time = props["Start Time"]["date"]["start"]
            
            if "End Time" in props and props["End Time"]["date"]:
                end_time = props["End Time"]["date"]["start"]
            
            if "Duration (Minutes)" in props and props["Duration (Minutes)"]["number"] is not None:
                try:
                    duration = int(props["Duration (Minutes)"]["number"])
                except (ValueError, TypeError):
                    duration = 0
            
            confidence = 95  # 默认置信度
            parsing_method = "Claude"  # 解析方法
            
            # 创建TimeRecord对象
            record = TimeRecord(
                id=page["id"],
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                activity=activity,
                category=category,
                description=description,
                confidence=confidence,
                parsing_method=parsing_method,
                matched_goal=None,  # TODO: 实现目标匹配
                created_at=page["created_time"]
            )
            
            return record
            
        except Exception as e:
            logger.error(f"转换Notion页面失败: {e}")
            return None
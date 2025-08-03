#!/usr/bin/env python3
"""
SimpleTimeTracker - 简化版智能时间记录工具
支持Claude AI自然语言解析、Notion数据存储、报告生成
"""

import os
import json
import datetime
import logging
import argparse
import re
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass
import pytz
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入依赖库
try:
    from notion_client import Client as NotionClient
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    logging.error("notion-client未安装，请运行: pip install notion-client")

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    logging.error("anthropic未安装，请运行: pip install anthropic")

# 配置日志
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TimeRecord:
    """时间记录数据类"""
    start_time: datetime.datetime
    end_time: datetime.datetime
    activity: str
    description: str
    category: str
    duration: int  # 分钟
    confidence: float = 1.0

@dataclass
class DailyGoal:
    """目标数据类（基于deadline管理）"""
    goal_id: str
    title: str
    date: datetime.date  # 截止日期(deadline)
    estimated_time: int  # 预估总时长（分钟）
    priority: str
    status: str
    progress: int  # 0-100
    actual_time: int = 0  # 实际投入时间

class SimpleTimeAgent:
    """简化版时间记录AI助手"""
    
    def __init__(self):
        """初始化配置和客户端"""
        self.load_config()
        self.init_clients()
        self.init_activity_mapping()
        
    def load_config(self):
        """加载环境配置"""
        # Notion配置
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.database_id = os.getenv('DATABASE_ID')
        self.goals_database_id = os.getenv('GOALS_DATABASE_ID')
        self.page_id = os.getenv('PAGE_ID')
        
        # Claude配置
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.claude_model = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
        self.claude_max_tokens = int(os.getenv('CLAUDE_MAX_TOKENS', '1000'))
        self.claude_temperature = float(os.getenv('CLAUDE_TEMPERATURE', '0.1'))
        
        # 时区配置
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Shanghai'))
        
        # 验证必要配置
        if not self.notion_token or not self.database_id:
            raise ValueError("缺少Notion配置: NOTION_TOKEN, DATABASE_ID")
        if not self.goals_database_id:
            logger.warning("缺少Goals数据库配置: GOALS_DATABASE_ID，将禁用目标管理功能")
        if not self.anthropic_api_key:
            logger.warning("缺少Claude配置: ANTHROPIC_API_KEY，将禁用AI解析功能")
            
    def init_clients(self):
        """初始化API客户端"""
        # Notion客户端
        if NOTION_AVAILABLE and self.notion_token:
            self.notion = NotionClient(auth=self.notion_token)
            logger.info("✅ Notion客户端初始化成功")
        else:
            self.notion = None
            logger.error("❌ Notion客户端初始化失败")
            
        # Claude客户端
        if CLAUDE_AVAILABLE and self.anthropic_api_key:
            self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            logger.info("✅ Claude客户端初始化成功")
        else:
            self.claude_client = None
            logger.warning("⚠️ Claude客户端未初始化，将使用规则引擎解析")
            
    def init_activity_mapping(self):
        """初始化活动分类映射"""
        # 从环境变量加载活动分类
        production_activities = os.getenv('PRODUCTION_ACTIVITIES', '').split(',')
        investment_activities = os.getenv('INVESTMENT_ACTIVITIES', '').split(',')
        expense_activities = os.getenv('EXPENSE_ACTIVITIES', '').split(',')
        
        self.activity_mapping = {}
        
        # 生产类活动
        for activity in production_activities:
            if activity.strip():
                self.activity_mapping[activity.strip()] = '生产'
                
        # 投资类活动  
        for activity in investment_activities:
            if activity.strip():
                self.activity_mapping[activity.strip()] = '投资'
                
        # 支出类活动
        for activity in expense_activities:
            if activity.strip():
                self.activity_mapping[activity.strip()] = '支出'
                
        logger.info(f"✅ 加载了 {len(self.activity_mapping)} 个活动分类")
        
    def parse_with_claude(self, text: str) -> Optional[Dict[str, Any]]:
        """使用Claude AI解析自然语言时间记录"""
        if not self.claude_client:
            return None
            
        try:
            # 构建解析提示词
            prompt = f"""
请解析以下时间记录文本，返回JSON格式的结构化数据：

输入文本: "{text}"

当前时间: {datetime.datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}

请返回以下JSON格式:
{{
    "start_time": "YYYY-MM-DDTHH:MM:SS",
    "end_time": "YYYY-MM-DDTHH:MM:SS", 
    "activity": "活动名称",
    "description": "详细描述",
    "confidence": 0.95
}}

可识别的活动类型: {', '.join(self.activity_mapping.keys())}

解析规则:
1. 识别时间范围（开始和结束时间）
2. 提取活动类型（必须从可识别列表中选择最相近的）
3. 生成描述文本
4. 评估解析置信度(0-1)
5. 如果是相对时间("2小时前"等)，基于当前时间计算绝对时间
6. 时间格式必须是ISO格式

只返回JSON，不要其他文字。
"""
            
            response = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=self.claude_max_tokens,
                temperature=self.claude_temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析JSON响应
            content = response.content[0].text.strip()
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
                
            result = json.loads(content)
            
            # 验证和转换时间格式
            start_time = datetime.datetime.fromisoformat(result['start_time'])
            end_time = datetime.datetime.fromisoformat(result['end_time'])
            
            # 设置时区
            if start_time.tzinfo is None:
                start_time = self.timezone.localize(start_time)
            if end_time.tzinfo is None:
                end_time = self.timezone.localize(end_time)
                
            result['start_time'] = start_time
            result['end_time'] = end_time
            result['duration'] = int((end_time - start_time).total_seconds() / 60)
            
            logger.info(f"🤖 Claude解析成功: {result['activity']} ({result['confidence']:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Claude解析失败: {e}")
            return None
            
    def parse_with_rules(self, text: str) -> Optional[Dict[str, Any]]:
        """使用规则引擎解析时间记录"""
        try:
            # 简单的时间模式匹配
            patterns = [
                # 13点到13点40编程 (带分钟)
                r'(\d{1,2})点到(\d{1,2})点(\d{1,2})(.+)',
                # 7点到9点阅读
                r'(\d{1,2})点到(\d{1,2})点(.+)',
                # 14:30-16:00编程
                r'(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})(.+)',
                # 上午9点到11点开会
                r'上午(\d{1,2})点到(\d{1,2})点(.+)',
                # 晚上8点到9点运动
                r'晚上(\d{1,2})点到(\d{1,2})点(.+)'
            ]
            
            for pattern in patterns:
                match = re.match(pattern, text.strip())
                if match:
                    return self._parse_matched_pattern(match, text)
                    
            return None
            
        except Exception as e:
            logger.error(f"❌ 规则解析失败: {e}")
            return None
            
    def _parse_matched_pattern(self, match, original_text: str) -> Dict[str, Any]:
        """解析匹配的时间模式"""
        groups = match.groups()
        now = datetime.datetime.now(self.timezone)
        today = now.date()
        
        if len(groups) == 4:  # 新模式: 13点到13点40编程
            start_hour = int(groups[0])
            end_hour = int(groups[1])
            end_minute = int(groups[2])
            activity_text = groups[3].strip()
            
            start_time = self.timezone.localize(
                datetime.datetime.combine(today, datetime.time(start_hour, 0))
            )
            end_time = self.timezone.localize(
                datetime.datetime.combine(today, datetime.time(end_hour, end_minute))
            )
            
        elif len(groups) == 3:  # 简单模式: 7点到9点阅读
            start_hour = int(groups[0])
            end_hour = int(groups[1])
            activity_text = groups[2].strip()
            
            start_time = self.timezone.localize(
                datetime.datetime.combine(today, datetime.time(start_hour, 0))
            )
            end_time = self.timezone.localize(
                datetime.datetime.combine(today, datetime.time(end_hour, 0))
            )
            
        elif len(groups) == 5:  # 时分模式: 14:30-16:00编程
            start_hour, start_min = int(groups[0]), int(groups[1])
            end_hour, end_min = int(groups[2]), int(groups[3])
            activity_text = groups[4].strip()
            
            start_time = self.timezone.localize(
                datetime.datetime.combine(today, datetime.time(start_hour, start_min))
            )
            end_time = self.timezone.localize(
                datetime.datetime.combine(today, datetime.time(end_hour, end_min))
            )
            
        # 匹配活动类型
        activity = self._match_activity(activity_text)
        
        return {
            'start_time': start_time,
            'end_time': end_time,
            'activity': activity,
            'description': activity_text,
            'duration': int((end_time - start_time).total_seconds() / 60),
            'confidence': 0.8
        }
        
    def _match_activity(self, text: str) -> str:
        """匹配活动类型"""
        for activity in self.activity_mapping.keys():
            if activity in text:
                return activity
        return '其他'
        
    def parse_natural_input(self, text: str) -> Optional[Dict[str, Any]]:
        """解析自然语言输入（优先Claude策略）"""
        logger.info(f"🔍 开始解析: {text}")
        
        # 优先使用Claude AI（准确性高）
        claude_result = self.parse_with_claude(text)
        
        # 如果Claude失败，使用规则引擎作为备选
        if not claude_result:
            rule_result = self.parse_with_rules(text)
            if rule_result:
                logger.info("⚙️ Claude解析失败，使用规则引擎")
                return rule_result
        else:
            logger.info("🤖 使用Claude解析")
            return claude_result
            
        logger.error(f"❌ 无法解析输入: {text}")
        return None
        
    def save_to_notion(self, data: Dict[str, Any], goal_id: Optional[str] = None) -> bool:
        """保存时间记录到Notion数据库"""
        if not self.notion:
            logger.error("❌ Notion客户端未初始化")
            return False
            
        try:
            # 构建Notion格式的数据
            start_time = data['start_time']
            end_time = data['end_time']
            activity = data['activity']
            description = data.get('description', '')
            
            # 生成task格式: mmddHHmmmmddHHmm行为
            task_format = f"{start_time.strftime('%m%d%H%M')}{end_time.strftime('%m%d%H%M')}{description}"
            
            # 获取活动分类
            category = self.activity_mapping.get(activity, '支出')
            
            # 创建Notion页面 - Start Time和End Time现在是Date类型，可以写入
            properties = {
                "Task": {"title": [{"text": {"content": task_format}}]},
                "支出项": {"select": {"name": activity}},
                "Duration (Minutes)": {"number": data['duration']},
                "Start Time": {"date": {"start": start_time.isoformat()}},
                "End Time": {"date": {"start": end_time.isoformat()}}
            }
            
            # 如果有关联目标，添加Goal关系
            if goal_id:
                properties["Goal"] = {"relation": [{"id": goal_id}]}
            
            response = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            logger.info(f"✅ 成功保存到Notion: {activity} ({data['duration']}分钟)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存到Notion失败: {e}")
            return False
            
    def process_single_input(self, text: str) -> bool:
        """处理单条输入（集成目标管理）"""
        # 解析输入
        parsed_data = self.parse_natural_input(text)
        if not parsed_data:
            print(f"❌ 解析失败: {text}")
            return False
            
        # 智能匹配目标
        matched_goal = None
        if self.goals_database_id:
            record_date = parsed_data['start_time'].date()
            matched_goal = self.find_matching_goal(parsed_data['description'], record_date)
        
        # 保存到Notion（包含目标关联）
        goal_id = matched_goal.goal_id if matched_goal else None
        success = self.save_to_notion(parsed_data, goal_id)
        
        if success:
            # 如果匹配到目标，更新目标进度
            if matched_goal:
                # 计算目标实际投入时间
                actual_time = self.calculate_goal_actual_time(matched_goal.goal_id)
                # 更新目标进度
                self.update_goal_progress(matched_goal.goal_id, actual_time, matched_goal.estimated_time)
            
            # 输出成功信息
            start_time = parsed_data['start_time']
            end_time = parsed_data['end_time']
            activity = parsed_data['activity']
            duration = parsed_data['duration']
            confidence = parsed_data.get('confidence', 1.0)
            category = self.activity_mapping.get(activity, '支出')
            
            print(f"✅ 记录成功! ({'🤖 Claude解析' if confidence > 0.9 else '⚙️ 规则解析'})")
            print(f"📅 时间: {start_time.strftime('%m/%d %H:%M')} - {end_time.strftime('%H:%M')}")
            print(f"⏱️ 时长: {duration}分钟")
            print(f"🏷️ 活动: {activity} ({category})")
            print(f"📝 描述: {parsed_data.get('description', '')}")
            
            # 显示目标关联信息
            if matched_goal:
                actual_time = self.calculate_goal_actual_time(matched_goal.goal_id)
                progress = min(100, int(actual_time / matched_goal.estimated_time * 100)) if matched_goal.estimated_time > 0 else 0
                print(f"🎯 关联目标: {matched_goal.title}")
                print(f"📊 目标进度: {actual_time}/{matched_goal.estimated_time}分钟 ({progress}%)")
                print(f"⏰ 截止日期: {matched_goal.date.strftime('%m/%d')}")
            
            print(f"🟢 识别置信度: {confidence*100:.0f}%")
            return True
        else:
            print(f"❌ 保存失败: {text}")
            return False
            
    def process_batch_file(self, file_path: str) -> Tuple[int, int]:
        """处理批量文件输入"""
        success_count = 0
        total_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            print(f"📄 开始处理批量文件: {file_path}")
            print(f"📝 共 {len(lines)} 条记录")
            print("-" * 50)
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # 跳过空行和注释
                    continue
                    
                total_count += 1
                print(f"[{i}/{len(lines)}] 处理: {line}")
                
                if self.process_single_input(line):
                    success_count += 1
                    print()
                else:
                    print("⚠️ 处理失败\n")
                    
            print("-" * 50)
            print(f"📊 批量处理完成: {success_count}/{total_count} 成功")
            return success_count, total_count
            
        except FileNotFoundError:
            print(f"❌ 文件不存在: {file_path}")
            return 0, 0
        except Exception as e:
            print(f"❌ 批量处理失败: {e}")
            return 0, 0
    
    # ==================== 目标管理功能 ====================
    
    def query_active_goals(self, current_date: datetime.date) -> List[DailyGoal]:
        """查询活跃目标（截止日期>=今天且未完成）"""
        if not self.notion or not self.goals_database_id:
            logger.warning("Goals数据库未配置，无法查询目标")
            return []
            
        try:
            # 构建查询条件：截止日期>=今天 且 状态!=Completed
            filter_condition = {
                "and": [
                    {
                        "property": "Deadline",
                        "date": {
                            "on_or_after": current_date.isoformat()
                        }
                    },
                    {
                        "property": "Status", 
                        "status": {
                            "does_not_equal": "Completed"
                        }
                    }
                ]
            }
            
            response = self.notion.databases.query(
                database_id=self.goals_database_id,
                filter=filter_condition
            )
            
            goals = []
            for page in response.get('results', []):
                try:
                    props = page['properties']
                    
                    # 提取目标数据
                    title = props.get('Goal Title', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                    if not title:  # 如果Goal Title为空，尝试从主标题获取
                        title = props.get('Goal Title', {}).get('title', [{}])[0].get('plain_text', '')
                    
                    date_str = props.get('Deadline', {}).get('date', {}).get('start', '')
                    estimated_time = props.get('Estimated Time', {}).get('number', 0)
                    priority = props.get('Priority', {}).get('select', {}).get('name', 'Medium')
                    status = props.get('Status', {}).get('status', {}).get('name', 'Planned')
                    progress = props.get('Progress', {}).get('number', 0)
                    
                    if title and date_str:
                        goal_date = datetime.datetime.fromisoformat(date_str).date()
                        goals.append(DailyGoal(
                            goal_id=page['id'],
                            title=title,
                            date=goal_date,
                            estimated_time=estimated_time or 0,
                            priority=priority,
                            status=status,
                            progress=progress or 0
                        ))
                        
                except Exception as e:
                    logger.warning(f"解析目标记录失败: {e}")
                    continue
                    
            logger.info(f"📋 查询到 {len(goals)} 个目标")
            return goals
            
        except Exception as e:
            logger.error(f"❌ 查询目标失败: {e}")
            return []
    
    def find_matching_goal(self, activity_text: str, current_date: datetime.date) -> Optional[DailyGoal]:
        """智能匹配时间记录与活跃目标（基于deadline逻辑）"""
        goals = self.query_active_goals(current_date)
        if not goals:
            return None
            
        # 简单关键词匹配
        activity_lower = activity_text.lower()
        best_match = None
        best_score = 0
        
        for goal in goals:
            goal_lower = goal.title.lower()
            
            # 计算匹配分数 - 双向匹配
            score = 0
            
            # 方向1：活动描述的词在目标中
            words = activity_lower.split()
            for word in words:
                if len(word) > 1 and word in goal_lower:
                    score += len(word)
            
            # 方向2：目标的词在活动描述中
            goal_words = goal_lower.split()
            for word in goal_words:
                if len(word) > 1 and word in activity_lower:
                    score += len(word)
            
            if score > best_score:
                best_score = score
                best_match = goal
                
        # 需要至少2分的匹配分数
        if best_score >= 2:
            logger.info(f"🎯 找到匹配目标: {activity_text} -> {best_match.title} (分数: {best_score})")
            return best_match
        else:
            logger.info(f"🔍 未找到匹配目标: {activity_text}")
            return None
    
    def calculate_goal_actual_time(self, goal_id: str) -> int:
        """计算目标的实际投入时间"""
        if not self.notion:
            return 0
            
        try:
            # 查询关联到此目标的所有时间记录
            filter_condition = {
                "property": "Goal",
                "relation": {
                    "contains": goal_id
                }
            }
            
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter=filter_condition
            )
            
            total_time = 0
            for page in response.get('results', []):
                props = page['properties']
                
                # 使用Duration (Minutes)字段 - 现在是number类型
                duration_number = props.get('Duration (Minutes)', {}).get('number')
                if duration_number is not None:
                    try:
                        duration = int(duration_number)
                        total_time += duration
                    except:
                        continue
                        
            return total_time
            
        except Exception as e:
            logger.error(f"❌ 计算目标时间失败: {e}")
            return 0
    
    def update_goal_progress(self, goal_id: str, actual_time: int, estimated_time: int) -> bool:
        """更新目标进度和状态"""
        if not self.notion:
            return False
            
        try:
            # 计算进度百分比
            if estimated_time > 0:
                time_progress = min(100, int(actual_time / estimated_time * 100))
            else:
                time_progress = 0
            
            # 确定状态
            if actual_time == 0:
                status = "Planned"
                progress = 0
            elif time_progress >= 100:
                status = "Completed"
                progress = 100
            else:
                status = "In Progress"
                progress = time_progress
            
            # 更新Notion
            properties = {
                "Status": {"status": {"name": status}},
                "Progress": {"number": progress}
            }
            
            self.notion.pages.update(
                page_id=goal_id,
                properties=properties
            )
            
            logger.info(f"📊 目标进度已更新: {progress}% ({status})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新目标进度失败: {e}")
            return False
            
    def interactive_mode(self):
        """交互模式"""
        print("🤖 SimpleTimeTracker 交互模式")
        print("输入时间记录，或输入 'quit' 退出")
        print("支持格式: '7点到9点阅读', '14:30-16:00编程' 等")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n📝 请输入时间记录: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q', '退出']:
                    print("👋 再见!")
                    break
                    
                if not user_input:
                    continue
                    
                self.process_single_input(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 输入处理错误: {e}")
                
    def query_notion_data(self, start_date: datetime.date, end_date: datetime.date) -> List[Dict]:
        """查询Notion数据库中的时间记录"""
        if not self.notion:
            return []
            
        try:
            # 构建查询条件
            filter_condition = {
                "and": [
                    {
                        "property": "Start Time",
                        "date": {
                            "on_or_after": start_date.isoformat()
                        }
                    },
                    {
                        "property": "Start Time", 
                        "date": {
                            "on_or_before": end_date.isoformat()
                        }
                    }
                ]
            }
            
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter=filter_condition
            )
            
            records = []
            for page in response.get('results', []):
                try:
                    props = page['properties']
                    
                    # 提取数据
                    task = props.get('Task', {}).get('title', [{}])[0].get('text', {}).get('content', '')
                    expense_item = props.get('支出项', {}).get('select', {})
                    expense_item = expense_item.get('name', '') if expense_item else ''
                    
                    start_time_str = props.get('Start Time', {}).get('date', {}).get('start', '')
                    end_time_str = props.get('End Time', {}).get('date', {}).get('start', '')
                    
                    # 计算duration（如果有开始和结束时间）
                    duration = 0
                    if start_time_str and end_time_str:
                        try:
                            start_dt = datetime.datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                            end_dt = datetime.datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                            duration = int((end_dt - start_dt).total_seconds() / 60)
                        except:
                            duration = 0
                    
                    # 根据活动类型推断category
                    category = self.activity_mapping.get(expense_item, '支出')
                    
                    if start_time_str and end_time_str:
                        records.append({
                            'task': task,
                            'expense_item': expense_item,
                            'start_time': datetime.datetime.fromisoformat(start_time_str.replace('Z', '+00:00')),
                            'end_time': datetime.datetime.fromisoformat(end_time_str.replace('Z', '+00:00')),
                            'duration': duration or 0,
                            'category': category
                        })
                        
                except Exception as e:
                    logger.warning(f"解析记录失败: {e}")
                    continue
                    
            logger.info(f"📊 查询到 {len(records)} 条记录")
            return records
            
        except Exception as e:
            logger.error(f"❌ 查询Notion数据失败: {e}")
            return []
            
    def generate_daily_report(self, target_date: Optional[datetime.date] = None) -> str:
        """生成日报（控制台输出）"""
        if target_date is None:
            target_date = datetime.date.today()
            
        print(f"📊 生成日报: {target_date.strftime('%Y-%m-%d')}")
        print("=" * 60)
        
        # 查询当日数据
        records = self.query_notion_data(target_date, target_date)
        
        if not records:
            report = f"📅 {target_date.strftime('%Y-%m-%d')} 暂无时间记录"
            print(report)
            return report
            
        # 统计数据
        total_duration = sum(record['duration'] for record in records)
        category_stats = {}
        activity_stats = {}
        
        for record in records:
            category = record['category'] or '未分类'
            activity = record['expense_item'] or '未知活动'
            duration = record['duration']
            
            category_stats[category] = category_stats.get(category, 0) + duration
            activity_stats[activity] = activity_stats.get(activity, 0) + duration
            
        # 生成报告
        report_lines = [
            f"📅 日期: {target_date.strftime('%Y-%m-%d')}",
            f"📝 记录条数: {len(records)}",
            f"⏱️ 总时长: {total_duration}分钟 ({total_duration/60:.1f}小时)",
            f"📊 有效率: {total_duration/1440*100:.1f}% (基于24小时)",
            "",
            "📈 分类统计:",
        ]
        
        # 分类统计
        for category, duration in sorted(category_stats.items()):
            percentage = duration / total_duration * 100 if total_duration > 0 else 0
            report_lines.append(f"  • {category}: {duration}分钟 ({duration/60:.1f}小时, {percentage:.1f}%)")
            
        report_lines.extend(["", "🏷️ 活动统计:"])
        
        # 活动统计（按时长排序）
        for activity, duration in sorted(activity_stats.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"  • {activity}: {duration}分钟")
            
        report_lines.extend(["", "📋 详细记录:"])
        
        # 详细记录（按时间排序）
        sorted_records = sorted(records, key=lambda x: x['start_time'])
        for record in sorted_records:
            start_time = record['start_time'].strftime('%H:%M')
            end_time = record['end_time'].strftime('%H:%M') 
            activity = record['expense_item']
            duration = record['duration']
            report_lines.append(f"  {start_time}-{end_time} {activity} ({duration}分钟)")
            
        report = '\n'.join(report_lines)
        print(report)
        return report
        
    def generate_weekly_report(self, target_date: Optional[datetime.date] = None) -> bool:
        """生成周报（保存到Notion页面）"""
        if target_date is None:
            target_date = datetime.date.today()
            
        # 计算本周的开始和结束日期（周一到周日）
        days_since_monday = target_date.weekday()
        week_start = target_date - datetime.timedelta(days=days_since_monday)
        week_end = week_start + datetime.timedelta(days=6)
        
        print(f"📊 生成周报: {week_start} 到 {week_end}")
        
        # 查询本周数据
        records = self.query_notion_data(week_start, week_end)
        
        if not records:
            print("❌ 本周暂无时间记录")
            return False
            
        # 统计数据
        total_duration = sum(record['duration'] for record in records)
        week_total_minutes = 7 * 24 * 60  # 一周总分钟数
        unrecorded_minutes = week_total_minutes - total_duration
        effective_rate = total_duration / week_total_minutes * 100
        
        category_stats = {}
        activity_stats = {}
        
        for record in records:
            category = record['category'] or '支出'
            activity = record['expense_item'] or '未知活动'
            duration = record['duration']
            
            category_stats[category] = category_stats.get(category, 0) + duration
            activity_stats[activity] = activity_stats.get(activity, 0) + duration
            
        # 计算分类比例
        production_time = category_stats.get('生产', 0)
        investment_time = category_stats.get('投资', 0) 
        expense_time = category_stats.get('支出', 0)
        
        # 生成周报内容
        week_num = week_start.isocalendar()[1]
        report_content = f"""📊 第{week_num}周时间记录报告 ({week_start} 至 {week_end})

1. 本周记录有效时间7天，总时长{week_total_minutes}分钟，实际记录时间 {total_duration} 分钟，有效率 {effective_rate:.1f}%
2. 未记录时间 {unrecorded_minutes} 分钟，折合 {unrecorded_minutes/60:.1f} 小时
3. 生产：投资：支出 = {production_time}:{investment_time}:{expense_time} ≈ {production_time/60:.1f}:{investment_time/60:.1f}:{expense_time/60:.1f}（采用24小时为基数）
   按照3个8小时，8小时睡觉，8小时工作和8小时其他，每天有 {unrecorded_minutes/60/7:.1f} 小时没有被妥善利用

📈 详细分析：
- 生产类活动：{production_time}分钟 ({production_time/60:.1f}小时)"""

        # 添加生产类详细统计
        production_details = []
        for activity, duration in activity_stats.items():
            if self.activity_mapping.get(activity) == '生产':
                production_details.append(f"{activity}：{duration}分钟")
        if production_details:
            report_content += "\n  " + ", ".join(production_details)
            
        report_content += f"""
- 投资类活动：{investment_time}分钟 ({investment_time/60:.1f}小时)"""

        # 添加投资类详细统计
        investment_details = []
        for activity, duration in activity_stats.items():
            if self.activity_mapping.get(activity) == '投资':
                investment_details.append(f"{activity}：{duration}分钟")
        if investment_details:
            report_content += "\n  " + ", ".join(investment_details)
            
        report_content += f"""
- 支出类活动：{expense_time}分钟 ({expense_time/60:.1f}小时)"""

        # 添加支出类详细统计
        expense_details = []
        for activity, duration in activity_stats.items():
            if self.activity_mapping.get(activity) == '支出':
                expense_details.append(f"{activity}：{duration}分钟")
        if expense_details:
            report_content += "\n  " + ", ".join(expense_details)
            
        # 添加改进建议
        suggestions = []
        if effective_rate < 60:
            suggestions.append("建议提高时间记录的完整性")
        if production_time < investment_time:
            suggestions.append("可以考虑增加生产性活动的时间")
        if expense_time > production_time + investment_time:
            suggestions.append("建议减少支出类活动，增加有价值的时间投入")
            
        if suggestions:
            report_content += f"""

🎯 改进建议：
- """ + "\n- ".join(suggestions)

        # 保存到Notion页面
        try:
            if not self.page_id:
                print("❌ 缺少PAGE_ID配置，无法保存到Notion")
                print("📄 周报内容:")
                print("-" * 60)
                print(report_content)
                return False
                
            # 在指定页面添加新的文本块
            self.notion.blocks.children.append(
                block_id=self.page_id,
                children=[
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": f"第{week_num}周时间记录报告"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block", 
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": report_content
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
            
            print("✅ 周报已保存到Notion页面")
            print("📄 周报内容:")
            print("-" * 60)
            print(report_content)
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存周报到Notion失败: {e}")
            print("📄 周报内容:")
            print("-" * 60)
            print(report_content)
            return False


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description='SimpleTimeTracker - 简化版智能时间记录工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python time_agent.py                          # 交互模式
  python time_agent.py --text "7点到9点阅读"    # 单条记录
  python time_agent.py --file input.txt         # 批量输入
  python time_agent.py --daily-report           # 生成日报
  python time_agent.py --weekly-report          # 生成周报
        """
    )
    
    parser.add_argument('--file', help='批量输入文件路径')
    parser.add_argument('--text', help='单条时间记录文本')
    parser.add_argument('--daily-report', action='store_true', help='生成日报')
    parser.add_argument('--weekly-report', action='store_true', help='生成周报')
    parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    try:
        # 初始化时间代理
        agent = SimpleTimeAgent()
        
        # 处理日期参数
        target_date = None
        if args.date:
            target_date = datetime.datetime.strptime(args.date, '%Y-%m-%d').date()
            
        # 根据参数执行相应功能
        if args.daily_report:
            agent.generate_daily_report(target_date)
        elif args.weekly_report:
            agent.generate_weekly_report(target_date)
        elif args.file:
            agent.process_batch_file(args.file)
        elif args.text:
            agent.process_single_input(args.text)
        else:
            # 默认交互模式
            agent.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        logger.error(f"❌ 程序错误: {e}")
        print(f"❌ 程序错误: {e}")



if __name__ == "__main__":
    main()
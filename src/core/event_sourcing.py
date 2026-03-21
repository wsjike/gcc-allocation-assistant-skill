"""
GCC Allocation Assistant - 事件溯源核心

第1轮优化：事件驱动架构
实现状态机管理、事件日志、审计追踪

Author: maxbay
Email: xcbai25@stu.pku.edu.cn
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
import json
import hashlib


class MilestoneEventType(Enum):
    """里程碑事件类型"""
    CREATED = "milestone_created"
    ACTIVATED = "milestone_activated"
    SUBMITTED = "milestone_submitted"
    UNDER_REVIEW = "milestone_under_review"
    APPROVED = "milestone_approved"
    REJECTED = "milestone_rejected"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_CONFIRMED = "payment_confirmed"
    CANCELLED = "milestone_cancelled"


@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: str
    event_type: str
    aggregate_id: str  # 里程碑ID或项目ID
    timestamp: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    def get_hash(self) -> str:
        """生成事件哈希（用于防篡改）"""
        content = f"{self.event_id}{self.event_type}{self.timestamp}{json.dumps(self.payload, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class EventStore:
    """事件存储 - 不可篡改的事件日志"""
    
    def __init__(self):
        self.events: List[DomainEvent] = []
        self.aggregate_events: Dict[str, List[DomainEvent]] = {}
    
    def append(self, event: DomainEvent):
        """追加事件"""
        self.events.append(event)
        
        # 按聚合ID索引
        if event.aggregate_id not in self.aggregate_events:
            self.aggregate_events[event.aggregate_id] = []
        self.aggregate_events[event.aggregate_id].append(event)
    
    def get_events(self, aggregate_id: str) -> List[DomainEvent]:
        """获取特定聚合的所有事件"""
        return self.aggregate_events.get(aggregate_id, [])
    
    def get_all_events(self) -> List[DomainEvent]:
        """获取所有事件（按时间排序）"""
        return sorted(self.events, key=lambda e: e.timestamp)
    
    def replay(self, aggregate_id: str) -> List[DomainEvent]:
        """回放事件（用于恢复状态）"""
        return self.get_events(aggregate_id)


class MilestoneState(Enum):
    """里程碑状态"""
    PENDING = auto()
    IN_PROGRESS = auto()
    SUBMITTED = auto()
    UNDER_REVIEW = auto()
    APPROVED = auto()
    PAID = auto()
    REJECTED = auto()
    CANCELLED = auto()


class MilestoneStateMachine:
    """
    里程碑状态机 - 第1轮核心优化
    
    状态转换规则：
    PENDING → IN_PROGRESS → SUBMITTED → UNDER_REVIEW → APPROVED → PAID
                              ↓              ↓
                           REJECTED      CANCELLED
    """
    
    # 定义合法状态转换
    TRANSITIONS = {
        MilestoneState.PENDING: [MilestoneState.IN_PROGRESS, MilestoneState.CANCELLED],
        MilestoneState.IN_PROGRESS: [MilestoneState.SUBMITTED, MilestoneState.CANCELLED],
        MilestoneState.SUBMITTED: [MilestoneState.UNDER_REVIEW],
        MilestoneState.UNDER_REVIEW: [MilestoneState.APPROVED, MilestoneState.REJECTED],
        MilestoneState.APPROVED: [MilestoneState.PAID],
        MilestoneState.REJECTED: [MilestoneState.IN_PROGRESS],  # 可重新提交
        MilestoneState.PAID: [],  # 终态
        MilestoneState.CANCELLED: []  # 终态
    }
    
    def __init__(self, milestone_id: str, event_store: EventStore):
        self.milestone_id = milestone_id
        self.event_store = event_store
        self.current_state = MilestoneState.PENDING
        self._load_state()
    
    def _load_state(self):
        """从事件日志恢复状态"""
        events = self.event_store.get_events(self.milestone_id)
        for event in events:
            self._apply_event(event)
    
    def _apply_event(self, event: DomainEvent):
        """应用事件更新状态"""
        state_map = {
            "milestone_created": MilestoneState.PENDING,
            "milestone_activated": MilestoneState.IN_PROGRESS,
            "milestone_submitted": MilestoneState.SUBMITTED,
            "milestone_under_review": MilestoneState.UNDER_REVIEW,
            "milestone_approved": MilestoneState.APPROVED,
            "milestone_rejected": MilestoneState.REJECTED,
            "payment_confirmed": MilestoneState.PAID,
            "milestone_cancelled": MilestoneState.CANCELLED
        }
        
        new_state = state_map.get(event.event_type)
        if new_state:
            self.current_state = new_state
    
    def can_transition_to(self, new_state: MilestoneState) -> bool:
        """检查是否可以转换到目标状态"""
        return new_state in self.TRANSITIONS.get(self.current_state, [])
    
    def transition(self, new_state: MilestoneState, 
                   triggered_by: str, reason: str = "") -> Optional[DomainEvent]:
        """
        执行状态转换
        
        Args:
            new_state: 目标状态
            triggered_by: 触发者
            reason: 转换原因
            
        Returns:
            生成的事件，如果转换不合法则返回None
        """
        if not self.can_transition_to(new_state):
            return None
        
        # 创建事件
        event_type_map = {
            MilestoneState.IN_PROGRESS: "milestone_activated",
            MilestoneState.SUBMITTED: "milestone_submitted",
            MilestoneState.UNDER_REVIEW: "milestone_under_review",
            MilestoneState.APPROVED: "milestone_approved",
            MilestoneState.REJECTED: "milestone_rejected",
            MilestoneState.PAID: "payment_confirmed",
            MilestoneState.CANCELLED: "milestone_cancelled"
        }
        
        event_type = event_type_map.get(new_state)
        if not event_type:
            return None
        
        event = DomainEvent(
            event_id=f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self.milestone_id}",
            event_type=event_type,
            aggregate_id=self.milestone_id,
            timestamp=datetime.now().isoformat(),
            payload={
                "from_state": self.current_state.name,
                "to_state": new_state.name,
                "reason": reason
            },
            metadata={
                "triggered_by": triggered_by,
                "previous_hash": self._get_last_event_hash()
            }
        )
        
        # 存储事件
        self.event_store.append(event)
        
        # 更新状态
        self.current_state = new_state
        
        return event
    
    def _get_last_event_hash(self) -> str:
        """获取最后一个事件的哈希"""
        events = self.event_store.get_events(self.milestone_id)
        if events:
            return events[-1].get_hash()
        return "0" * 16
    
    def get_state(self) -> MilestoneState:
        """获取当前状态"""
        return self.current_state
    
    def get_history(self) -> List[DomainEvent]:
        """获取状态变更历史"""
        return self.event_store.get_events(self.milestone_id)


class EventHandler(ABC):
    """事件处理器基类"""
    
    @abstractmethod
    def handle(self, event: DomainEvent):
        pass


class PaymentEventHandler(EventHandler):
    """支付事件处理器"""
    
    def __init__(self, payment_service):
        self.payment_service = payment_service
    
    def handle(self, event: DomainEvent):
        if event.event_type == "milestone_approved":
            # 触发支付
            milestone_id = event.aggregate_id
            amount = event.payload.get("amount", 0)
            recipient = event.payload.get("recipient", "")
            
            print(f"[支付事件] 里程碑 {milestone_id} 已批准，触发支付 {amount} 给 {recipient}")
            
            # 调用支付服务
            # self.payment_service.initiate_payment(milestone_id, amount, recipient)


class NotificationEventHandler(EventHandler):
    """通知事件处理器"""
    
    def __init__(self, notification_service):
        self.notification_service = notification_service
    
    def handle(self, event: DomainEvent):
        # 发送通知
        notifications = {
            "milestone_submitted": "里程碑已提交，等待审核",
            "milestone_approved": "里程碑已通过审核",
            "milestone_rejected": "里程碑未通过审核，请查看原因",
            "payment_confirmed": "资金已发放"
        }
        
        message = notifications.get(event.event_type)
        if message:
            recipient = event.payload.get("applicant", "")
            print(f"[通知] 发送给 {recipient}: {message}")


class EventBus:
    """事件总线 - 发布订阅模式"""
    
    def __init__(self):
        self.handlers: Dict[str, List[EventHandler]] = {}
        self.event_store: Optional[EventStore] = None
    
    def set_event_store(self, store: EventStore):
        """设置事件存储"""
        self.event_store = store
    
    def subscribe(self, event_type: str, handler: EventHandler):
        """订阅事件"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def publish(self, event: DomainEvent):
        """发布事件"""
        # 存储事件
        if self.event_store:
            self.event_store.append(event)
        
        # 分发到处理器
        handlers = self.handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler.handle(event)
            except Exception as e:
                print(f"[错误] 事件处理失败: {e}")


# 便捷函数
def create_milestone_workflow(milestone_id: str) -> tuple:
    """
    创建里程碑工作流
    
    Returns:
        (state_machine, event_bus)
    """
    event_store = EventStore()
    state_machine = MilestoneStateMachine(milestone_id, event_store)
    event_bus = EventBus()
    event_bus.set_event_store(event_store)
    
    # 注册处理器
    event_bus.subscribe("milestone_approved", PaymentEventHandler(None))
    event_bus.subscribe("milestone_submitted", NotificationEventHandler(None))
    event_bus.subscribe("milestone_approved", NotificationEventHandler(None))
    
    return state_machine, event_bus

"""
GCC Allocation Assistant - 数据模型

Author: maxbay
Email: xcbai25@stu.pku.edu.cn
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


class MilestoneStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class ProjectStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


@dataclass
class Milestone:
    """里程碑"""
    id: str = field(default_factory=lambda: f"ms_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    title: str = ""
    description: str = ""
    deliverables: List[str] = field(default_factory=list)
    due_date: Optional[str] = None
    amount: float = 0.0
    status: MilestoneStatus = MilestoneStatus.PENDING
    
    # 验证相关
    submitted_at: Optional[str] = None
    submitted_evidence: List[str] = field(default_factory=list)  # GitHub links, etc.
    review_result: Optional[str] = None
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    
    # 支付相关
    payment_tx_hash: Optional[str] = None
    paid_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "deliverables": self.deliverables,
            "due_date": self.due_date,
            "amount": self.amount,
            "status": self.status.value,
            "submitted_at": self.submitted_at,
            "review_result": self.review_result,
            "payment_tx_hash": self.payment_tx_hash
        }


@dataclass
class Project:
    """资助项目"""
    id: str = field(default_factory=lambda: f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    name: str = ""
    description: str = ""
    applicant: str = ""
    github_url: str = ""
    total_funding: float = 0.0
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # 里程碑
    milestones: List[Milestone] = field(default_factory=list)
    
    # GitHub 追踪
    target_commits: int = 0
    target_issues: int = 0
    target_prs: int = 0
    
    # 进度
    progress_percentage: float = 0.0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def calculate_progress(self) -> float:
        """计算项目进度"""
        if not self.milestones:
            return 0.0
        
        completed = sum(1 for m in self.milestones 
                       if m.status in [MilestoneStatus.APPROVED, MilestoneStatus.PAID])
        return (completed / len(self.milestones)) * 100
    
    def get_next_milestone(self) -> Optional[Milestone]:
        """获取下一个待完成的里程碑"""
        for ms in self.milestones:
            if ms.status in [MilestoneStatus.PENDING, MilestoneStatus.IN_PROGRESS]:
                return ms
        return None
    
    def get_pending_payment(self) -> float:
        """获取待支付金额"""
        return sum(ms.amount for ms in self.milestones 
                  if ms.status == MilestoneStatus.APPROVED)


@dataclass
class Payment:
    """支付记录"""
    id: str = field(default_factory=lambda: f"pay_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    milestone_id: str = ""
    project_id: str = ""
    amount: float = 0.0
    recipient: str = ""
    status: str = "pending"  # pending, approved, executed, confirmed
    
    # 多签信息
    required_signatures: int = 3
    current_signatures: int = 0
    signers: List[str] = field(default_factory=list)
    
    # 链上信息
    tx_hash: Optional[str] = None
    executed_at: Optional[str] = None
    confirmed_at: Optional[str] = None


@dataclass
class RiskAlert:
    """风险预警"""
    project_id: str = ""
    alert_type: str = ""  # delay, low_activity, milestone_overdue, etc.
    severity: str = "medium"  # low, medium, high, critical
    message: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved: bool = False
    resolved_at: Optional[str] = None

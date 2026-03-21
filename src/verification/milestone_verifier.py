"""
GCC Allocation Assistant - 里程碑验证引擎

第3轮优化：智能验证引擎
实现多维度自动验证、规则引擎、GitHub深度集成

Author: maxbay
Email: xcbai25@stu.pku.edu.cn
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re


class VerificationStatus(Enum):
    """验证状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"


@dataclass
class VerificationResult:
    """验证结果"""
    status: VerificationStatus
    score: float  # 0-100
    checks: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    verified_at: str = field(default_factory=lambda: datetime.now().isoformat())


class VerificationRule(ABC):
    """验证规则基类"""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
    
    @abstractmethod
    def check(self, milestone: Dict, evidence: Dict) -> Dict[str, Any]:
        """
        执行验证检查
        
        Returns:
            {
                "passed": bool,
                "score": float,
                "details": str,
                "metadata": dict
            }
        """
        pass


class GitHubActivityRule(VerificationRule):
    """GitHub 活动验证规则"""
    
    def __init__(self):
        super().__init__("GitHub Activity", weight=0.3)
    
    def check(self, milestone: Dict, evidence: Dict) -> Dict[str, Any]:
        """检查GitHub活动"""
        github_data = evidence.get("github", {})
        
        # 获取指标
        commits = github_data.get("commits", 0)
        prs = github_data.get("pull_requests", 0)
        issues_closed = github_data.get("issues_closed", 0)
        
        # 计算得分
        score = 0
        details = []
        
        # 提交检查
        target_commits = milestone.get("target_commits", 10)
        if commits >= target_commits:
            score += 40
            details.append(f"✓ 代码提交达标: {commits}/{target_commits}")
        else:
            score += (commits / target_commits) * 40
            details.append(f"⚠ 代码提交不足: {commits}/{target_commits}")
        
        # PR检查
        target_prs = milestone.get("target_prs", 2)
        if prs >= target_prs:
            score += 30
            details.append(f"✓ PR数量达标: {prs}/{target_prs}")
        else:
            score += (prs / target_prs) * 30
            details.append(f"⚠ PR数量不足: {prs}/{target_prs}")
        
        # Issue检查
        target_issues = milestone.get("target_issues", 5)
        if issues_closed >= target_issues:
            score += 30
            details.append(f"✓ Issue解决达标: {issues_closed}/{target_issues}")
        else:
            score += (issues_closed / target_issues) * 30
            details.append(f"⚠ Issue解决不足: {issues_closed}/{target_issues}")
        
        return {
            "passed": score >= 70,
            "score": score,
            "details": "; ".join(details),
            "metadata": {
                "commits": commits,
                "prs": prs,
                "issues_closed": issues_closed
            }
        }


class DeliverableCompletenessRule(VerificationRule):
    """交付物完整性验证规则"""
    
    def __init__(self):
        super().__init__("Deliverable Completeness", weight=0.25)
    
    def check(self, milestone: Dict, evidence: Dict) -> Dict[str, Any]:
        """检查交付物完整性"""
        required_deliverables = milestone.get("deliverables", [])
        submitted_links = evidence.get("links", [])
        
        if not required_deliverables:
            return {
                "passed": True,
                "score": 100,
                "details": "无明确交付物要求",
                "metadata": {}
            }
        
        # 检查每个交付物
        found_count = 0
        details = []
        
        for deliverable in required_deliverables:
            # 简单检查：是否有相关链接
            found = any(deliverable.lower() in link.lower() for link in submitted_links)
            if found:
                found_count += 1
                details.append(f"✓ {deliverable}")
            else:
                details.append(f"✗ {deliverable} (未找到)")
        
        score = (found_count / len(required_deliverables)) * 100
        
        return {
            "passed": score >= 80,
            "score": score,
            "details": "; ".join(details),
            "metadata": {
                "required": len(required_deliverables),
                "found": found_count
            }
        }


class CodeQualityRule(VerificationRule):
    """代码质量验证规则"""
    
    def __init__(self):
        super().__init__("Code Quality", weight=0.2)
    
    def check(self, milestone: Dict, evidence: Dict) -> Dict[str, Any]:
        """检查代码质量"""
        quality_data = evidence.get("code_quality", {})
        
        # 获取质量指标
        test_coverage = quality_data.get("test_coverage", 0)
        lint_score = quality_data.get("lint_score", 100)
        complexity = quality_data.get("complexity", 10)
        
        score = 0
        details = []
        
        # 测试覆盖率
        if test_coverage >= 80:
            score += 40
            details.append(f"✓ 测试覆盖率优秀: {test_coverage}%")
        elif test_coverage >= 50:
            score += (test_coverage / 80) * 40
            details.append(f"⚠ 测试覆盖率一般: {test_coverage}%")
        else:
            details.append(f"✗ 测试覆盖率不足: {test_coverage}%")
        
        # 代码规范
        if lint_score >= 90:
            score += 30
            details.append(f"✓ 代码规范良好: {lint_score}")
        else:
            score += (lint_score / 90) * 30
            details.append(f"⚠ 代码规范需改进: {lint_score}")
        
        # 复杂度
        if complexity <= 10:
            score += 30
            details.append(f"✓ 代码复杂度合理: {complexity}")
        else:
            score += max(0, 30 - (complexity - 10) * 2)
            details.append(f"⚠ 代码复杂度偏高: {complexity}")
        
        return {
            "passed": score >= 70,
            "score": score,
            "details": "; ".join(details),
            "metadata": {
                "test_coverage": test_coverage,
                "lint_score": lint_score,
                "complexity": complexity
            }
        }


class DocumentationRule(VerificationRule):
    """文档完整性验证规则"""
    
    def __init__(self):
        super().__init__("Documentation", weight=0.15)
    
    def check(self, milestone: Dict, evidence: Dict) -> Dict[str, Any]:
        """检查文档"""
        docs = evidence.get("documentation", {})
        
        checks = {
            "README": docs.get("has_readme", False),
            "API文档": docs.get("has_api_doc", False),
            "部署文档": docs.get("has_deployment_doc", False),
            "更新日志": docs.get("has_changelog", False)
        }
        
        passed_count = sum(1 for v in checks.values() if v)
        score = (passed_count / len(checks)) * 100
        
        details = [f"{'✓' if v else '✗'} {k}" for k, v in checks.items()]
        
        return {
            "passed": score >= 75,
            "score": score,
            "details": "; ".join(details),
            "metadata": checks
        }


class TimelineComplianceRule(VerificationRule):
    """时间合规性验证规则"""
    
    def __init__(self):
        super().__init__("Timeline Compliance", weight=0.1)
    
    def check(self, milestone: Dict, evidence: Dict) -> Dict[str, Any]:
        """检查时间合规性"""
        due_date = milestone.get("due_date")
        submitted_at = evidence.get("submitted_at")
        
        if not due_date or not submitted_at:
            return {
                "passed": True,
                "score": 100,
                "details": "无明确时间要求",
                "metadata": {}
            }
        
        from datetime import datetime
        
        due = datetime.fromisoformat(due_date)
        submitted = datetime.fromisoformat(submitted_at)
        
        # 计算延期天数
        delay_days = (submitted - due).days
        
        if delay_days <= 0:
            score = 100
            details = f"✓ 按时提交，提前 {-delay_days} 天"
        elif delay_days <= 7:
            score = 80
            details = f"⚠ 轻微延期 {delay_days} 天"
        elif delay_days <= 30:
            score = 50
            details = f"⚠ 延期 {delay_days} 天"
        else:
            score = 20
            details = f"✗ 严重延期 {delay_days} 天"
        
        return {
            "passed": score >= 50,
            "score": score,
            "details": details,
            "metadata": {
                "due_date": due_date,
                "submitted_at": submitted_at,
                "delay_days": max(0, delay_days)
            }
        }


class MilestoneVerifier:
    """
    里程碑验证引擎 - 第3轮核心优化
    
    功能：
    1. 多维度自动验证
    2. 可配置验证规则
    3. 智能评分系统
    4. 自动/人工审核决策
    """
    
    # 自动通过阈值
    AUTO_APPROVE_THRESHOLD = 80
    # 必须人工审核阈值
    MANUAL_REVIEW_THRESHOLD = 60
    
    def __init__(self):
        self.rules: List[VerificationRule] = [
            GitHubActivityRule(),
            DeliverableCompletenessRule(),
            CodeQualityRule(),
            DocumentationRule(),
            TimelineComplianceRule()
        ]
    
    def verify(self, milestone: Dict, evidence: Dict) -> VerificationResult:
        """
        执行完整验证
        
        Args:
            milestone: 里程碑定义
            evidence: 提交的证据
            
        Returns:
            验证结果
        """
        checks = []
        total_score = 0
        total_weight = 0
        
        # 执行所有规则
        for rule in self.rules:
            try:
                result = rule.check(milestone, evidence)
                
                weighted_score = result["score"] * rule.weight
                total_score += weighted_score
                total_weight += rule.weight
                
                checks.append({
                    "rule": rule.name,
                    "weight": rule.weight,
                    "passed": result["passed"],
                    "score": result["score"],
                    "details": result["details"],
                    "metadata": result.get("metadata", {})
                })
            except Exception as e:
                checks.append({
                    "rule": rule.name,
                    "weight": rule.weight,
                    "passed": False,
                    "score": 0,
                    "details": f"验证失败: {str(e)}",
                    "metadata": {}
                })
        
        # 计算最终得分
        final_score = (total_score / total_weight) if total_weight > 0 else 0
        
        # 确定状态
        if final_score >= self.AUTO_APPROVE_THRESHOLD:
            status = VerificationStatus.PASSED
            summary = f"验证通过（自动批准）得分: {final_score:.1f}"
        elif final_score >= self.MANUAL_REVIEW_THRESHOLD:
            status = VerificationStatus.MANUAL_REVIEW
            summary = f"需要人工审核，得分: {final_score:.1f}"
        else:
            status = VerificationStatus.FAILED
            summary = f"验证未通过，得分: {final_score:.1f}"
        
        # 生成建议
        recommendations = self._generate_recommendations(checks)
        
        return VerificationResult(
            status=status,
            score=final_score,
            checks=checks,
            summary=summary,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, checks: List[Dict]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        for check in checks:
            if not check["passed"]:
                rule_name = check["rule"]
                if rule_name == "GitHub Activity":
                    recommendations.append("增加代码提交频率，完成更多PR和Issue")
                elif rule_name == "Deliverable Completeness":
                    recommendations.append("补充缺失的交付物")
                elif rule_name == "Code Quality":
                    recommendations.append("提高测试覆盖率，优化代码规范")
                elif rule_name == "Documentation":
                    recommendations.append("完善项目文档")
                elif rule_name == "Timeline Compliance":
                    recommendations.append("注意里程碑时间节点")
        
        return recommendations
    
    def add_rule(self, rule: VerificationRule):
        """添加自定义规则"""
        self.rules.append(rule)
    
    def get_rule_weights(self) -> Dict[str, float]:
        """获取规则权重配置"""
        return {rule.name: rule.weight for rule in self.rules}


# 便捷函数
def verify_milestone(milestone: Dict, evidence: Dict) -> VerificationResult:
    """快速验证里程碑"""
    verifier = MilestoneVerifier()
    return verifier.verify(milestone, evidence)

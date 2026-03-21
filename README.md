# 💰 GCC Allocation Assistant

> 智能资金分配助手 - GCC AI Agent Hackathon 分配赛道
> 
> **里程碑验证 · 自动支付 · 进度追踪**

---

## 🎯 解决的问题

- 里程碑审核慢？→ **自动验证，即时审批**
- 支付流程长？→ **自动触发，链上执行**
- 进度不透明？→ **实时监控，自动报告**
- 风险发现晚？→ **智能预警，提前干预**

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| ✅ **自动验证** | GitHub 数据检查 + 完成度评估 |
| 💸 **自动支付** | 里程碑通过即触发多签支付 |
| 📈 **进度追踪** | 实时计算项目完成百分比 |
| ⚠️ **风险预警** | 逾期/滞后/停滞自动检测 |
| 📊 **审计报告** | 资金流转全程记录 |

---

## 🚀 快速开始

```python
from src.allocator import AllocationEngine

engine = AllocationEngine()

# 创建项目
project = engine.create_project(
    name="隐私协议开发",
    applicant="0x1234...",
    total_funding=100000,
    milestones=[
        {"title": "MVP", "amount": 30000, "due_date": "2024-04-01"},
        {"title": "测试网", "amount": 40000, "due_date": "2024-06-01"},
        {"title": "主网", "amount": 30000, "due_date": "2024-08-01"}
    ]
)

# 提交里程碑
result = engine.submit_milestone(
    project_id=project.id,
    milestone_id=project.milestones[0].id,
    evidence=["https://github.com/..."]
)

print(result)
```

---

## 📊 20轮迭代成果

| 轮次 | 功能 | 状态 |
|------|------|------|
| 1-4 | 基础架构与里程碑管理 | ✅ |
| 5-6 | GitHub 集成 | ✅ |
| 7-8 | 自动验证 | ✅ |
| 9-12 | 支付系统与链上集成 | ✅ |
| 13-14 | 风险监控 | ✅ |
| 15-18 | 报告与通知 | ✅ |
| 19-20 | 集成优化 | ✅ |

---

**Author:** maxbay  
**Email:** xcbai25@stu.pku.edu.cn  
**赛道:** 分配 (Allocation)

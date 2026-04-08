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

## ❓ FAQ：升级 Copilot Pro 后 VS Code 仍无法使用

> **Q：我已经升级了 GitHub Copilot Pro，为什么 VS Code 模型列表里还有些模型显示"升级"？**

**常见原因速查：**

1. **账号不一致** — VS Code 登录的 GitHub 账号与购买 Pro 的账号不同  
2. **订阅未同步** — 新订阅需 5–10 分钟生效，重启 VS Code 或重新登录即可  
3. **组织策略限制** — 所在组织/企业管理员可能禁用了 Copilot 或限制了可用模型  
4. **扩展版本过旧** — 更新或重装 `GitHub Copilot` / `GitHub Copilot Chat` 扩展  
5. **网络/代理问题** — 企业防火墙或代理拦截了 Copilot API 请求  
6. **模型需要更高订阅** — 部分高级模型（如 Claude 3.7）仅限 Pro+ 或企业版；**建议使用 Auto 模式**自动选择最佳可用模型  

📖 **完整排障步骤（含日志收集方法）请参阅：[docs/troubleshooting.md](docs/troubleshooting.md)**

---

**Author:** maxbay  
**Email:** xcbai25@stu.pku.edu.cn  
**赛道:** 分配 (Allocation)

#!/usr/bin/env python3
"""GCC Allocation Assistant - 带链接跳转"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
from threading import Timer

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCC Allocation Assistant</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f8fafc;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: 24px;
            padding: 20px;
            background: rgba(30, 41, 59, 0.8);
            border-radius: 16px;
            border: 1px solid #334155;
        }

        .header h1 {
            font-size: 1.8rem;
            margin-bottom: 8px;
            background: linear-gradient(90deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header p {
            color: #94a3b8;
        }

        /* Stats Row - 可点击 */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: rgba(30, 41, 59, 0.9);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid #334155;
            text-align: center;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            border-color: #60a5fa;
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
        }

        .stat-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 12px;
            font-size: 1.25rem;
        }

        .stat-card:nth-child(1) .stat-icon { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
        .stat-card:nth-child(2) .stat-icon { background: rgba(16, 185, 129, 0.15); color: #34d399; }
        .stat-card:nth-child(3) .stat-icon { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
        .stat-card:nth-child(4) .stat-icon { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }

        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .stat-card:nth-child(1) .stat-value { color: #60a5fa; }
        .stat-card:nth-child(2) .stat-value { color: #34d399; }
        .stat-card:nth-child(3) .stat-value { color: #a78bfa; }
        .stat-card:nth-child(4) .stat-value { color: #fbbf24; }

        .stat-label {
            color: #94a3b8;
            font-size: 0.875rem;
        }

        /* Main Grid */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        /* Card Styles */
        .card {
            background: rgba(30, 41, 59, 0.9);
            border-radius: 16px;
            border: 1px solid #334155;
            display: flex;
            flex-direction: column;
        }

        .card-header {
            padding: 16px 20px;
            border-bottom: 1px solid #334155;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card-title i {
            color: #60a5fa;
        }

        .view-all {
            color: #60a5fa;
            font-size: 0.85rem;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s;
        }

        .view-all:hover {
            color: #93c5fd;
            gap: 8px;
        }

        .card-body {
            padding: 20px;
            flex: 1;
        }

        /* Fund Overview */
        .fund-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 16px;
        }

        .fund-stat {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 14px;
            text-align: center;
            text-decoration: none;
            color: inherit;
            transition: all 0.2s;
        }

        .fund-stat:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .fund-stat-value {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 2px;
        }

        .fund-stat-label {
            font-size: 0.75rem;
            color: #94a3b8;
        }

        .chart-wrapper {
            height: 160px;
        }

        /* Project List - 可点击 */
        .project-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .project-item {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 14px;
            border: 1px solid #334155;
            text-decoration: none;
            color: inherit;
            display: block;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .project-item:hover {
            border-color: #60a5fa;
            background: rgba(59, 130, 246, 0.05);
            transform: translateX(4px);
        }

        .project-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .project-name {
            font-weight: 600;
            font-size: 0.95rem;
            color: #f8fafc;
        }

        .project-badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
        }

        .badge-active { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .badge-risk { background: rgba(239, 68, 68, 0.2); color: #f87171; }

        .project-meta {
            display: flex;
            gap: 16px;
            margin-bottom: 10px;
            font-size: 0.8rem;
            color: #94a3b8;
        }

        .project-meta span {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .progress-bar {
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            border-radius: 3px;
        }

        .fill-green { background: #10b981; }
        .fill-purple { background: #8b5cf6; }
        .fill-red { background: #ef4444; }

        /* Milestone List - 可点击 */
        .milestone-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .milestone-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .milestone-item:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateX(4px);
        }

        .milestone-icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
        }

        .icon-done { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .icon-progress { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
        .icon-pending { background: rgba(148, 163, 184, 0.2); color: #94a3b8; }

        .milestone-info {
            flex: 1;
        }

        .milestone-title {
            font-weight: 500;
            font-size: 0.9rem;
            margin-bottom: 2px;
            color: #f8fafc;
        }

        .milestone-meta {
            font-size: 0.75rem;
            color: #94a3b8;
        }

        .milestone-percent {
            font-weight: 600;
        }

        /* Risk Section */
        .risk-section {
            background: rgba(30, 41, 59, 0.9);
            border-radius: 16px;
            border: 1px solid #334155;
            overflow: hidden;
        }

        .risk-header {
            padding: 16px 20px;
            background: rgba(239, 68, 68, 0.1);
            border-bottom: 1px solid #334155;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .risk-title-header {
            font-size: 1.1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #f87171;
        }

        .risk-count {
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .risk-body {
            padding: 20px;
        }

        .risk-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }

        /* Risk Cards - 可点击 */
        .risk-card {
            padding: 16px;
            border-radius: 12px;
            border-left: 4px solid;
            text-decoration: none;
            color: inherit;
            display: block;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .risk-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }

        .risk-card.high {
            background: rgba(239, 68, 68, 0.1);
            border-left-color: #ef4444;
        }

        .risk-card.high:hover {
            background: rgba(239, 68, 68, 0.15);
            box-shadow: 0 8px 25px rgba(239, 68, 68, 0.2);
        }

        .risk-card.medium {
            background: rgba(245, 158, 11, 0.1);
            border-left-color: #f59e0b;
        }

        .risk-card.medium:hover {
            background: rgba(245, 158, 11, 0.15);
            box-shadow: 0 8px 25px rgba(245, 158, 11, 0.2);
        }

        .risk-card.low {
            background: rgba(59, 130, 246, 0.1);
            border-left-color: #3b82f6;
        }

        .risk-card.low:hover {
            background: rgba(59, 130, 246, 0.15);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
        }

        .risk-card-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }

        .risk-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }

        .risk-card.high .risk-dot { background: #ef4444; }
        .risk-card.medium .risk-dot { background: #f59e0b; }
        .risk-card.low .risk-dot { background: #3b82f6; }

        .risk-card-title {
            font-weight: 600;
            font-size: 0.95rem;
            color: #f8fafc;
        }

        .risk-level-badge {
            margin-left: auto;
            font-size: 0.7rem;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
        }

        .risk-card.high .risk-level-badge { background: rgba(239, 68, 68, 0.2); color: #f87171; }
        .risk-card.medium .risk-level-badge { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
        .risk-card.low .risk-level-badge { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }

        .risk-desc {
            font-size: 0.85rem;
            color: #94a3b8;
            line-height: 1.4;
        }

        .risk-project {
            margin-top: 8px;
            font-size: 0.8rem;
            color: #64748b;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 20px;
            padding: 16px;
            color: #64748b;
            font-size: 0.875rem;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
        }

        ::-webkit-scrollbar-thumb {
            background: #475569;
            border-radius: 3px;
        }

        @media (max-width: 1200px) {
            .stats-row { grid-template-columns: repeat(2, 1fr); }
            .main-grid { grid-template-columns: 1fr; }
            .risk-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1><i class="fas fa-wallet"></i> GCC Allocation Assistant</h1>
            <p>智能资金分配平台 | 实时监控与风险预警</p>
        </div>

        <!-- Stats Row - 可点击 -->
        <div class="stats-row">
            <a href="/fund/overview" class="stat-card">
                <div class="stat-icon"><i class="fas fa-wallet"></i></div>
                <div class="stat-value">$380K</div>
                <div class="stat-label">总资金池</div>
            </a>
            <a href="/fund/allocated" class="stat-card">
                <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
                <div class="stat-value">$50K</div>
                <div class="stat-label">已分配</div>
            </a>
            <a href="/projects/active" class="stat-card">
                <div class="stat-icon"><i class="fas fa-project-diagram"></i></div>
                <div class="stat-value">12</div>
                <div class="stat-label">活跃项目</div>
            </a>
            <a href="/projects/pending" class="stat-card">
                <div class="stat-icon"><i class="fas fa-clock"></i></div>
                <div class="stat-value">8</div>
                <div class="stat-label">待审核</div>
            </a>
        </div>

        <!-- Main Grid -->
        <div class="main-grid">
            <!-- Left: 资金总览 -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-chart-pie"></i>
                        资金总览
                    </div>
                    <a href="/fund/details" class="view-all">
                        查看详情 <i class="fas fa-arrow-right"></i>
                    </a>
                </div>
                <div class="card-body">
                    <div class="fund-stats">
                        <a href="/fund/allocated" class="fund-stat">
                            <div class="fund-stat-value" style="color: #34d399;">$50K</div>
                            <div class="fund-stat-label">已分配</div>
                        </a>
                        <a href="/fund/available" class="fund-stat">
                            <div class="fund-stat-value" style="color: #a78bfa;">$280K</div>
                            <div class="fund-stat-label">待分配</div>
                        </a>
                        <a href="/fund/reserved" class="fund-stat">
                            <div class="fund-stat-value" style="color: #fbbf24;">$50K</div>
                            <div class="fund-stat-label">预留</div>
                        </a>
                        <a href="/fund/total" class="fund-stat">
                            <div class="fund-stat-value" style="color: #60a5fa;">$380K</div>
                            <div class="fund-stat-label">总计</div>
                        </a>
                    </div>
                    <div class="chart-wrapper">
                        <canvas id="fundChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Middle: 活跃项目 -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-folder-open"></i>
                        活跃项目
                    </div>
                    <a href="/projects" class="view-all">
                        查看全部 <i class="fas fa-arrow-right"></i>
                    </a>
                </div>
                <div class="card-body">
                    <div class="project-list">
                        <a href="/project/privacy-protocol" class="project-item">
                            <div class="project-header">
                                <span class="project-name">GCC 隐私协议开发</span>
                                <span class="project-badge badge-active">进行中</span>
                            </div>
                            <div class="project-meta">
                                <span><i class="fas fa-dollar-sign"></i> $100,000</span>
                                <span><i class="fas fa-flag"></i> 3 里程碑</span>
                                <span><i class="fas fa-percentage"></i> 33%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill fill-green" style="width: 33%"></div>
                            </div>
                        </a>

                        <a href="/project/bridge" class="project-item">
                            <div class="project-header">
                                <span class="project-name">GCC 跨链桥开发</span>
                                <span class="project-badge badge-active">进行中</span>
                            </div>
                            <div class="project-meta">
                                <span><i class="fas fa-dollar-sign"></i> $150,000</span>
                                <span><i class="fas fa-flag"></i> 4 里程碑</span>
                                <span><i class="fas fa-percentage"></i> 46%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill fill-purple" style="width: 46%"></div>
                            </div>
                        </a>

                        <a href="/project/defi-aggregator" class="project-item">
                            <div class="project-header">
                                <span class="project-name">GCC DeFi 聚合器</span>
                                <span class="project-badge badge-risk">有风险</span>
                            </div>
                            <div class="project-meta">
                                <span><i class="fas fa-dollar-sign"></i> $80,000</span>
                                <span><i class="fas fa-flag"></i> 3 里程碑</span>
                                <span><i class="fas fa-percentage"></i> 0%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill fill-red" style="width: 0%"></div>
                            </div>
                        </a>
                    </div>
                </div>
            </div>

            <!-- Right: 里程碑进度 -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        <i class="fas fa-flag-checkered"></i>
                        里程碑进度
                    </div>
                    <a href="/milestones" class="view-all">
                        查看全部 <i class="fas fa-arrow-right"></i>
                    </a>
                </div>
                <div class="card-body">
                    <div class="milestone-list">
                        <a href="/milestone/mvp-complete" class="milestone-item">
                            <div class="milestone-icon icon-done"><i class="fas fa-check"></i></div>
                            <div class="milestone-info">
                                <div class="milestone-title">MVP 开发完成</div>
                                <div class="milestone-meta">$30,000 · 隐私协议</div>
                            </div>
                            <div class="milestone-percent" style="color: #34d399;">100%</div>
                        </a>
                        <a href="/milestone/core-dev" class="milestone-item">
                            <div class="milestone-icon icon-progress"><i class="fas fa-spinner fa-spin"></i></div>
                            <div class="milestone-info">
                                <div class="milestone-title">核心开发</div>
                                <div class="milestone-meta">$60,000 · 跨链桥</div>
                            </div>
                            <div class="milestone-percent" style="color: #60a5fa;">65%</div>
                        </a>
                        <a href="/milestone/audit" class="milestone-item">
                            <div class="milestone-icon icon-pending"><i class="fas fa-clock"></i></div>
                            <div class="milestone-info">
                                <div class="milestone-title">安全审计</div>
                                <div class="milestone-meta">$40,000 · 待启动</div>
                            </div>
                            <div class="milestone-percent" style="color: #94a3b8;">0%</div>
                        </a>
                        <a href="/milestone/mainnet" class="milestone-item">
                            <div class="milestone-icon icon-pending"><i class="fas fa-hourglass-start"></i></div>
                            <div class="milestone-info">
                                <div class="milestone-title">主网上线</div>
                                <div class="milestone-meta">$20,000 · 待启动</div>
                            </div>
                            <div class="milestone-percent" style="color: #94a3b8;">0%</div>
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <!-- Risk Section - Full Width -->
        <div class="risk-section">
            <div class="risk-header">
                <div class="risk-title-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    风险预警
                </div>
                <span class="risk-count">4 个警告</span>
            </div>
            <div class="risk-body">
                <div class="risk-grid">
                    <a href="/risk/overdue-defi" class="risk-card high">
                        <div class="risk-card-header">
                            <div class="risk-dot"></div>
                            <span class="risk-card-title">逾期风险</span>
                            <span class="risk-level-badge">HIGH</span>
                        </div>
                        <div class="risk-desc">DeFi聚合器里程碑1已逾期30天，无提交记录</div>
                        <div class="risk-project">涉及项目: GCC DeFi 聚合器</div>
                    </a>

                    <a href="/risk/progress-bridge" class="risk-card medium">
                        <div class="risk-card-header">
                            <div class="risk-dot"></div>
                            <span class="risk-card-title">进度滞后</span>
                            <span class="risk-level-badge">MEDIUM</span>
                        </div>
                        <div class="risk-desc">GitHub提交频率下降50%，需关注开发进度</div>
                        <div class="risk-project">涉及项目: GCC 跨链桥开发</div>
                    </a>

                    <a href="/risk/fund-usage" class="risk-card low">
                        <div class="risk-card-header">
                            <div class="risk-dot"></div>
                            <span class="risk-card-title">资金使用率</span>
                            <span class="risk-level-badge">LOW</span>
                        </div>
                        <div class="risk-desc">第一阶段资金使用率达90%，建议关注预算</div>
                        <div class="risk-project">涉及项目: GCC 隐私协议开发</div>
                    </a>

                    <a href="/risk/delay-bridge" class="risk-card medium">
                        <div class="risk-card-header">
                            <div class="risk-dot"></div>
                            <span class="risk-card-title">里程碑延迟</span>
                            <span class="risk-level-badge">MEDIUM</span>
                        </div>
                        <div class="risk-desc">跨链桥项目核心开发预计延迟1周</div>
                        <div class="risk-project">涉及项目: GCC 跨链桥开发</div>
                    </a>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            GCC AI Agent Hackathon 2024 · 分配赛道 · OpenClaw Skill · 20轮迭代优化
        </div>
    </div>

    <script>
        const ctx = document.getElementById('fundChart').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['已分配', '待分配', '预留'],
                datasets: [{
                    data: [50000, 280000, 50000],
                    backgroundColor: ['#10b981', '#8b5cf6', '#f59e0b'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            padding: 15,
                            usePointStyle: true,
                            font: { size: 11 }
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>'''

class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        else:
            # 处理链接跳转 - 返回提示信息
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # 根据路径显示不同的提示
            path_display = self.path
            title = "页面导航"
            
            if 'fund' in self.path:
                title = "资金管理"
                content = "资金详情页面"
            elif 'project' in self.path or 'projects' in self.path:
                title = "项目管理"
                content = "项目详情页面"
            elif 'milestone' in self.path or 'milestones' in self.path:
                title = "里程碑管理"
                content = "里程碑详情页面"
            elif 'risk' in self.path:
                title = "风险预警"
                content = "风险详情页面"
            else:
                content = "功能页面"
            
            response_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - GCC Allocation</title>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }}
        .container {{
            text-align: center;
            padding: 40px;
            background: rgba(30, 41, 59, 0.9);
            border-radius: 20px;
            border: 1px solid #334155;
            max-width: 500px;
        }}
        .icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        h1 {{
            font-size: 1.8rem;
            margin-bottom: 12px;
            background: linear-gradient(90deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        p {{
            color: #94a3b8;
            margin-bottom: 24px;
            font-size: 1rem;
        }}
        .path {{
            background: rgba(59, 130, 246, 0.1);
            padding: 12px 20px;
            border-radius: 8px;
            font-family: monospace;
            color: #60a5fa;
            margin-bottom: 24px;
            word-break: break-all;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            background: #3b82f6;
            color: white;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .btn:hover {{
            background: #2563eb;
            transform: translateY(-2px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🚀</div>
        <h1>{title}</h1>
        <p>{content} - 功能开发中</p>
        <div class="path">{path_display}</div>
        <a href="/" class="btn">← 返回仪表盘</a>
    </div>
</body>
</html>'''
            self.wfile.write(response_html.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

def open_browser(port):
    webbrowser.open(f'http://localhost:{port}')

def main():
    port = 8081
    server = HTTPServer(('localhost', port), DemoHandler)
    
    print(f"🚀 启动分配可视化服务器...")
    print(f"🌐 访问地址: http://localhost:{port}")
    print("\n正在自动打开浏览器...")
    print("按 Ctrl+C 停止服务器\n")
    
    Timer(1.5, open_browser, args=[port]).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ 服务器已停止")
        server.shutdown()

if __name__ == '__main__':
    main()

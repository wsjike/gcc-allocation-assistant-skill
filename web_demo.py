#!/usr/bin/env python3
"""GCC Allocation Assistant - Web可视化演示"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
from threading import Timer

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCC Allocation Assistant - 资金分配可视化</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card-title {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-box {
            text-align: center;
            padding: 20px;
            border-radius: 12px;
            background: #f8f9fa;
        }
        .stat-value { font-size: 2em; font-weight: bold; color: #11998e; }
        .stat-label { color: #666; font-size: 0.9em; margin-top: 5px; }
        .project-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
        }
        .project-title { font-size: 1.1em; font-weight: bold; margin-bottom: 10px; }
        .project-meta { display: flex; gap: 20px; color: #666; font-size: 0.9em; }
        .milestone-item {
            display: flex;
            align-items: center;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .milestone-status {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2em;
            margin-right: 15px;
        }
        .status-paid { background: #d4edda; }
        .status-progress { background: #fff3cd; }
        .status-pending { background: #e2e3e5; }
        .milestone-info { flex: 1; }
        .milestone-title { font-weight: bold; margin-bottom: 5px; }
        .milestone-amount { color: #666; font-size: 0.9em; }
        .progress-bar {
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #11998e, #38ef7d);
            border-radius: 4px;
        }
        .risk-item {
            display: flex;
            align-items: center;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .risk-high { background: #f8d7da; border-left: 4px solid #dc3545; }
        .risk-medium { background: #fff3cd; border-left: 4px solid #ffc107; }
        .risk-low { background: #d1ecf1; border-left: 4px solid #17a2b8; }
        .risk-icon { font-size: 1.5em; margin-right: 15px; }
        .risk-content { flex: 1; }
        .risk-title { font-weight: bold; margin-bottom: 5px; }
        .risk-desc { color: #666; font-size: 0.9em; }
        .chart-container { position: relative; height: 250px; }
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 GCC Allocation Assistant</h1>
            <p>分配赛道可视化仪表盘 | 20轮迭代 | 智能资金分配</p>
        </div>
        
        <div class="dashboard">
            <!-- 资金统计 -->
            <div class="card">
                <div class="card-title">
                    <span>📊</span>
                    资金总览
                </div>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">$380K</div>
                        <div class="stat-label">总资金池</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">$50K</div>
                        <div class="stat-label">已分配</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">12</div>
                        <div class="stat-label">活跃项目</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">8</div>
                        <div class="stat-label">待审核</div>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="fundChart"></canvas>
                </div>
            </div>
            
            <!-- 项目列表 -->
            <div class="card">
                <div class="card-title">
                    <span>📋</span>
                    活跃项目
                </div>
                <div class="project-card">
                    <div class="project-title">GCC 隐私协议开发</div>
                    <div class="project-meta">
                        <span>💰 $100,000</span>
                        <span>📅 3个里程碑</span>
                        <span style="color: #28a745;">进行中</span>
                    </div>
                </div>
                <div class="project-card">
                    <div class="project-title">GCC 跨链桥开发</div>
                    <div class="project-meta">
                        <span>💰 $150,000</span>
                        <span>📅 4个里程碑</span>
                        <span style="color: #28a745;">进行中</span>
                    </div>
                </div>
                <div class="project-card">
                    <div class="project-title">GCC DeFi 聚合器</div>
                    <div class="project-meta">
                        <span>💰 $80,000</span>
                        <span>📅 3个里程碑</span>
                        <span style="color: #dc3545;">有风险</span>
                    </div>
                </div>
            </div>
            
            <!-- 里程碑进度 -->
            <div class="card">
                <div class="card-title">
                    <span>🎯</span>
                    里程碑进度
                </div>
                <div class="milestone-item">
                    <div class="milestone-status status-paid">✅</div>
                    <div class="milestone-info">
                        <div class="milestone-title">MVP 开发完成</div>
                        <div class="milestone-amount">$30,000 | 隐私协议开发</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 100%"></div>
                        </div>
                    </div>
                </div>
                <div class="milestone-item">
                    <div class="milestone-status status-progress">🔄</div>
                    <div class="milestone-info">
                        <div class="milestone-title">核心开发</div>
                        <div class="milestone-amount">$60,000 | 跨链桥开发</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 65%"></div>
                        </div>
                    </div>
                </div>
                <div class="milestone-item">
                    <div class="milestone-status status-pending">⏳</div>
                    <div class="milestone-info">
                        <div class="milestone-title">安全审计</div>
                        <div class="milestone-amount">$40,000 | 待启动</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 风险预警 -->
            <div class="card">
                <div class="card-title">
                    <span>⚠️</span>
                    风险预警
                </div>
                <div class="risk-item risk-high">
                    <div class="risk-icon">🔴</div>
                    <div class="risk-content">
                        <div class="risk-title">逾期风险 [HIGH]</div>
                        <div class="risk-desc">DeFi聚合器里程碑1已逾期30天</div>
                    </div>
                </div>
                <div class="risk-item risk-medium">
                    <div class="risk-icon">🟡</div>
                    <div class="risk-content">
                        <div class="risk-title">进度滞后 [MEDIUM]</div>
                        <div class="risk-desc">GitHub提交频率下降50%</div>
                    </div>
                </div>
                <div class="risk-item risk-low">
                    <div class="risk-icon">🟢</div>
                    <div class="risk-content">
                        <div class="risk-title">资金使用率 [LOW]</div>
                        <div class="risk-desc">第一阶段资金使用率达90%</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>GCC AI Agent Hackathon 2024 | 分配赛道 | OpenClaw Skill</p>
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
                    backgroundColor: ['#11998e', '#e0e0e0', '#38ef7d']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
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
            self.send_response(404)
            self.end_headers()
    
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

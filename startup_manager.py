#!/usr/bin/env python3
"""
系統啟動管理器
提供友善的命令行介面來管理系統服務
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class SystemManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.services = {
            'database': False,
            'api': False,
            'frontend': False,
            'n8n': False
        }
    
    def check_docker(self):
        """檢查 Docker 是否運行"""
        try:
            subprocess.run(['docker', '--version'], 
                          capture_output=True, 
                          check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def start_database(self):
        """啟動資料庫服務"""
        print("🔄 啟動資料庫服務...")
        try:
            subprocess.run(['docker-compose', 'up', '-d', 'postgres', 'pgadmin'],
                          cwd=self.project_root,
                          check=True)
            print("✅ 資料庫服務已啟動")
            print("   PostgreSQL: localhost:15432")
            print("   pgAdmin: http://localhost:15050")
            self.services['database'] = True
            time.sleep(5)  # 等待資料庫就緒
            return True
        except subprocess.CalledProcessError:
            print("❌ 資料庫服務啟動失敗")
            return False
    
    def start_api(self):
        """啟動 API 服務"""
        print("🔄 啟動 API 服務...")
        api_script = self.project_root / 'api_server.py'
        if not api_script.exists():
            print("❌ api_server.py 不存在")
            return False
        
        try:
            # 在背景執行
            subprocess.Popen([sys.executable, str(api_script)],
                           cwd=self.project_root)
            print("✅ API 服務已啟動")
            print("   URL: http://localhost:5000")
            print("   健康檢查: http://localhost:5000/health")
            self.services['api'] = True
            time.sleep(3)
            return True
        except Exception as e:
            print(f"❌ API 服務啟動失敗: {e}")
            return False
    
    def start_frontend(self):
        """啟動前端服務"""
        print("🔄 啟動前端服務...")
        frontend_dir = self.project_root / 'frontend'
        if not frontend_dir.exists():
            print("❌ frontend 目錄不存在")
            return False
        
        try:
            subprocess.Popen(['npm', 'run', 'dev'],
                           cwd=frontend_dir,
                           shell=True)
            print("✅ 前端服務已啟動")
            print("   URL: http://localhost:5173")
            self.services['frontend'] = True
            return True
        except Exception as e:
            print(f"❌ 前端服務啟動失敗: {e}")
            return False
    
    def start_n8n(self):
        """啟動 N8N 服務（選用）"""
        print("🔄 啟動 N8N 自動化服務...")
        try:
            subprocess.run(['docker-compose', '--profile', 'full', 'up', '-d', 'n8n'],
                          cwd=self.project_root,
                          check=True)
            print("✅ N8N 服務已啟動")
            print("   URL: http://localhost:5678")
            self.services['n8n'] = True
            return True
        except subprocess.CalledProcessError:
            print("❌ N8N 服務啟動失敗")
            return False
    
    def stop_all(self):
        """停止所有服務"""
        print("🛑 停止所有服務...")
        
        # 停止 Docker 容器
        try:
            subprocess.run(['docker-compose', 'down'],
                          cwd=self.project_root,
                          check=True)
            print("✅ Docker 容器已停止")
        except subprocess.CalledProcessError:
            print("⚠️  Docker 容器停止失敗")
        
        print("✅ 所有服務已停止")
    
    def show_status(self):
        """顯示服務狀態"""
        print("\n" + "="*50)
        print("系統服務狀態")
        print("="*50)
        
        for service, status in self.services.items():
            symbol = "✅" if status else "⭕"
            print(f"{symbol} {service.capitalize()}: {'運行中' if status else '未啟動'}")
        
        print("="*50 + "\n")
    
    def start_all(self, include_n8n=False):
        """啟動所有服務"""
        print("\n" + "="*50)
        print("AI 投資分析儀 - 系統啟動管理器")
        print("="*50 + "\n")
        
        # 檢查 Docker
        if not self.check_docker():
            print("❌ Docker 未安裝或未啟動")
            print("   請先安裝並啟動 Docker Desktop")
            return False
        
        print("✅ Docker 服務正常\n")
        
        # 依序啟動服務
        steps = [
            ("資料庫", self.start_database),
            ("API", self.start_api),
            ("前端", self.start_frontend),
        ]
        
        if include_n8n:
            steps.append(("N8N", self.start_n8n))
        
        for name, func in steps:
            if not func():
                print(f"\n❌ {name}服務啟動失敗，停止後續啟動")
                return False
            print()
        
        print("="*50)
        print("🎉 系統啟動完成！")
        print("="*50)
        print("\n📊 可用服務：")
        print("   - 前端應用: http://localhost:5173")
        print("   - API 服務: http://localhost:5000")
        print("   - pgAdmin:  http://localhost:15050")
        if include_n8n:
            print("   - N8N:      http://localhost:5678")
        print("\n💡 提示：按 Ctrl+C 不會停止背景服務")
        print("   要停止服務請執行: python startup_manager.py stop\n")
        
        self.show_status()
        return True

def main():
    manager = SystemManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            include_n8n = '--n8n' in sys.argv
            manager.start_all(include_n8n=include_n8n)
        elif command == 'stop':
            manager.stop_all()
        elif command == 'status':
            manager.show_status()
        else:
            print("用法:")
            print("  python startup_manager.py start [--n8n]  # 啟動所有服務")
            print("  python startup_manager.py stop           # 停止所有服務")
            print("  python startup_manager.py status         # 檢查服務狀態")
    else:
        # 預設啟動所有服務（不含 N8N）
        manager.start_all(include_n8n=False)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
        sys.exit(0)

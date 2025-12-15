#!/usr/bin/env python
# coding:utf-8
"""演示如何在主应用中集成 RPC 服务器"""

import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
ROOT_PATH = Path(__file__).parent
sys.path.insert(0, str(ROOT_PATH))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer

from app.rpc import start_rpc_server, stop_rpc_server
from app.rpc.signalr_client import signalr_client
from app.common.config import cfg


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoCaptioner with RPC")
        self.setGeometry(100, 100, 400, 300)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 状态标签
        self.status_label = QLabel("RPC 状态: 未启动")
        layout.addWidget(self.status_label)

        # 启动 RPC 按钮
        self.start_btn = QPushButton("启动 RPC 服务器")
        self.start_btn.clicked.connect(self.start_rpc)
        layout.addWidget(self.start_btn)

        # 停止 RPC 按钮
        self.stop_btn = QPushButton("停止 RPC 服务器")
        self.stop_btn.clicked.connect(self.stop_rpc)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)

        # 连接状态标签
        self.connection_label = QLabel("SignalR: 未连接")
        layout.addWidget(self.connection_label)

        # 创建定时器更新状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # 每秒更新一次

        self.rpc_started = False

    def start_rpc(self):
        """启动 RPC 服务器"""
        if not self.rpc_started:
            host = cfg.rpc_host.value
            port = cfg.rpc_port.value
            start_rpc_server(host=host, port=port)
            self.rpc_started = True
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText(f"RPC 状态: 运行中 (http://{host}:{port})")

    def stop_rpc(self):
        """停止 RPC 服务器"""
        if self.rpc_started:
            stop_rpc_server()
            self.rpc_started = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("RPC 状态: 已停止")

    def update_status(self):
        """更新连接状态"""
        if signalr_client.is_connected:
            self.connection_label.setText(
                f"SignalR: 已连接 ({signalr_client.master_url})"
            )
        else:
            self.connection_label.setText("SignalR: 未连接")

    def closeEvent(self, event):
        """关闭事件"""
        if self.rpc_started:
            stop_rpc_server()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

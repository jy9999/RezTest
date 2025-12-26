#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rez Qt GUI 应用
基于 PyQt5 的图形界面，提供完整的包管理和环境管理功能
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
    QLabel, QSplitter, QTreeWidget, QTreeWidgetItem, QComboBox, 
    QStatusBar, QMessageBox, QDialog, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon

# 配置 Rez 包搜索路径
os.environ['REZ_PACKAGES_PATH'] = r'D:\UE\RezTest\my_packages'

from rez import packages
from rez.config import config
from rez.resolved_context import ResolvedContext
from rez.version import Version

# ---- 新增兼容函数 ----
def get_family_by_name(family_name):
    for family in packages.iter_package_families():
        if family.name == family_name:
            return family
    return None


class PackageWorker(QThread):
    """后台加载包的线程"""
    packages_loaded = pyqtSignal(list)
    
    def run(self):
        try:
            families = []
            for family in packages.iter_package_families():
                families.append(family.name)
            families.sort()
            self.packages_loaded.emit(families)
        except Exception as e:
            self.packages_loaded.emit([f"Error: {str(e)}"])


class PackageBrowserTab(QWidget):
    """包浏览器标签"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_packages()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        # 左侧：包列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("可用包:"))
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索包...")
        self.search_input.textChanged.connect(self.filter_packages)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        self.package_list = QListWidget()
        self.package_list.itemClicked.connect(self.on_package_selected)
        left_layout.addWidget(self.package_list)
        
        # 右侧：包详情
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("包详情:"))
        
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(2)
        self.detail_table.setHorizontalHeaderLabels(["属性", "值"])
        self.detail_table.setColumnWidth(0, 150)
        self.detail_table.setColumnWidth(1, 300)
        right_layout.addWidget(self.detail_table)
        
        # 版本列表
        right_layout.addWidget(QLabel("版本:"))
        self.version_list = QListWidget()
        right_layout.addWidget(self.version_list)
        
        # 创建分割线
        splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        self.current_packages = []
    
    def load_packages(self):
        """后台加载包"""
        self.worker = PackageWorker()
        self.worker.packages_loaded.connect(self.on_packages_loaded)
        self.worker.start()
    
    def on_packages_loaded(self, pkg_list):
        """包加载完成"""
        self.current_packages = pkg_list
        self.package_list.clear()
        for pkg in pkg_list:
            if not pkg.startswith("Error"):
                self.package_list.addItem(pkg)
    
    def filter_packages(self):
        """过滤包列表"""
        search_text = self.search_input.text().lower()
        self.package_list.clear()
        for pkg in self.current_packages:
            if search_text in pkg.lower():
                self.package_list.addItem(pkg)
    
    def on_package_selected(self, item):
        """选中包时显示详情"""
        pkg_name = item.text()
        try:
            family = get_family_by_name(pkg_name)
            if family:
                self.show_package_details(family)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取包信息失败: {str(e)}")
    
    def show_package_details(self, family):
        """显示包详情"""
        self.detail_table.setRowCount(0)
        self.add_detail_row("包名", family.name)
        self.add_detail_row("包族", family.name)
        self.version_list.clear()
        versions = []
        for pkg in family.iter_packages():
            versions.append(str(pkg.version))
            self.version_list.addItem(str(pkg.version))
        self.add_detail_row("版本数", str(len(versions)))
    
    def add_detail_row(self, key, value):
        """添加详情行"""
        row = self.detail_table.rowCount()
        self.detail_table.insertRow(row)
        self.detail_table.setItem(row, 0, QTableWidgetItem(key))
        self.detail_table.setItem(row, 1, QTableWidgetItem(str(value)))


class DependenciesTab(QWidget):
    """依赖关系标签"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 包选择
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("选择包:"))
        self.package_combo = QComboBox()
        self.load_packages_combo()
        select_layout.addWidget(self.package_combo)
        
        refresh_btn = QPushButton("刷新依赖")
        refresh_btn.clicked.connect(self.show_dependencies)
        select_layout.addWidget(refresh_btn)
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # 依赖树
        layout.addWidget(QLabel("依赖树:"))
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["包", "版本"])
        layout.addWidget(self.tree)
        
        self.setLayout(layout)
    
    def load_packages_combo(self):
        """加载包到下拉框"""
        try:
            self.package_combo.clear()
            for family in packages.iter_package_families():
                # 获取该包族的所有版本
                versions = list(family.iter_packages())
                if versions:
                    latest_pkg = versions[-1]  # 最新版本
                    self.package_combo.addItem(
                        f"{family.name}",
                        f"{family.name}-{latest_pkg.version}"
                    )
        except Exception as e:
            print(f"加载包失败: {e}")
    
    def show_dependencies(self):
        """显示依赖关系"""
        pkg_str = self.package_combo.currentData()
        if not pkg_str:
            return
        
        self.tree.clear()
        try:
            ctx = ResolvedContext([pkg_str])
            
            # 根节点
            root = QTreeWidgetItem([pkg_str, ""])
            self.tree.addTopLevelItem(root)
            
            # 添加依赖
            for pkg in ctx.resolved_packages:
                child = QTreeWidgetItem([pkg.qualified_name, str(pkg.version)])
                root.addChild(child)
            
            root.setExpanded(True)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"解析依赖失败: {str(e)}")


class EnvironmentTab(QWidget):
    """环境管理标签"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 包选择区域
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("添加包:"))
        self.package_input = QLineEdit()
        self.package_input.setPlaceholderText("例: python-3.9, maya-2022")
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_package_to_env)
        select_layout.addWidget(self.package_input)
        select_layout.addWidget(add_btn)
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # 环境包列表
        layout.addWidget(QLabel("环境中的包:"))
        self.env_list = QListWidget()
        layout.addWidget(self.env_list)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        resolve_btn = QPushButton("解析环境")
        resolve_btn.clicked.connect(self.resolve_environment)
        btn_layout.addWidget(resolve_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_environment)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 结果显示
        layout.addWidget(QLabel("解析结果:"))
        self.result_text = QTableWidget()
        self.result_text.setColumnCount(2)
        self.result_text.setHorizontalHeaderLabels(["包", "版本"])
        layout.addWidget(self.result_text)
        
        self.setLayout(layout)
        self.env_packages = []
    
    def add_package_to_env(self):
        """添加包到环境"""
        pkg_text = self.package_input.text().strip()
        if not pkg_text:
            return

        # 支持用逗号分隔一次添加多个，如: python-3.9,maya-2022
        entries = [p.strip() for p in pkg_text.split(",") if p.strip()]
        if entries:
            self.env_packages.extend(entries)
            for p in entries:
                self.env_list.addItem(p)

        #region agent log
        import time, json
        try:
            with open(r"e:\UE\RezTest\.cursor\debug.log", "a", encoding="utf-8") as __f:
                __f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "env-add",
                    "hypothesisId": "H1-comma-split",
                    "location": "rez_qt_gui.py:add_package_to_env",
                    "message": "added packages",
                    "data": {"raw": pkg_text, "entries": entries, "env_packages": list(self.env_packages)},
                    "timestamp": int(time.time() * 1000)
                }) + "\n")
        except Exception:
            pass
        #endregion

        self.package_input.clear()
    
    def clear_environment(self):
        """清空环境"""
        self.env_packages.clear()
        self.env_list.clear()
        self.result_text.setRowCount(0)
    
    def resolve_environment(self):
        """解析环境"""
        if not self.env_packages:
            QMessageBox.information(self, "提示", "请先添加包")
            return
        
        try:
            #region agent log
            import time, json
            try:
                with open(r"e:\UE\RezTest\.cursor\debug.log", "a", encoding="utf-8") as __f:
                    __f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "env-resolve",
                        "hypothesisId": "H1-comma-split",
                        "location": "rez_qt_gui.py:resolve_environment BEFORE",
                        "message": "resolving",
                        "data": {"env_packages": list(self.env_packages)},
                        "timestamp": int(time.time() * 1000)
                    }) + "\n")
            except Exception:
                pass
            #endregion

            ctx = ResolvedContext(self.env_packages)
            
            self.result_text.setRowCount(0)
            for pkg in ctx.resolved_packages:
                row = self.result_text.rowCount()
                self.result_text.insertRow(row)
                self.result_text.setItem(row, 0, QTableWidgetItem(pkg.qualified_name))
                self.result_text.setItem(row, 1, QTableWidgetItem(str(pkg.version)))
            
            QMessageBox.information(self, "成功", f"已解析 {len(ctx.resolved_packages)} 个包")
        except Exception as e:
            #region agent log
            try:
                with open(r"e:\UE\RezTest\.cursor\debug.log", "a", encoding="utf-8") as __f:
                    __f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "env-resolve",
                        "hypothesisId": "H1-comma-split",
                        "location": "rez_qt_gui.py:resolve_environment EXCEPTION",
                        "message": "resolve failed",
                        "data": {"env_packages": list(self.env_packages), "err": str(e)},
                        "timestamp": int(time.time() * 1000)
                    }) + "\n")
            except Exception:
                pass
            #endregion
            QMessageBox.warning(self, "错误", f"解析失败: {str(e)}")


class StatusTab(QWidget):
    """状态信息标签"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.show_status()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(2)
        self.status_table.setHorizontalHeaderLabels(["配置项", "值"])
        self.status_table.setColumnWidth(0, 250)
        self.status_table.setColumnWidth(1, 400)
        layout.addWidget(self.status_table)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.show_status)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
    
    def show_status(self):
        """显示系统状态"""
        self.status_table.setRowCount(0)
        
        try:
            # 添加 Rez 版本信息
            import rez
            self.add_status_row("Rez 版本", rez.__version__)
            
            # 添加配置信息（兼容不同配置字段）
            pkg_paths = getattr(config, "packages_path", None)
            if pkg_paths is None:
                pkg_paths = getattr(config, "package_paths", "N/A")
            self.add_status_row("包搜索路径", str(pkg_paths))

            self.add_status_row("本地包路径", str(getattr(config, "local_packages_path", "N/A")))
            self.add_status_row("缓存路径", str(getattr(config, "cache_dir", "N/A")))
            self.add_status_row("插件路径", str(getattr(config, "plugin_paths", "N/A")))
            
            # 统计信息
            family_count = len(list(packages.iter_package_families()))
            self.add_status_row("已安装包族数", str(family_count))
            
        except Exception as e:
            self.add_status_row("错误", str(e))
    
    def add_status_row(self, key, value):
        """添加状态行"""
        row = self.status_table.rowCount()
        self.status_table.insertRow(row)
        self.status_table.setItem(row, 0, QTableWidgetItem(key))
        self.status_table.setItem(row, 1, QTableWidgetItem(str(value)))


class RezQtGUI(QMainWindow):
    """Rez Qt GUI 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Rez 包管理系统 - Qt GUI")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央小部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建标签页
        self.tabs = QTabWidget()
        
        # 添加各个标签页
        self.tabs.addTab(PackageBrowserTab(), "📦 包浏览器")
        self.tabs.addTab(DependenciesTab(), "🔗 依赖分析")
        self.tabs.addTab(EnvironmentTab(), "⚙️  环境管理")
        self.tabs.addTab(StatusTab(), "📊 系统状态")
        
        # 设置主布局
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        
        # 添加状态栏
        self.statusBar().showMessage("就绪")
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                padding: 6px;
                border-radius: 4px;
            }
        """)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = RezQtGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

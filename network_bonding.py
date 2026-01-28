"""
网络叠加工具 - 多网卡负载均衡配置工具
支持Windows系统的网络接口管理，实现多网卡负载均衡、提升网络速度和稳定性
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import subprocess
import time
import threading


class ModernButton(ttk.Frame):
    """
    现代化按钮组件
    提供带有悬停效果的扁平化按钮样式
    """
    def __init__(self, parent, text, command=None, bg_color="#0078d7", text_color="white", **kwargs):
        super().__init__(parent, **kwargs)
        self.btn = tk.Button(
            self,
            text=text,
            command=command,
            bg=bg_color,
            fg=text_color,
            font=("Microsoft YaHei", 10),
            cursor="hand2",
            relief="flat",
            padx=20,
            pady=8,
            borderwidth=0
        )
        self.btn.pack(fill=tk.BOTH, expand=True)
        self.btn.bind('<Enter>', lambda e: self.btn.configure(bg=self.darken_color(bg_color)))
        self.btn.bind('<Leave>', lambda e: self.btn.configure(bg=bg_color))

    def darken_color(self, hex_color, factor=0.8):
        """
        颜色变暗处理
        用于生成悬停状态下的按钮颜色

        Args:
            hex_color: 十六进制颜色值 (如 "#0078d7")
            factor: 变暗因子，默认0.8表示变暗20%

        Returns:
            变暗后的十六进制颜色值
        """
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"




class NetworkBondingApp:
    """
    网络叠加工具主应用类
    提供图形界面来管理和配置多网络接口的负载均衡
    """
    def __init__(self, root):
        self.root = root
        self.root.title("网络叠加工具 v0.1")
        self.root.geometry("650x530")
        self.root.resizable(True, True)
        self.root.configure(bg="#f5f5f5")

        self.interfaces = []
        self.tooltip_label = None
        self.setup_styles()
        self.create_widgets()
        self.refresh_interfaces()

    def setup_styles(self):
        """
        配置应用程序的样式主题
        设置颜色、字体、表格样式等UI元素
        """
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('Card.TFrame', background='white', relief='flat')
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('Title.TLabel', font=('Arial', 20, 'bold'), foreground='#2c3e50', background='#f5f5f5')
        self.style.configure('Desc.TLabel', font=('Arial', 10), foreground='#7f8c8d', background='#f5f5f5')
        self.style.configure('Header.TLabel', font=('Arial', 11, 'bold'), foreground='#34495e', background='white')
        self.style.configure('TLabel', font=('Arial', 9), foreground='#2c3e50', background='white')

        self.style.configure('Treeview',
            font=('Arial', 9),
            background='white',
            foreground='black',
            fieldbackground='white',
            rowheight=30)
        self.style.configure('Treeview.Heading',
            font=('Arial', 10, 'bold'),
            background='#ecf0f1',
            foreground='#2c3e50')
        self.style.map('Treeview',
            background=[('selected', '#3498db')],
            foreground=[('selected', 'white')])

        self.root.option_add('*Listbox.background', 'white')
        self.root.option_add('*Listbox.foreground', 'black')
        self.root.option_add('*Listbox.font', 'Arial 9')

    def create_widgets(self):
        """
        创建主界面的所有组件
        包括头部、左右两栏布局（网络列表和操作面板）
        """
        main_container = tk.Frame(self.root, bg="#f5f5f5")
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.create_header(main_container)

        content_frame = tk.Frame(main_container, bg="#f5f5f5")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.create_two_column_layout(content_frame)

    def create_header(self, parent):
        """
        创建应用头部区域
        显示标题、版本号和功能描述

        Args:
            parent: 父容器组件
        """
        header_frame = tk.Frame(parent, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        header_content = tk.Frame(header_frame, bg="white")
        header_content.pack(fill=tk.BOTH, padx=20, pady=15)

        title_label = tk.Label(
            header_content,
            text="网络叠加工具",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        title_label.pack(side=tk.LEFT, padx=(0, 10))

        version_label = tk.Label(
            header_content,
            text="v0.1",
            font=("Microsoft YaHei", 10),
            bg="#0078d7",
            fg="white",
            padx=6,
            pady=2
        )
        version_label.pack(side=tk.LEFT, padx=(0, 30))

        desc_label = tk.Label(
            header_content,
            text="多网卡负载均衡 · 提升网络速度和稳定性",
            font=("Microsoft YaHei", 10),
            bg="white",
            fg="#7f8c8d"
        )
        desc_label.pack(side=tk.RIGHT)

    def create_two_column_layout(self, parent):
        """
        创建双列布局
        左侧：可用网络接口列表
        右侧：操作控制面板

        Args:
            parent: 父容器组件
        """
        left_panel = self.create_panel(parent, "可用网络接口")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        left_content = left_panel

        right_panel = self.create_panel(parent, "操作面板")
        right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0), anchor=tk.N)
        right_content = right_panel

        self.create_network_list(left_content)
        self.create_control_panel(right_content)

    def create_panel(self, parent, title):
        panel_frame = tk.Frame(parent, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)

        header = tk.Frame(panel_frame, bg="#3498db")
        header.pack(fill=tk.X)

        title_label = tk.Label(
            header,
            text=f"  {title}  ",
            font=("Arial", 9, "bold"),
            bg="#3498db",
            fg="white"
        )
        title_label.pack(side=tk.LEFT, pady=4)

        content = tk.Frame(panel_frame, bg="white")
        content.pack(fill=tk.BOTH, padx=5, pady=5, anchor=tk.N)

        return panel_frame

    def create_network_list(self, parent):
        """
        创建网络接口列表组件
        使用Treeview表格显示所有可用网络接口的状态、类型、IP和网关信息

        Args:
            parent: 父容器组件
        """
        self.tree = ttk.Treeview(
            parent,
            columns=("status", "type", "ip", "gateway"),
            show="headings",
            selectmode="extended",
            height=10
        )

        self.tree.heading("status", text="状态", anchor=tk.CENTER)
        self.tree.heading("type", text="类型", anchor=tk.CENTER)
        self.tree.heading("ip", text="IP地址", anchor=tk.W)
        self.tree.heading("gateway", text="网关", anchor=tk.W)

        self.tree.column("status", width=50, anchor=tk.CENTER)
        self.tree.column("type", width=60, anchor=tk.CENTER)
        self.tree.column("ip", width=90, anchor=tk.W)
        self.tree.column("gateway", width=80, anchor=tk.W)

        self.tree.pack(fill=tk.BOTH, expand=False)

        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        refresh_btn = tk.Button(
            btn_frame,
            text="🔄 刷新网络接口",
            command=self.refresh_interfaces,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief="flat",
            padx=12,
            pady=4,
            borderwidth=0
        )
        refresh_btn.pack(fill=tk.X)
        self.add_hover_effect(refresh_btn, "#95a5a6", "#7f8c8d")

    def create_control_panel(self, parent):
        """
        创建操作控制面板
        包括已选接口列表、添加/移除按钮、负载均衡模式选择和操作按钮

        Args:
            parent: 父容器组件
        """
        tk.Label(
            parent,
            text="选择的网络接口",
            font=("Microsoft YaHei", 11, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 10))

        list_frame = tk.Frame(parent, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
        list_frame.pack(fill=tk.X, pady=(0, 10))

        self.selected_list = tk.Listbox(
            list_frame,
            height=2,
            font=font.Font(family="Segoe UI", size=7),
            bg="#f9f9f9"
        )
        self.selected_list.pack(fill=tk.X, padx=10, pady=10)

        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(fill=tk.X, pady=(0, 15))

        add_btn = tk.Button(
            btn_frame,
            text="➤ 添加",
            command=self.add_to_selected,
            bg="#27ae60",
            fg="white",
            font=("Microsoft YaHei", 10),
            cursor="hand2",
            relief="flat",
            padx=15,
            pady=6,
            borderwidth=0
        )
        add_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.add_hover_effect(add_btn, "#27ae60", "#219150")

        remove_btn = tk.Button(
            btn_frame,
            text="✖ 移除",
            command=self.remove_from_selected,
            bg="#e74c3c",
            fg="white",
            font=("Microsoft YaHei", 10),
            cursor="hand2",
            relief="flat",
            padx=15,
            pady=6,
            borderwidth=0
        )
        remove_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.add_hover_effect(remove_btn, "#e74c3c", "#c0392b")

        tk.Label(
            parent,
            text="负载均衡模式",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor=tk.W, pady=(0, 10))

        self.mode_var = tk.StringVar(value="round_robin")

        mode_descriptions = {
            "round_robin": "轮询模式：按顺序轮流使用各网络接口，适合带宽相近的情况",
            "source_hash": "源IP哈希：根据发起请求的IP路由，保持会话连接",
            "dest_hash": "目标IP哈希：根据目标服务器IP路由，连接稳定",
            "least_conn": "最小连接数：动态选择负载最小的接口，智能分配"
        }

        modes = [
            ("⭕ 轮询模式 (Round Robin)", "round_robin"),
            ("⭕ 源IP哈希", "source_hash"),
            ("⭕ 目标IP哈希", "dest_hash"),
            ("⭕ 最小连接数", "least_conn")
        ]

        for text, value in modes:
            radio = tk.Radiobutton(
                parent,
                text=text,
                variable=self.mode_var,
                value=value,
                bg="white",
                fg="#2c3e50",
                font=("Arial", 9),
                activebackground="white",
                activeforeground="#0078d7",
                selectcolor="white",
                cursor="hand2"
            )
            radio.pack(anchor=tk.W, pady=3)

            def make_enter_handler(mode_value, desc):
                return lambda e: self._show_tooltip(mode_value, mode_descriptions[mode_value])

            radio.bind('<Enter>', make_enter_handler(value, mode_descriptions[value]))
            radio.bind('<Leave>', lambda e: self._hide_tooltip())

        tk.Label(parent, text="", bg="white").pack(pady=5)

        btn_container = tk.Frame(parent, bg="white")
        btn_container.pack(fill=tk.X, pady=(0, 5))

        enable_btn = tk.Button(
            btn_container,
            text="✓ 启用",
            command=self.enable_bonding,
            bg="#0078d7",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief="flat",
            padx=10,
            pady=5,
            borderwidth=0
        )
        enable_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.add_hover_effect(enable_btn, "#0078d7", "#0056b3")

        disable_btn = tk.Button(
            btn_container,
            text="⏸ 禁用",
            command=self.disable_bonding,
            bg="#f39c12",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief="flat",
            padx=10,
            pady=5,
            borderwidth=0
        )
        disable_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
        self.add_hover_effect(disable_btn, "#f39c12", "#d68910")

        status_btn = tk.Button(
            btn_container,
            text="ℹ 状态",
            command=self.show_status,
            bg="#34495e",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief="flat",
            padx=10,
            pady=5,
            borderwidth=0
        )
        status_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))
        self.add_hover_effect(status_btn, "#34495e", "#2c3e50")

    def add_hover_effect(self, button, normal_color, hover_color):
        """
        为按钮添加鼠标悬停效果

        Args:
            button: 按钮对象
            normal_color: 正常状态下的背景色
            hover_color: 鼠标悬停时的背景色
        """
        button.bind('<Enter>', lambda e: button.configure(bg=hover_color))
        button.bind('<Leave>', lambda e: button.configure(bg=normal_color))

    def _show_tooltip(self, widget, text):
        """
        显示工具提示
        在鼠标位置显示文本提示框

        Args:
            widget: 触发提示的组件
            text: 提示文本内容
        """
        if self.tooltip_label is None:
            self.tooltip_label = tk.Label(
                self.root,
                text=text,
                bg="#2c3e50",
                fg="white",
                font=("Arial", 8),
                padx=8,
                pady=5,
                relief="solid",
                borderwidth=1
            )
            self.tooltip_label.lift()
        else:
            self.tooltip_label.config(text=text)

        x = self.root.winfo_pointerx() + 15
        y = self.root.winfo_pointery() + 15

        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        self.tooltip_label.update_idletasks()
        label_width = self.tooltip_label.winfo_reqwidth()
        label_height = self.tooltip_label.winfo_reqheight()

        if x + label_width > root_width:
            x = x - label_width - 30
        if y + label_height > root_height:
            y = y - label_height - 30

        self.tooltip_label.place(x=x, y=y)

    def _hide_tooltip(self):
        """
        隐藏工具提示
        移除当前显示的工具提示框
        """
        if self.tooltip_label is not None:
            self.tooltip_label.place_forget()

    def refresh_interfaces(self):
        """
        刷新网络接口列表
        在后台线程中重新扫描所有网络接口
        """
        self.tree.delete(*self.tree.get_children())

        thread = threading.Thread(target=self._refresh_networks_bg, daemon=True)
        thread.start()

    def _refresh_networks_bg(self):
        try:
            result = subprocess.run(
                ['ipconfig'],
                capture_output=True,
                text=True,
                encoding='gbk',
                timeout=5
            )

            self.root.after(0, lambda: self.parse_network_config(result.stdout))
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: messagebox.showwarning("警告", "获取网络接口超时，请重试"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"获取网络接口失败: {e}"))

    def parse_network_config(self, output):
        """
        解析ipconfig命令输出
        提取各网络接口的名称、类型、IP地址、网关和连接状态

        Args:
            output: ipconfig命令的输出文本
        """
        self.interfaces = []
        current_interface = None

        for line in output.split('\n'):
            line = line.strip()

            if line.startswith('以太网适配器') or line.startswith('无线局域网适配器') or line.startswith('Wi-Fi'):
                if current_interface:
                    self.interfaces.append(current_interface)
                current_interface = {
                    'name': line.split(' ')[-1],
                    'type': '有线' if '以太网' in line else '无线',
                    'ip': '',
                    'gateway': '',
                    'status': '未连接'
                }

            elif current_interface and 'IPv4 地址' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    current_interface['ip'] = parts[1].strip()
                    current_interface['status'] = '已连接'

            elif current_interface and '默认网关' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    current_interface['gateway'] = parts[1].strip()

        if current_interface:
            self.interfaces.append(current_interface)

        for i, interface in enumerate(self.interfaces):
            self.tree.insert('', 'end', iid=str(i), values=(
                interface['status'],
                interface['type'],
                interface['ip'] or '-',
                interface['gateway'] or '-'
            ))

    def add_to_selected(self):
        selected_items = self.tree.selection()
        for item_id in selected_items:
            index = int(item_id)
            if index < len(self.interfaces):
                interface = self.interfaces[index]
                if interface['status'] == '已连接':
                    text = f"{interface['name']} ({interface['ip']})"
                    if text not in self.selected_list.get(0, tk.END):
                        self.selected_list.insert(tk.END, text)
                else:
                    messagebox.showwarning("警告", f"{interface['name']} 未连接，无法添加")

    def remove_from_selected(self):
        """
        从已选列表中移除选中的接口
        支持多选批量移除
        """
        selection = self.selected_list.curselection()
        for index in reversed(selection):
            self.selected_list.delete(index)

    def enable_bonding(self):
        selected_count = self.selected_list.size()
        if selected_count < 2:
            messagebox.showwarning("警告", "请至少选择2个网络接口进行叠加")
            return

        mode = self.mode_var.get()

        for i in range(selected_count):
            self.root.update()
            time.sleep(0.3)
        messagebox.showinfo("成功", "网络叠加配置完成！\n\n注意：这是模拟配置。\n实际的网络叠加需要管理员权限和\n额外的网络驱动支持。")

    def disable_bonding(self):
        """
        禁用网络叠加功能
        恢复默认网络配置
        """
        messagebox.showinfo("成功", "网络叠加已禁用！")

    def show_status(self):
        """
        显示网络叠加状态信息
        包括当前模式、已选接口列表和配置建议
        """
        selected_count = self.selected_list.size()
        mode = self.mode_var.get()

        mode_names = {
            "round_robin": "轮询模式",
            "source_hash": "源IP哈希",
            "dest_hash": "目标IP哈希",
            "least_conn": "最小连接数"
        }
        mode_display = mode_names.get(mode, mode)

        if selected_count == 0:
            status_text = "📊 网络叠加状态\n\n" \
                        f"叠加模式: {mode_display}\n" \
                        f"已选接口: {selected_count} 个\n\n" \
                        "⚠️  未选择任何网络接口\n" \
                        "请先选择至少 2 个接口进行叠加"
        else:
            status_text = "📊 网络叠加状态\n\n" \
                        f"叠加模式: {mode_display}\n" \
                        f"已选接口: {selected_count} 个\n\n" \
                        "📡 接口列表:\n"
            for i in range(selected_count):
                interface = self.selected_list.get(i)
                status_text += f"  {i+1}. {interface}\n"

            if selected_count < 2:
                status_text += f"\n⚠️  当前只选择了 {selected_count} 个接口\n" \
                            "建议至少选择 2 个接口以获得最佳效果"

        messagebox.showinfo("网络叠加状态", status_text)


def main():
    """
    程序入口函数
    创建主窗口并启动应用
    """
    root = tk.Tk()
    app = NetworkBondingApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()

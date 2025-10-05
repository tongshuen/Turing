import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import importlib.util
import subprocess
import threading
import re

class TuringIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Turing (T) 语言 IDE")
        self.root.geometry("1000x700")
        
        # 当前解释器实例
        self.interpreter = None
        self.interpreter_version = None
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主界面
        self.create_main_interface()
        
        # 设置语法高亮
        self.setup_highlight_tags()
        
        # 加载可用解释器
        self.load_interpreters()
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="打开", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="剪切", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="复制", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="粘贴", command=self.paste, accelerator="Ctrl+V")
        menubar.add_cascade(label="编辑", menu=edit_menu)
        
        # 运行菜单
        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="运行", command=self.run_code, accelerator="F5")
        run_menu.add_command(label="停止", command=self.stop_execution, accelerator="Ctrl+F2")
        run_menu.add_command(label="单步执行", command=self.step_execution, accelerator="F10")
        menubar.add_cascade(label="运行", menu=run_menu)
        
        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="选择解释器", command=self.select_interpreter)
        settings_menu.add_command(label="主题设置", command=self.theme_settings)
        menubar.add_cascade(label="设置", menu=settings_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="帮助文档", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # 绑定快捷键
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<F5>', lambda e: self.run_code())
        self.root.bind('<Control-F2>', lambda e: self.stop_execution())
        self.root.bind('<F10>', lambda e: self.step_execution())
        
    def create_main_interface(self):
        """创建主界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 顶部工具栏
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # 解释器选择
        ttk.Label(toolbar, text="解释器:").pack(side=tk.LEFT, padx=(0, 5))
        self.interpreter_var = tk.StringVar()
        self.interpreter_combo = ttk.Combobox(toolbar, textvariable=self.interpreter_var, state="readonly")
        self.interpreter_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.interpreter_combo.bind('<<ComboboxSelected>>', self.on_interpreter_selected)
        
        # 运行按钮
        ttk.Button(toolbar, text="运行 (F5)", command=self.run_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="停止 (Ctrl+F2)", command=self.stop_execution).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="单步 (F10)", command=self.step_execution).pack(side=tk.LEFT, padx=5)
        
        # 代码编辑区和输出区分割
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 代码编辑器
        code_frame = ttk.Frame(paned_window)
        paned_window.add(code_frame, weight=70)
        
        ttk.Label(code_frame, text="代码编辑器:").pack(anchor=tk.W)
        self.code_text = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD, font=("Consolas", 11))
        self.code_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 添加行号
        self.add_line_numbers()
        
        # 输出区域
        output_frame = ttk.Frame(paned_window)
        paned_window.add(output_frame, weight=30)
        
        # 输出标签
        output_notebook = ttk.Notebook(output_frame)
        output_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 程序输出标签页
        output_tab = ttk.Frame(output_notebook)
        output_notebook.add(output_tab, text="输出")
        
        self.output_text = scrolledtext.ScrolledText(output_tab, wrap=tk.WORD, font=("Consolas", 11))
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)
        
        # 状态输出标签页
        state_tab = ttk.Frame(output_notebook)
        output_notebook.add(state_tab, text="状态")
        
        self.state_text = scrolledtext.ScrolledText(state_tab, wrap=tk.WORD, font=("Consolas", 11))
        self.state_text.pack(fill=tk.BOTH, expand=True)
        self.state_text.config(state=tk.DISABLED)
        
        # 底部状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 当前文件路径
        self.current_file = None
        
        # 执行线程
        self.execution_thread = None
        self.stop_execution_flag = False
        
    def setup_highlight_tags(self):
        """设置语法高亮的标签"""
        # 定义不同指令的颜色
        self.code_text.tag_configure('basic_ops', foreground='blue')
        self.code_text.tag_configure('io_ops', foreground='green')
        self.code_text.tag_configure('loop_ops', foreground='red')
        self.code_text.tag_configure('extended_ops', foreground='purple')
        self.code_text.tag_configure('comment', foreground='gray')
        
        # 绑定按键事件来实时更新高亮
        self.code_text.bind('<KeyRelease>', self.highlight_syntax)
        self.code_text.bind('<ButtonRelease>', self.highlight_syntax)
        
    def highlight_syntax(self, event=None):
        """执行语法高亮"""
        # 定义不同指令的分类
        basic_ops = ['>', '<', '+', '-']
        io_ops = ['.', ',']
        loop_ops = ['[', ']']
        extended_ops = ['!', '@', '#', '$', '%', '^', '&', '*']
        
        # 先移除所有现有的标签
        for tag in ['basic_ops', 'io_ops', 'loop_ops', 'extended_ops', 'comment']:
            self.code_text.tag_remove(tag, '1.0', tk.END)
        
        # 获取所有文本
        text = self.code_text.get('1.0', tk.END)
        
        # 高亮注释（以#开头的行）
        for line_num, line in enumerate(text.split('\n'), start=1):
            if line.strip().startswith('#'):
                start_pos = f"{line_num}.0"
                end_pos = f"{line_num}.end"
                self.code_text.tag_add('comment', start_pos, end_pos)
        
        # 高亮指令
        for i, char in enumerate(text):
            pos = f'1.0 + {i} chars'
            if char in basic_ops:
                self.code_text.tag_add('basic_ops', pos, f'{pos} + 1 chars')
            elif char in io_ops:
                self.code_text.tag_add('io_ops', pos, f'{pos} + 1 chars')
            elif char in loop_ops:
                self.code_text.tag_add('loop_ops', pos, f'{pos} + 1 chars')
            elif char in extended_ops:
                self.code_text.tag_add('extended_ops', pos, f'{pos} + 1 chars')
    
    def add_line_numbers(self):
        """为代码编辑器添加行号"""
        # 创建一个框架来包含行号和文本
        line_number_frame = ttk.Frame(self.code_text.master)
        line_number_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.line_numbers = tk.Text(line_number_frame, width=4, takefocus=0, 
                                   border=0, background='lightgrey', 
                                   state=tk.DISABLED, font=("Consolas", 11))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # 绑定滚动事件
        self.code_text.config(yscrollcommand=self.on_text_scroll)
        self.line_numbers.config(yscrollcommand=self.on_text_scroll)
        
        # 绑定按键事件更新行号
        self.code_text.bind('<KeyRelease>', self.update_line_numbers)
        self.code_text.bind('<MouseWheel>', self.update_line_numbers)
        
        self.update_line_numbers()
        
    def on_text_scroll(self, *args):
        """同步文本和行号的滚动"""
        self.code_text.yview(*args)
        self.line_numbers.yview(*args)
        
    def update_line_numbers(self, event=None):
        """更新行号显示"""
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete(1.0, tk.END)
        
        # 获取代码行数
        lines = self.code_text.get(1.0, tk.END).count('\n')
        
        # 添加行号
        for i in range(1, lines + 2):
            self.line_numbers.insert(tk.END, f"{i}\n")
            
        self.line_numbers.config(state=tk.DISABLED)
        
        # 更新语法高亮
        self.highlight_syntax()
        
    def load_interpreters(self):
        """加载可用的解释器"""
        interpreter_dir = "./interpreter"
        interpreters = {}
        
        if os.path.exists(interpreter_dir):
            for file in os.listdir(interpreter_dir):
                if file.endswith('.py'):
                    version = file[:-3]  # 去掉.py扩展名
                    interpreters[version] = os.path.join(interpreter_dir, file)
        
        self.interpreters = interpreters
        
        # 更新下拉框
        self.interpreter_combo['values'] = list(interpreters.keys())
        
        if interpreters:
            # 默认选择第一个
            first_version = list(interpreters.keys())[0]
            self.interpreter_var.set(first_version)
            self.load_interpreter(first_version)
        
    def load_interpreter(self, version):
        """加载指定版本的解释器"""
        if version in self.interpreters:
            try:
                file_path = self.interpreters[version]
                
                # 动态导入模块
                spec = importlib.util.spec_from_file_location(f"interpreter_{version}", file_path)
                interpreter_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(interpreter_module)
                
                # 创建解释器实例
                self.interpreter = interpreter_module.TuringInterpreter()
                self.interpreter_version = version
                
                self.status_bar.config(text=f"已加载解释器: {version}")
                
            except Exception as e:
                messagebox.showerror("错误", f"加载解释器失败: {e}")
                self.interpreter = None
                self.interpreter_version = None
        else:
            messagebox.showerror("错误", f"找不到解释器版本: {version}")
    
    def on_interpreter_selected(self, event):
        """当选择解释器时"""
        version = self.interpreter_var.get()
        self.load_interpreter(version)
    
    def select_interpreter(self):
        """选择解释器对话框"""
        if not self.interpreters:
            messagebox.showinfo("信息", "没有找到可用的解释器")
            return
            
        # 创建选择对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("选择解释器")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="可用解释器版本:").pack(pady=10)
        
        # 创建列表框
        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for version in self.interpreters.keys():
            listbox.insert(tk.END, version)
        
        # 选择按钮
        def on_select():
            selection = listbox.curselection()
            if selection:
                version = listbox.get(selection[0])
                self.interpreter_var.set(version)
                self.load_interpreter(version)
                dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="选择", command=on_select).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)
    
    def theme_settings(self):
        """主题设置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("主题设置")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="语法高亮颜色设置:").pack(pady=10)
        
        # 颜色设置控件
        colors_frame = ttk.Frame(dialog)
        colors_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 基本操作颜色
        ttk.Label(colors_frame, text="基本操作 (> < + -):").grid(row=0, column=0, sticky=tk.W)
        self.basic_color_var = tk.StringVar(value='blue')
        ttk.Entry(colors_frame, textvariable=self.basic_color_var).grid(row=0, column=1)
        
        # I/O操作颜色
        ttk.Label(colors_frame, text="I/O操作 (. ,):").grid(row=1, column=0, sticky=tk.W)
        self.io_color_var = tk.StringVar(value='green')
        ttk.Entry(colors_frame, textvariable=self.io_color_var).grid(row=1, column=1)
        
        # 循环操作颜色
        ttk.Label(colors_frame, text="循环操作 ([ ]):").grid(row=2, column=0, sticky=tk.W)
        self.loop_color_var = tk.StringVar(value='red')
        ttk.Entry(colors_frame, textvariable=self.loop_color_var).grid(row=2, column=1)
        
        # 扩展操作颜色
        ttk.Label(colors_frame, text="扩展操作 (! @ # $ % ^ & *):").grid(row=3, column=0, sticky=tk.W)
        self.extended_color_var = tk.StringVar(value='purple')
        ttk.Entry(colors_frame, textvariable=self.extended_color_var).grid(row=3, column=1)
        
        # 注释颜色
        ttk.Label(colors_frame, text="注释 (#):").grid(row=4, column=0, sticky=tk.W)
        self.comment_color_var = tk.StringVar(value='gray')
        ttk.Entry(colors_frame, textvariable=self.comment_color_var).grid(row=4, column=1)
        
        # 应用按钮
        def apply_colors():
            self.code_text.tag_configure('basic_ops', foreground=self.basic_color_var.get())
            self.code_text.tag_configure('io_ops', foreground=self.io_color_var.get())
            self.code_text.tag_configure('loop_ops', foreground=self.loop_color_var.get())
            self.code_text.tag_configure('extended_ops', foreground=self.extended_color_var.get())
            self.code_text.tag_configure('comment', foreground=self.comment_color_var.get())
            self.highlight_syntax()
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="应用", command=apply_colors).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)
    
    def new_file(self):
        """新建文件"""
        self.code_text.delete(1.0, tk.END)
        self.current_file = None
        self.status_bar.config(text="新建文件")
        
    def open_file(self):
        """打开文件"""
        file_path = filedialog.askopenfilename(
            filetypes=[("T语言文件", "*.t"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.code_text.delete(1.0, tk.END)
                self.code_text.insert(1.0, content)
                self.current_file = file_path
                self.status_bar.config(text=f"已打开: {file_path}")
                self.update_line_numbers()
                
            except Exception as e:
                messagebox.showerror("错误", f"打开文件失败: {e}")
    
    def save_file(self):
        """保存文件"""
        if self.current_file:
            file_path = self.current_file
        else:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".t",
                filetypes=[("T语言文件", "*.t"), ("所有文件", "*.*")]
            )
            if not file_path:
                return
            self.current_file = file_path
        
        try:
            content = self.code_text.get(1.0, tk.END)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.status_bar.config(text=f"已保存: {file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {e}")
    
    def undo(self):
        """撤销"""
        try:
            self.code_text.edit_undo()
        except tk.TclError:
            pass
    
    def redo(self):
        """重做"""
        try:
            self.code_text.edit_redo()
        except tk.TclError:
            pass
    
    def cut(self):
        """剪切"""
        self.code_text.event_generate("<<Cut>>")
    
    def copy(self):
        """复制"""
        self.code_text.event_generate("<<Copy>>")
    
    def paste(self):
        """粘贴"""
        self.code_text.event_generate("<<Paste>>")
    
    def run_code(self):
        """运行代码"""
        if not self.interpreter:
            messagebox.showerror("错误", "请先选择解释器")
            return
            
        # 清空输出
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        self.state_text.config(state=tk.NORMAL)
        self.state_text.delete(1.0, tk.END)
        self.state_text.config(state=tk.DISABLED)
        
        # 获取代码
        code = self.code_text.get(1.0, tk.END)
        
        # 在新线程中执行
        self.stop_execution_flag = False
        self.execution_thread = threading.Thread(target=self.execute_code, args=(code, False))
        self.execution_thread.daemon = True
        self.execution_thread.start()
        
        self.status_bar.config(text="正在执行...")
    
    def step_execution(self):
        """单步执行"""
        if not self.interpreter:
            messagebox.showerror("错误", "请先选择解释器")
            return
            
        # 清空输出
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        self.state_text.config(state=tk.NORMAL)
        self.state_text.delete(1.0, tk.END)
        self.state_text.config(state=tk.DISABLED)
        
        # 获取代码
        code = self.code_text.get(1.0, tk.END)
        
        # 在新线程中执行
        self.stop_execution_flag = False
        self.execution_thread = threading.Thread(target=self.execute_code, args=(code, True))
        self.execution_thread.daemon = True
        self.execution_thread.start()
        
        self.status_bar.config(text="单步执行中...")
    
    def stop_execution(self):
        """停止执行"""
        self.stop_execution_flag = True
        self.status_bar.config(text="执行已停止")
    
    def execute_code(self, code, single_step):
        """执行代码"""
        try:
            # 重定向输出到我们的文本区域
            import io
            import contextlib
            
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            # 执行代码
            self.interpreter.execute(code, single_step=single_step)
            
            # 获取输出
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # 更新UI
            self.root.after(0, self.update_output, output)
            
            self.root.after(0, lambda: self.status_bar.config(text="执行完成"))
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def update_output(self, output):
        """更新输出区域"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, output)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def show_error(self, error_msg):
        """显示错误信息"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"\n错误: {error_msg}")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        self.status_bar.config(text=f"执行错误: {error_msg}")
    
    def show_help(self):
        """显示帮助文档"""
        help_window = tk.Toplevel(self.root)
        help_window.title("T语言帮助文档")
        help_window.geometry("800x600")
        
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=("Consolas", 11))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 加载帮助内容
        help_content = """
Turing (T) 机器语言解释器 - 帮助文档

指令集:
  >   数据指针右移
  <   数据指针左移
  +   当前数据值加1
  -   当前数据值减1
  .   输出当前数据值对应的ASCII字符
  ,   输入一个字符并存储其ASCII值
  [   如果当前数据值为0，跳转到匹配的]
  ]   如果当前数据值不为0，跳转到匹配的[
  !   交换纸带A和纸带B当前指针位置的值
  @   将纸带A当前指令复制到纸带B
  #   将纸带B当前值复制到纸带A
  $   纸带B当前值加上纸带A当前指令值
  %   纸带B当前值减去纸带A当前指令值
  ^   纸带B当前值乘以纸带A当前指令值
  &   纸带B当前值除以纸带A当前指令值(非零)
  *   纸带B当前值与纸带A当前指令值异或

纸带:
  解释器使用两个无限长的纸带:
  - 纸带A: 存储指令代码
  - 纸带B: 存储数据值
  纸带初始长度为500，会根据需要自动扩展或收缩。

语法高亮:
  不同类型的指令会显示为不同颜色:
  - 基本操作: 蓝色
  - I/O操作: 绿色
  - 循环操作: 红色
  - 扩展操作: 紫色
  - 注释: 灰色
"""
        help_text.insert(1.0, help_content)
        help_text.config(state=tk.DISABLED)
    
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo("关于", "Turing (T) 语言 IDE\n\n一个基于Tkinter的T语言集成开发环境\n支持多版本解释器和语法高亮")
    
    def run(self):
        """运行IDE"""
        self.root.mainloop()

def main():
    root = tk.Tk()
    ide = TuringIDE(root)
    ide.run()

if __name__ == "__main__":
    main()

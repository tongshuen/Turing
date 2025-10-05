import sys
import re
import readline  # 用于改进命令行输入体验

class TuringInterpreter:
    def __init__(self):
        # 初始化两个纸带，默认长度500
        self.tape_a = [0] * 500  # 指令纸带
        self.tape_b = [0] * 500  # 数据纸带
        self.pointer = 0         # 当前指针位置
        self.instruction_ptr = 0 # 当前执行指令的位置
        self.code = ""           # 原始代码
        self.brackets = {}       # 用于存储循环匹配
        self.debug_mode = False
        self.verbose_mode = False
        self.step_mode = False
        
    def preprocess_code(self, code):
        """预处理代码，去除注释和无效字符"""
        # 只保留有效指令字符
        cleaned_code = re.sub(r'[^><+\-.,\[\]!@#$%^&*]', '', code)
        return cleaned_code
    
    def match_brackets(self, code):
        """匹配循环括号，建立跳转表"""
        stack = []
        brackets = {}
        for pos, cmd in enumerate(code):
            if cmd == '[':
                stack.append(pos)
            elif cmd == ']':
                if stack:
                    start = stack.pop()
                    brackets[start] = pos
                    brackets[pos] = start
        return brackets
    
    def adjust_tape_size(self):
        """根据需要调整纸带大小"""
        required_size = max(len(self.tape_a), abs(self.pointer) + 1)
        if len(self.tape_a) < required_size:
            # 扩展纸带
            extension = [0] * (required_size - len(self.tape_a))
            self.tape_a.extend(extension)
            self.tape_b.extend(extension.copy())
        elif len(self.tape_a) > 500 and required_size < len(self.tape_a) // 2:
            # 收缩纸带，但保持最小500长度
            new_size = max(500, required_size)
            self.tape_a = self.tape_a[:new_size]
            self.tape_b = self.tape_b[:new_size]
    
    def normalize_pointer(self):
        """规范化指针位置"""
        if not self.tape_a:
            self.tape_a = [0]
            self.tape_b = [0]
            self.pointer = 0
            return
        
        if self.pointer < 0:
            self.pointer = abs(self.pointer) % len(self.tape_a)
        elif self.pointer >= len(self.tape_a):
            self.pointer %= len(self.tape_a)
    
    def execute(self, code, single_step=False):
        """执行代码"""
        self.code = self.preprocess_code(code)
        self.brackets = self.match_brackets(self.code)
        self.instruction_ptr = 0
        self.pointer = 0
        
        while self.instruction_ptr < len(self.code):
            cmd = self.code[self.instruction_ptr]
            
            # 调整纸带大小和指针位置
            self.adjust_tape_size()
            self.normalize_pointer()
            
            if self.debug_mode or self.verbose_mode:
                self.show_state()
            
            if cmd == '>':
                self.pointer += 1
            elif cmd == '<':
                self.pointer -= 1
            elif cmd == '+':
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] + 1) % 256
            elif cmd == '-':
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] - 1) % 256
            elif cmd == '.':
                print(chr(self.tape_b[self.pointer]), end='', flush=True)
            elif cmd == ',':
                try:
                    self.tape_b[self.pointer] = ord(sys.stdin.read(1)) % 256
                except:
                    self.tape_b[self.pointer] = 0
            elif cmd == '[':
                if self.tape_b[self.pointer] == 0:
                    self.instruction_ptr = self.brackets[self.instruction_ptr]
            elif cmd == ']':
                if self.tape_b[self.pointer] != 0:
                    self.instruction_ptr = self.brackets[self.instruction_ptr]
            elif cmd == '!':
                # 交换两个纸带的指针位置的值
                self.tape_a[self.pointer], self.tape_b[self.pointer] = self.tape_b[self.pointer], self.tape_a[self.pointer]
            elif cmd == '@':
                # 将纸带A当前指令复制到纸带B
                self.tape_b[self.pointer] = self.tape_a[self.pointer]
            elif cmd == '#':
                # 将纸带B当前值复制到纸带A
                self.tape_a[self.pointer] = self.tape_b[self.pointer]
            elif cmd == '$':
                # 纸带B当前值加上纸带A当前指令值
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] + self.tape_a[self.pointer]) % 256
            elif cmd == '%':
                # 纸带B当前值减去纸带A当前指令值
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] - self.tape_a[self.pointer]) % 256
            elif cmd == '^':
                # 纸带B当前值乘以纸带A当前指令值
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] * self.tape_a[self.pointer]) % 256
            elif cmd == '&':
                # 纸带B当前值除以纸带A当前指令值(非零)
                if self.tape_a[self.pointer] != 0:
                    self.tape_b[self.pointer] = (self.tape_b[self.pointer] // self.tape_a[self.pointer]) % 256
            elif cmd == '*':
                # 纸带B当前值与纸带A当前指令值异或
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] ^ self.tape_a[self.pointer]) % 256
            
            self.instruction_ptr += 1
            
            if single_step:
                input("按Enter继续...")
    
    def show_state(self):
        """显示当前状态"""
        print(f"\n指令指针: {self.instruction_ptr}, 数据指针: {self.pointer}")
        
        # 显示纸带A的指令区域
        start = max(0, self.instruction_ptr - 15)
        end = min(len(self.code), self.instruction_ptr + 16)
        print("纸带A (指令):")
        tape_a_display = list(self.code[start:end])
        if self.instruction_ptr >= start and self.instruction_ptr < end:
            tape_a_display[self.instruction_ptr - start] = f"[{tape_a_display[self.instruction_ptr - start]}]"
        print("".join(tape_a_display))
        
        # 显示纸带B的数据区域
        start_b = max(0, self.pointer - 15)
        end_b = min(len(self.tape_b), self.pointer + 16)
        print("纸带B (数据):")
        tape_b_display = [str(x) for x in self.tape_b[start_b:end_b]]
        if self.pointer >= start_b and self.pointer < end_b:
            tape_b_display[self.pointer - start_b] = f"[{tape_b_display[self.pointer - start_b]}]"
        print(" ".join(tape_b_display))
        
        # 显示当前指令的ASCII表示
        if self.instruction_ptr < len(self.code):
            print(f"当前指令: '{self.code[self.instruction_ptr]}' (ASCII: {ord(self.code[self.instruction_ptr])})")
        
        # 显示纸带B当前值的ASCII表示
        print(f"当前数据: {self.tape_b[self.pointer]} (ASCII: {chr(self.tape_b[self.pointer]) if 32 <= self.tape_b[self.pointer] <= 126 else '非可打印字符'})")

def print_help():
    """打印帮助信息"""
    print("""
Turing (T) 机器语言解释器 - 帮助文档

用法: python turing.py [选项] [文件]

选项:
  -h, --help     显示此帮助信息
  -v, --verbose  显示详细执行过程
  -s, --step     单步执行模式
  -f, --full     显示完整文档

如果没有提供文件参数，解释器将进入交互模式。

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

交互模式:
  在交互模式下，您可以:
  - 直接输入T代码执行
  - 输入"quit"或"exit"退出
  - 输入"clear"清空纸带
  - 输入"state"查看当前状态
""")

def print_full_docs():
    """打印完整文档"""
    print("""
Turing (T) 机器语言解释器 - 完整文档

1. 概述
T是一种基于双纸带模型的图灵完备编程语言，灵感来自Brainfuck但进行了扩展和重构。
它使用两个无限长的纸带：一个用于存储指令(纸带A)，一个用于存储数据(纸带B)。

2. 纸带模型
- 纸带A: 存储指令代码，初始加载用户提供的程序
- 纸带B: 存储数据值，初始全为0
- 指针: 指向当前操作的纸带B位置
- 指令指针: 指向当前执行的纸带A位置

3. 指令集详解
>   数据指针右移一位
<   数据指针左移一位
+   当前数据值加1(模256)
-   当前数据值减1(模256)
.   输出当前数据值对应的ASCII字符
,   从输入读取一个字符并存储其ASCII值
[   开始循环，如果当前数据值为0，跳转到匹配的]
]   结束循环，如果当前数据值不为0，跳转到匹配的[
!   交换纸带A和纸带B当前指针位置的值
@   将纸带A当前指令复制到纸带B
#   将纸带B当前值复制到纸带A
$   纸带B当前值加上纸带A当前指令值
%   纸带B当前值减去纸带A当前指令值
^   纸带B当前值乘以纸带A当前指令值
&   纸带B当前值除以纸带A当前指令值(非零)
*   纸带B当前值与纸带A当前指令值异或

4. 技术细节
- 所有数值操作都是模256的
- 纸带初始长度为500，会根据需要自动扩展
- 当指针超出当前纸带长度时，会自动环绕
- 负数指针取其绝对值

5. 示例程序
5.1 打印"Hello, World!"
++++++++[>++++++++>+++++++++++>+++++<<<-]>.>++.+++++++..+++.>-.
------------.<++++++++.--------.+++.------.--------.>+.

5.2 简单加法器 (输入两个数字，输出它们的和)
,>,<[->+<]>.

5.3 纸带交互示例 (使用纸带A和B的交互功能)
+++@#$  # 将3存入纸带B，然后进行各种操作

6. 实现说明
- 解释器用Python实现
- 支持交互模式和文件模式
- 提供调试和单步执行功能
""")

def interactive_mode(interpreter):
    """交互模式"""
    print("Turing (T) 机器语言解释器 - 交互模式")
    print("输入T代码执行，或输入help获取帮助")
    
    while True:
        try:
            user_input = input("T> ").strip()
            
            if user_input.lower() in ('quit', 'exit'):
                break
            elif user_input.lower() == 'help':
                print_help()
            elif user_input.lower() == 'clear':
                interpreter = TuringInterpreter()
                print("纸带已清空")
            elif user_input.lower() == 'state':
                interpreter.show_state()
            elif user_input:
                interpreter.execute(user_input)
        except KeyboardInterrupt:
            print("\n中断执行")
        except Exception as e:
            print(f"错误: {e}")

def main():
    interpreter = TuringInterpreter()
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-h', '--help'):
            print_help()
        elif sys.argv[1] in ('-f', '--full'):
            print_full_docs()
        elif sys.argv[1] in ('-v', '--verbose'):
            interpreter.verbose_mode = True
            if len(sys.argv) > 2:
                with open(sys.argv[2], 'r') as f:
                    code = f.read()
                interpreter.execute(code)
            else:
                interactive_mode(interpreter)
        elif sys.argv[1] in ('-s', '--step'):
            interpreter.step_mode = True
            if len(sys.argv) > 2:
                with open(sys.argv[2], 'r') as f:
                    code = f.read()
                interpreter.execute(code, single_step=True)
            else:
                interactive_mode(interpreter)
        else:
            with open(sys.argv[1], 'r') as f:
                code = f.read()
            interpreter.execute(code)
    else:
        interactive_mode(interpreter)

if __name__ == "__main__":
    main()
import sys
import re
import readline  # 用于改进命令行输入体验

class TuringInterpreter:
    def __init__(self):
        # 初始化两个纸带，默认长度500
        self.tape_a = [0] * 500  # 指令纸带
        self.tape_b = [0] * 500  # 数据纸带
        self.pointer = 0         # 当前指针位置
        self.instruction_ptr = 0 # 当前执行指令的位置
        self.code = ""           # 原始代码
        self.brackets = {}       # 用于存储循环匹配
        self.debug_mode = False
        self.verbose_mode = False
        self.step_mode = False
        
    def preprocess_code(self, code):
        """预处理代码，去除注释和无效字符"""
        # 只保留有效指令字符
        cleaned_code = re.sub(r'[^><+\-.,\[\]!@#$%^&*]', '', code)
        return cleaned_code
    
    def match_brackets(self, code):
        """匹配循环括号，建立跳转表"""
        stack = []
        brackets = {}
        for pos, cmd in enumerate(code):
            if cmd == '[':
                stack.append(pos)
            elif cmd == ']':
                if stack:
                    start = stack.pop()
                    brackets[start] = pos
                    brackets[pos] = start
        return brackets
    
    def adjust_tape_size(self):
        """根据需要调整纸带大小"""
        required_size = max(len(self.tape_a), abs(self.pointer) + 1)
        if len(self.tape_a) < required_size:
            # 扩展纸带
            extension = [0] * (required_size - len(self.tape_a))
            self.tape_a.extend(extension)
            self.tape_b.extend(extension.copy())
        elif len(self.tape_a) > 500 and required_size < len(self.tape_a) // 2:
            # 收缩纸带，但保持最小500长度
            new_size = max(500, required_size)
            self.tape_a = self.tape_a[:new_size]
            self.tape_b = self.tape_b[:new_size]
    
    def normalize_pointer(self):
        """规范化指针位置"""
        if not self.tape_a:
            self.tape_a = [0]
            self.tape_b = [0]
            self.pointer = 0
            return
        
        if self.pointer < 0:
            self.pointer = abs(self.pointer) % len(self.tape_a)
        elif self.pointer >= len(self.tape_a):
            self.pointer %= len(self.tape_a)
    
    def execute(self, code, single_step=False):
        """执行代码"""
        self.code = self.preprocess_code(code)
        self.brackets = self.match_brackets(self.code)
        self.instruction_ptr = 0
        self.pointer = 0
        
        while self.instruction_ptr < len(self.code):
            cmd = self.code[self.instruction_ptr]
            
            # 调整纸带大小和指针位置
            self.adjust_tape_size()
            self.normalize_pointer()
            
            if self.debug_mode or self.verbose_mode:
                self.show_state()
            
            if cmd == '>':
                self.pointer += 1
            elif cmd == '<':
                self.pointer -= 1
            elif cmd == '+':
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] + 1) % 256
            elif cmd == '-':
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] - 1) % 256
            elif cmd == '.':
                print(chr(self.tape_b[self.pointer]), end='', flush=True)
            elif cmd == ',':
                try:
                    self.tape_b[self.pointer] = ord(sys.stdin.read(1)) % 256
                except:
                    self.tape_b[self.pointer] = 0
            elif cmd == '[':
                if self.tape_b[self.pointer] == 0:
                    self.instruction_ptr = self.brackets[self.instruction_ptr]
            elif cmd == ']':
                if self.tape_b[self.pointer] != 0:
                    self.instruction_ptr = self.brackets[self.instruction_ptr]
            elif cmd == '!':
                # 交换两个纸带的指针位置的值
                self.tape_a[self.pointer], self.tape_b[self.pointer] = self.tape_b[self.pointer], self.tape_a[self.pointer]
            elif cmd == '@':
                # 将纸带A当前指令复制到纸带B
                self.tape_b[self.pointer] = self.tape_a[self.pointer]
            elif cmd == '#':
                # 将纸带B当前值复制到纸带A
                self.tape_a[self.pointer] = self.tape_b[self.pointer]
            elif cmd == '$':
                # 纸带B当前值加上纸带A当前指令值
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] + self.tape_a[self.pointer]) % 256
            elif cmd == '%':
                # 纸带B当前值减去纸带A当前指令值
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] - self.tape_a[self.pointer]) % 256
            elif cmd == '^':
                # 纸带B当前值乘以纸带A当前指令值
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] * self.tape_a[self.pointer]) % 256
            elif cmd == '&':
                # 纸带B当前值除以纸带A当前指令值(非零)
                if self.tape_a[self.pointer] != 0:
                    self.tape_b[self.pointer] = (self.tape_b[self.pointer] // self.tape_a[self.pointer]) % 256
            elif cmd == '*':
                # 纸带B当前值与纸带A当前指令值异或
                self.tape_b[self.pointer] = (self.tape_b[self.pointer] ^ self.tape_a[self.pointer]) % 256
            
            self.instruction_ptr += 1
            
            if single_step:
                input("按Enter继续...")
    
    def show_state(self):
        """显示当前状态"""
        print(f"\n指令指针: {self.instruction_ptr}, 数据指针: {self.pointer}")
        
        # 显示纸带A的指令区域
        start = max(0, self.instruction_ptr - 15)
        end = min(len(self.code), self.instruction_ptr + 16)
        print("纸带A (指令):")
        tape_a_display = list(self.code[start:end])
        if self.instruction_ptr >= start and self.instruction_ptr < end:
            tape_a_display[self.instruction_ptr - start] = f"[{tape_a_display[self.instruction_ptr - start]}]"
        print("".join(tape_a_display))
        
        # 显示纸带B的数据区域
        start_b = max(0, self.pointer - 15)
        end_b = min(len(self.tape_b), self.pointer + 16)
        print("纸带B (数据):")
        tape_b_display = [str(x) for x in self.tape_b[start_b:end_b]]
        if self.pointer >= start_b and self.pointer < end_b:
            tape_b_display[self.pointer - start_b] = f"[{tape_b_display[self.pointer - start_b]}]"
        print(" ".join(tape_b_display))
        
        # 显示当前指令的ASCII表示
        if self.instruction_ptr < len(self.code):
            print(f"当前指令: '{self.code[self.instruction_ptr]}' (ASCII: {ord(self.code[self.instruction_ptr])})")
        
        # 显示纸带B当前值的ASCII表示
        print(f"当前数据: {self.tape_b[self.pointer]} (ASCII: {chr(self.tape_b[self.pointer]) if 32 <= self.tape_b[self.pointer] <= 126 else '非可打印字符'})")

def print_help():
    """打印帮助信息"""
    print("""
Turing (T) 机器语言解释器 - 帮助文档

用法: python turing.py [选项] [文件]

选项:
  -h, --help     显示此帮助信息
  -v, --verbose  显示详细执行过程
  -s, --step     单步执行模式
  -f, --full     显示完整文档

如果没有提供文件参数，解释器将进入交互模式。

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

交互模式:
  在交互模式下，您可以:
  - 直接输入T代码执行
  - 输入"quit"或"exit"退出
  - 输入"clear"清空纸带
  - 输入"state"查看当前状态
""")

def print_full_docs():
    """打印完整文档"""
    print("""
Turing (T) 机器语言解释器 - 完整文档

1. 概述
T是一种基于双纸带模型的图灵完备编程语言，灵感来自Brainfuck但进行了扩展和重构。
它使用两个无限长的纸带：一个用于存储指令(纸带A)，一个用于存储数据(纸带B)。

2. 纸带模型
- 纸带A: 存储指令代码，初始加载用户提供的程序
- 纸带B: 存储数据值，初始全为0
- 指针: 指向当前操作的纸带B位置
- 指令指针: 指向当前执行的纸带A位置

3. 指令集详解
>   数据指针右移一位
<   数据指针左移一位
+   当前数据值加1(模256)
-   当前数据值减1(模256)
.   输出当前数据值对应的ASCII字符
,   从输入读取一个字符并存储其ASCII值
[   开始循环，如果当前数据值为0，跳转到匹配的]
]   结束循环，如果当前数据值不为0，跳转到匹配的[
!   交换纸带A和纸带B当前指针位置的值
@   将纸带A当前指令复制到纸带B
#   将纸带B当前值复制到纸带A
$   纸带B当前值加上纸带A当前指令值
%   纸带B当前值减去纸带A当前指令值
^   纸带B当前值乘以纸带A当前指令值
&   纸带B当前值除以纸带A当前指令值(非零)
*   纸带B当前值与纸带A当前指令值异或

4. 技术细节
- 所有数值操作都是模256的
- 纸带初始长度为500，会根据需要自动扩展
- 当指针超出当前纸带长度时，会自动环绕
- 负数指针取其绝对值

5. 示例程序
5.1 打印"Hello, World!"
++++++++[>++++++++>+++++++++++>+++++<<<-]>.>++.+++++++..+++.>-.
------------.<++++++++.--------.+++.------.--------.>+.

5.2 简单加法器 (输入两个数字，输出它们的和)
,>,<[->+<]>.

5.3 纸带交互示例 (使用纸带A和B的交互功能)
+++@#$  # 将3存入纸带B，然后进行各种操作

6. 实现说明
- 解释器用Python实现
- 支持交互模式和文件模式
- 提供调试和单步执行功能
""")

def interactive_mode(interpreter):
    """交互模式"""
    print("Turing (T) 机器语言解释器 - 交互模式")
    print("输入T代码执行，或输入help获取帮助")
    
    while True:
        try:
            user_input = input("T> ").strip()
            
            if user_input.lower() in ('quit', 'exit'):
                break
            elif user_input.lower() == 'help':
                print_help()
            elif user_input.lower() == 'clear':
                interpreter = TuringInterpreter()
                print("纸带已清空")
            elif user_input.lower() == 'state':
                interpreter.show_state()
            elif user_input:
                interpreter.execute(user_input)
        except KeyboardInterrupt:
            print("\n中断执行")
        except Exception as e:
            print(f"错误: {e}")

def main():
    interpreter = TuringInterpreter()
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-h', '--help'):
            print_help()
        elif sys.argv[1] in ('-f', '--full'):
            print_full_docs()
        elif sys.argv[1] in ('-v', '--verbose'):
            interpreter.verbose_mode = True
            if len(sys.argv) > 2:
                with open(sys.argv[2], 'r') as f:
                    code = f.read()
                interpreter.execute(code)
            else:
                interactive_mode(interpreter)
        elif sys.argv[1] in ('-s', '--step'):
            interpreter.step_mode = True
            if len(sys.argv) > 2:
                with open(sys.argv[2], 'r') as f:
                    code = f.read()
                interpreter.execute(code, single_step=True)
            else:
                interactive_mode(interpreter)
        else:
            with open(sys.argv[1], 'r') as f:
                code = f.read()
            interpreter.execute(code)
    else:
        interactive_mode(interpreter)

if __name__ == "__main__":
    main()

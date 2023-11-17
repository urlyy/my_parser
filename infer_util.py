import re
import tree_sitter
from my_parser import MyParser
from my_enum import NodeName


def check(node: tree_sitter.Node):
    return node.type == NodeName.ASSIGNMENT_EXPRESSION.value or node.type == NodeName.DECLARATION.value or node.type == NodeName.UPDATE_EXPRESSION.value
    
def transfer(old_code:str):
    class wrapper:
        def __init__(self,code:str):
            self.lines = code.split('\n')
        def collect_related_variables():
            variable = ("int","a")
            variables = set()
            variables.add(variable)
        def add_definition(self):
            self.lines.insert(0,"void begin(){}")
            self.lines.insert(0,"void terminate(){}")
            # TODO 修改参数
            self.lines.insert(0,"void transfer(){}")
            return self
        def add_begin_call(self):
            for line in self.lines:
                # 找到函数定义
                if re.match(r'\b\w+\s+\w+\s*\([^)]*\)\s*{?', line) is not None:
                    
            return self
        def add_terminate_call(self):
            
            return self
        def add_transfer_call(self):
            return self
    
    
    
if __name__ == "__main__":
    file_path = 'input/code2.c'
    new_file_path = 'output/code2.c'
    code = None
    with open(file_path, 'r') as file:
        code = file.read()
    new_code = transfer(code)
    print(new_code)

import tree_sitter
from my_parser import MyParser
from my_enum import NodeName
from functools import reduce
import tree_sitter_utils as utils


def check(node: tree_sitter.Node):
    return node.type == NodeName.ASSIGNMENT_EXPRESSION.value or node.type == NodeName.DECLARATION.value or node.type == NodeName.UPDATE_EXPRESSION.value
    
# def transfer_function(parser: MyParser,func_node:tree_sitter.Node):
#     def collect_related_variables(self):
#         variable = ("int","a")
#         variables = set()
#         variables.add(variable)
#         # self.transfer_arguments = 
#     def add_definition(self):
#         self.lines.insert(0,"void begin(){}")
#         self.lines.insert(0,"void terminate(){}")
#         # TODO 修改参数
#         self.lines.insert(0,"void transfer(){}")
#         return self
#     def add_begin_call(self):
#         begin_call = "\tbegin();"
#         defination_row = -1
#         for idx,line in enumerate(self.lines):
#             # 找到函数定义
#             if re.match(r'\b\w+\s+\w+\s*\([^)]*\)\s*{?', line) is not None:
#                 defination_row = idx
#                 break
#         if defination_row == -1:
#             print("代码中没有函数")
#         else: 
#             if self.lines[idx].strip().endswith('{'):
#                 self.lines.insert(idx+1, begin_call)
#             else:
#                 for i in range(idx+1,len(self.lines)):
#                     if self.lines[i].strip().startswith('{'):
#                         idddx = self.lines[i].find('{')
#                         self.lines[i] = self.lines[0:idddx+1]+begin_call+self.lines[idddx+1:]
#         return self
#     def add_terminate_call(self):
#         terminate_call = "\terminate();"
#         return self
#     def add_transfer_call(self):
#         return self
        
    
    
def collect():
    pass
def add_defination(parser: MyParser):
    new_code = "void begin(){}\nvoid terminate(){}\nvoid trans(){}\n" + parser.code()
    parser.update(parser.root,new_code)
    
    
# TODO 只支持处理单个函数
if __name__ == "__main__":
    file_path = 'input/code2.c'
    # new_file_path = 'output/code2.c'
    code = None
    with open(file_path, 'r') as file:
        code = file.read()
    parser = MyParser()
    parser.set_code(code)
    # 开始处理
    add_defination(parser)
    print(parser.code())
    
    # check_function = lambda n:n.type == NodeName.FUNCTION_DEFINITION
    # func = utils.find_node(check_function)
    # utils.traverse(parser.root,lambda n: print(n.type,utils.code(n)))
    # new_code = transfer(code)
    # print(new_code)

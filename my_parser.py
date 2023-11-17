import tree_sitter # https://tree-sitter.github.io/tree-sitter/playground
from typing import Tuple
from my_enum import NodeName
import tree_sitter_utils as utils

class MyParser:
  def __init__(self):
    # 配置
    tree_sitter.Language.build_library(
      # so文件保存位置
      'build/my-languages.so',
      # 下git clone的仓库
      [
        'languages/tree-sitter-cpp',
      ]
    )
    # 加载cpp代码解析器
    CPP_LANGUAGE = tree_sitter.Language('build/my-languages.so', 'cpp')
    parser = tree_sitter.Parser()
    parser.set_language(CPP_LANGUAGE)
    self._parser = parser
  
  
  # 设置要解析的代码
  def set_code(self,code:str):
    self._tree:tree_sitter.Tree = self._parser.parse(code.encode('utf-8'))
  
  
  # 返回语法树的root节点
  @property
  def root(self):
    return self._tree.root_node
  
  
  # 从结点获得的代码，默认为所有代码
  def code(self,node: tree_sitter.Node = None):
    if node:
      return utils.code(node)
    else:
      return utils.code(self.root)
  
  
  # 返回结点的位置范围
  def range(self,node: tree_sitter.Node = None)->Tuple:
    if node:
      return (node.start_byte,node.end_byte,node.start_point,node.end_point)
    else:
      return (self.root.start_byte,self.root.end_byte,self.root.start_point,self.root.end_point)
  
  # 被替换的结点和新的代码
  def update(self,replaced_node:tree_sitter.Node,input_code:str):
    range = self.range(replaced_node)
    new_code = self.code().replace(self.code(replaced_node),input_code)
    lines = new_code.split('\n')
    # 修改语法树
    # 代码在字节时的偏移和在ide展示时的行列坐标
    # bytes: (start_byte,old_end_byte,new_end_byte)
    # points: ((start_row,start_column),(old_end_row,old_end_column),(new_end_row,new_end_column))
    bytes = (range[0],range[1],range[0]+len(new_code)-1)
    points = (range[2],range[3],(len(lines),len(lines[-1])))
    self._tree.edit(
      bytes[0],
      bytes[1],
      bytes[2],
      points[0],
      points[1],
      points[2],
    ) 
    self._tree = self._parser.parse(new_code.encode(),self._tree)
  
  
  # 找循环
  def find_loop_node(self):
    check = lambda node: node.type == Statement.WHILE.value or node.type == Statement.FOR.value
    return utils.find_node(self.root , check)
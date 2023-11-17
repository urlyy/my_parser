from loop_abstraction import LoopAbstractor
from my_parser import MyParser

if __name__ == "__main__":
  # 读取代码
  file_path = 'input/code2.c'
  new_file_path = 'output/code2.c'
  code = None
  with open(file_path, 'r') as file:
      code = file.read()
  # 新建解析器
  parser = MyParser()
  parser.set_code(code)
  # 进行循环抽象
  loop_abstractor = LoopAbstractor()
  while True:
    loop_node = parser.find_loop_node()
    if loop_node is None:
      break
    if_code = loop_abstractor.havoc_loop2if(loop_node)
    # print(if_code)
    parser.update(loop_node,if_code)
    with open(new_file_path , 'w') as file:
      file.write(parser.code())
    break
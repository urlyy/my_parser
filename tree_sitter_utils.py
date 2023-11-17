from typing import Any, Callable, List
import tree_sitter

def code(node: tree_sitter.Node):
    return node.text.decode("utf-8")
        
# 作为非递归遍历语法树方式的参考，dfs前序遍历
def traverse(root: tree_sitter.Node, operate: Callable[[tree_sitter.Node], None]):
    stack = [root]
    while stack:
        current_node = stack.pop()
        operate(current_node)
        # 将子节点按逆序入栈，保持栈顶的节点是先进后出
        stack.extend(reversed(current_node.children))

def find_node(root: tree_sitter.Node, check: Callable[[tree_sitter.Node], bool]):
    stack = [root]
    while stack:
        current_node = stack.pop()
        # 判断是否是符合条件的节点
        if check(current_node):
            return current_node
        # 将子节点按逆序入栈，保持栈顶的节点是先进后出
        stack.extend(reversed(current_node.children))
    # 如果遍历完整棵树都没有找到符合条件的节点，返回 None
    return None


def find_nodes(root: tree_sitter.Node, check: Callable[[tree_sitter.Node], bool],exclude: Callable[[tree_sitter.Node], bool] = None)->List[tree_sitter.Node]:
    stack = [root]
    res = []
    while stack:
        current_node = stack.pop()
        if exclude and exclude(current_node):
            continue
        if check(current_node):
            res.append(current_node)
        # 将子节点按逆序入栈，保持栈顶的节点是先进后出
        stack.extend(reversed(current_node.children))
    return res


def reduce_nodes(root: tree_sitter.Node, reduce: Callable[[Any,tree_sitter.Node],Any],init_val):
    stack = [root]
    res = init_val
    while stack:
        current_node = stack.pop()
        res = reduce(res,current_node)
        stack.extend(reversed(current_node.children))
    # 如果遍历完整棵树都没有找到符合条件的节点，返回 None
    return res


def find_nodes_generator(root: tree_sitter.Node, check: Callable[[tree_sitter.Node], bool],exclude: Callable[[tree_sitter.Node], bool] = None)->List[tree_sitter.Node]:
    stack = [root]
    while stack:
        current_node = stack.pop()
        if exclude and exclude(current_node):
            continue
        if check(current_node):
            yield current_node
        # 将子节点按逆序入栈，保持栈顶的节点是先进后出
        stack.extend(reversed(current_node.children))

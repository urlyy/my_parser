import tree_sitter
from my_enum import NodeName
import tree_sitter_utils as utils



class LoopAbstractor:
    def new_identifier_name(self,old_name,loop_idx):
        return f"LOOP_{loop_idx}_{old_name}"
    
    
    # 把循环改为if
    def havoc_for2if(self,node: tree_sitter.Node,loop_idx=0):
        # TODO!!!注意condition和body里面都可能有全局变量
        # 对应 "int i=0,j=0"
        init = node.child_by_field_name('initializer')
        # 对应 "i<10&&j<10&&j<20"
        # condition是一种嵌套的做法,即"((i<10 && j<10) && j<20)"
        # 每层将最左两个化为一起，分别的name为left和right，即左递归
        condition = node.child_by_field_name('condition')
        # 对应 "i<10&&j<10&&j<20"
        update = node.child_by_field_name('update')
        # 对应 "i++"后的")"后的"{int lyy;res += a + b;res += a-b;res ++;}"
        # 不能直接用key取到,无语
        body = node.named_children[-1]
        
        # 对应 "int"
        type = init.child_by_field_name('type')
        # 对应 "i=0,j=0"，是列表
        declarators = init.children_by_field_name('declarator')
        
        # 收集循环中初始化的临时变量
        tmp_declare_variables = set()
        for d in declarators:
            variable_name = utils.code(d.child_by_field_name("declarator"))
            tmp_declare_variables.add(variable_name)
        # print("循环临时定义的变量:",tmp_declare_variables)
        
        # 收集所有被改动的变量
        modified_variables = set()
        ## 循环体的每个语句
        for exp in body.named_children:
            if exp.type == 'declaration':
                pass
            elif exp.type == 'expression_statement':
                for eexp in exp.named_children:
                    if eexp.type == 'assignment_expression':
                        variable_name = eexp.child_by_field_name('left')
                        modified_variables.add(utils.code(variable_name))
                    elif eexp.type == 'update_expression':
                        variable_name = eexp.child_by_field_name('argument')
                        modified_variables.add(utils.code(variable_name))
        ## update的语句(注意是右递归)
        
        # 只有 "i++"，没有"i++,j++"的情况
        if update.child_by_field_name('left') is None:
            variable_name = utils.code(update.child_by_field_name('argument'))
            modified_variables.add(variable_name)
        else:
            tmp_root = update
            while True:
                left = tmp_root.child_by_field_name('left')
                right = tmp_root.child_by_field_name('right')
                variable_name = utils.code(left.child_by_field_name('argument'))
                modified_variables.add(variable_name)
                ### 其实就是最后一次循环了
                if right.child_by_field_name('right') is None:
                    variable_name = utils.code(right.child_by_field_name('argument'))
                    modified_variables.add(variable_name)
                    break
                tmp_root = tmp_root.child_by_field_name('right')
            # print("循环内被修改的变量:",modified_variables)
        
        
        # 循环边界条件的相关变量
        condition_variables = set()
        tmp_root = condition
        while True:
            left = tmp_root.child_by_field_name('left')
            right = tmp_root.child_by_field_name('right')
            # 其实就是最后一次循环了
            if left.child_by_field_name('left') is None:
                variable_name = utils.code(left)
                condition_variables.add(variable_name)
                break
            else:
                variable_name = utils.code(right.child_by_field_name('left'))
                condition_variables.add(variable_name)
            tmp_root = tmp_root.child_by_field_name('left')
        # print("循环边界条件的相关变量:",condition_variables)
        
        # 开始组装if
        new_if = ""
        
        def reduce_operator(res,node: tree_sitter.Node):
            type = node.type
            code = utils.code(node)
            # 开始处理
            if type == NodeName.DECLARATION.value or type == NodeName.INIT_DECLARATOR.value:
                pass
            # 生成新的定义，防止重复定义
            elif type == NodeName.IDENTIFIER.value:
                name = code
                if name in tmp_declare_variables:
                    name = self.new_identifier_name(name,loop_idx)
                res += name
            else:
                res += code + " "
            return res
        generated_declaration = utils.reduce_nodes(init,reduce_operator,"")
        new_if += generated_declaration +'\n'
        # print(generated_declaration)
        
        
        def reduce_operator(res,node: tree_sitter.Node):
            type = node.type
            code = utils.code(node)
            # # 开始处理
            if type == NodeName.BINARY_EXPRESSION.value:
                pass
            # # 配合之前新的定义
            elif type == NodeName.IDENTIFIER.value:
                name = code
                if code in tmp_declare_variables:
                    name = self.new_identifier_name(code,loop_idx)
                res += name
            else:
                res += code
            return res
        generated_condition = utils.reduce_nodes(condition,reduce_operator,"")
        new_if +=  "if(" + generated_condition + ")\n"
        
        
        generated_body = ""
        for variable in modified_variables:
            name = variable
            # TODO 判断以下是否需要new_identifier
            if name in tmp_declare_variables:
                name = self.new_identifier_name(name,loop_idx)
            exp = f"\t{name} = nondet_int();\n"
            generated_body += exp
        generated_body = "{\n" + generated_body + "}"
        # print(generated_body)
        new_if += generated_body
        
        # 再加个abort
        new_if += "\nif(" + generated_condition + ")abort();"
        # TODO for的三个部分的判空
        old_for = "/*" + utils.code(node) + "*/"
        all_new = "//START HAVOC\n" + old_for +"\n"+ new_if+"\n//END HAVOC"
        return all_new  
        
    def havoc_while2if(self,node: tree_sitter.Node,loop_idx=0):
        condition = node.child_by_field_name('condition')
        body = node.child_by_field_name('body')
        
        # 循环边界的变量
        # condition_variables = set()
        # check_condition_identifier = lambda n: n.type == 'identifier'
        # nodes = utils.find_nodes(condition,check_condition_identifier)
        # for i in list(map(lambda n:utils.code(n),nodes)):
        #     condition_variables.add(i)
        
        # 循环体里的变量
        modified_variables = set()
        check_body_identifier = lambda n: n.type == 'identifier'
        check_body_declaration = lambda n: n.type == 'declaration'
        nodes = utils.find_nodes(body,check_body_identifier)
        nodes_declaration = utils.find_nodes(body,check_body_declaration)
        # 取出body里的所有变量
        for i in list(map(lambda n:utils.code(n),nodes)):
            modified_variables.add(i)
        # 取出body里的定义的变量
        tmp_set = set()
        for dec in nodes_declaration:
            for d in dec.children_by_field_name('declarator'):
                identifier = utils.code(d.child_by_field_name('declarator'))
                tmp_set.add(identifier)
        # 所有变量 - 局部定义的变量 = 抽象输出的变量
        modified_variables -= tmp_set
        # 拼装if代码 
        exp = utils.find_node(condition,lambda n:n.type=='binary_expression')
        if_condition = "if(" + utils.code(exp)  + ")\n" 
        tmp_body = ""
        for variable in modified_variables:
            # name = self.new_identifier_name(variable,loop_idx)
            exp = f"\t{variable} = nondet_int();\n"
            tmp_body += exp
        if_body = "{\n" + tmp_body+ "}"
        
        new_if = if_condition + if_body
        
        new_if += "\n"+if_condition+ "abort();"
        
        
        old_for = "/*" + utils.code(node) + "*/"
        all_new = "//START HAVOC\n" + old_for +"\n"+ new_if+"\n//END HAVOC"
        # print(all_new)
        return all_new
    
    # 进行havoc循环抽象
    def havoc_loop2if(self,loop_node: tree_sitter.Node)->str:
        new_if_str = None
        if loop_node.type == NodeName.FOR.value:
            new_if_str = self.havoc_for2if(loop_node)
        else:
            new_if_str = self.havoc_while2if(loop_node)
        return new_if_str
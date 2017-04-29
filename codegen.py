from symboltable import ScopeStack
import constants

class CodeGenerator:
    def __init__(self):
        self._symbol_table = None
        self._register_counter = 0
        self._string_counter = 0
        self._label_counter = 0
        self._scope_stack = ScopeStack()
        self._output_file = "ir.ll"
        self._runtime_system_file = "runtime_system"
        self._output_file_ptr = None

    def generate(self, node, symbol_table):
        self._scope_stack.push("main")
        self._output_file_ptr = open(self._output_file,"w")
        self._symbol_table = symbol_table
        self._register_counter = 0
        self._string_counter = 0
        self._label_counter = 0
        self._add_runtime_system()
        self._generate_constant_string_declarations(node)
        self._generate_global_variable_declarations(node)
        self._generate_procedure_declarations(node)
        self._generate_main_header()
        self._generate_init_heap()
        self._generate(node)
        self._generate_cleanup_heap()
        self._generate_main_footer()
        self._output_file_ptr.close()

    def _next_register(self):
        name = "%r" + str(self._register_counter)
        self._register_counter += 1
        return name

    def _next_label(self):
        name = "label_" + str(self._label_counter)
        self._label_counter += 1
        return name

    def _next_string_name(self):
        name = "@string_" + str(self._string_counter)
        self._string_counter += 1
        return name

    def _add_runtime_system(self):
        with open(self._runtime_system_file,"r") as f:
            self._put(f.read())
            self._put("; runtime system")
            self._put(";" + 100*"-")
            self._put("; program")
            self._put("\n")

    def _generate_main_header(self):
        self._put("define i32 @main(){")

    def _generate_main_footer(self):
        self._put("ret i32 0")
        self._put("}")

    def _generate_global_variable_declarations(self,node):
        if node.name_matches('declaration'):
            child = node.children[0]
            if node.token and node.token.value == "global":
                global_flag = True
                if child.name_matches('variable_declaration'):
                    self._handle_variable_declaration(child,global_flag)
        else:
            for child in node.children:
                self._generate_global_variable_declarations(child)

    def _generate_constant_string_declarations(self, node):
        if node.name_matches("string"):
            string = node.token.value
            name = self._next_string_name()
            self._generate_constant_string_declaration(name,string)
            node.ir_string_reference = name
        else:
            for child in node.children:
                self._generate_constant_string_declarations(child)

    def _generate_procedure_declarations(self,node):
        if node.name_matches('declaration'):
            child = node.children[0]
            if child.name_matches('procedure_declaration'):
                self._scope_stack.push_node(child)
                self._handle_procedure_declaration(child)
                self._scope_stack.pop_node(child)
        else:
            for child in node.children:
                self._generate_procedure_declarations(child)

    def _generate(self,node):
        self._scope_stack.push_node(node)
        if node.name_matches("assignment_statement"):
            self._handle_assignment(node)
        elif node.name_matches("loop_statement"):
            self._handle_loop(node)
        elif node.name_matches("if_statement"):
            self._handle_if_statement(node)
        elif node.name_matches("variable_declaration"):
            self._handle_variable_declaration(node,False)
        elif node.name_matches("procedure_call"):
            self._handle_procedure_call(node)
        elif node.name_matches("return_statement"):
            self._generate_return();
        elif node.name_matches("procedure_declaration"):
            pass
        else:
            for child in node.children:
                self._generate(child)
        self._scope_stack.pop_node(node)

    def _put(self, statement):
        self._output_file_ptr.write(statement + "\n")

    def _generate_constant_string_declaration(self, name, string):
        self._put("%s = private unnamed_addr constant [%i x i8] c\"%s\\00\""%(name,len(string)+1,string))

    def _generate_global_variable_declaration(self, reg_name, dtype):
        self._put("%s = global %s zeroinitializer"%(reg_name, dtype))

    def _generate_global_array_declaration(self, reg_name, dtype, size):
        self._put("%s = global [%s x %s] zeroinitializer"%(reg_name,str(size),dtype))

    def _generate_variable_alloc(self, reg_name, dtype):
        self._put("%s = alloca %s"%(reg_name,dtype))

    def _generate_array_alloc(self, reg_name, dtype, size):
        self._put("%s = alloca [%s x %s]"%(reg_name,str(size),dtype))

    def _generate_store(self, src_name, dst_name, src_dtype, dst_dtype):
        self._put("store %s %s, %s %s"%(src_dtype, src_name, dst_dtype, dst_name))

    def _generate_array_store(self,name,size,dtype,index,value):
        ptr = self._generate_getelementptr(name,size,dtype,index)
        self._generate_store(value,ptr["value"],dtype,ptr["dtype"])

    def _generate_array_store_from_ptr(self,name,dtype,index,value):
        ptr = self._generate_getelementptr_from_ptr(name,dtype,index)
        self._generate_store(value,ptr["value"],dtype,ptr["dtype"])

    def _generate_load(self, src_name, dst_name, src_dtype):
        self._put("%s = load %s %s"%(dst_name, src_dtype, src_name))

    def _generate_array_load(self,name,size,dtype,index):
        ptr = self._generate_getelementptr(name,size,dtype,index)
        result_reg = self._next_register()
        self._generate_load(ptr["value"],result_reg,dtype+"*")
        return {"value":result_reg,"dtype":dtype}

    def _generate_array_load_from_arg(self,name,dtype,index):
        ptr = self._generate_getelementptr_from_ptr(name,dtype,index)
        result_reg = self._next_register()
        self._generate_load(ptr["value"],result_reg,dtype+"*")
        return {"value":result_reg,"dtype":dtype}

    def _generate_getelementptr(self, name, size, dtype, index):
        result_reg = self._next_register()
        self._put("%s = getelementptr inbounds [%s x %s]* %s, i32 0, i32 %s"%(result_reg,str(size),dtype,name,str(index)))
        return {"value":result_reg,"dtype":dtype+"*"}

    def _generate_getelementptr_from_ptr(self, name, dtype, index):
        result_reg = self._next_register()
        self._put("%s = getelementptr inbounds %s* %s, i32 %s"%(result_reg,dtype,name,str(index)))
        return {"value":result_reg,"dtype":dtype+"*"}

    def _generate_i32_to_fp_conversion(self,source_name):
        dest_name = self._next_register()
        self._put("%s = sitofp i32 %s to double"%(dest_name,source_name))
        return {"value":dest_name, "dtype":"double"}

    def _generate_fp_to_i32_conversion(self,source_name):
        dest_name = self._next_register()
        self._put("%s = fptosi double %s to i32"%(dest_name,source_name))
        return {"value":dest_name, "dtype":"i32"}

    def _generate_i1_to_i32_conversion(self,source_name):
        dest_name = self._next_register()
        self._put("%s = sext i1 %s to i32"%(dest_name,source_name))
        return {"value":dest_name, "dtype":"i32"}

    def _generate_i32_to_i1_conversion(self,source_name):
        dest_name = self._next_register()
        self._put("%s = icmp eq i32 %s, 0"%(dest_name,source_name))
        return {"value":dest_name, "dtype":"i1"}

    def _generate_procedure_declaration(self,name,args,body):
        header = "define void %s"%name
        arg_strings = map(lambda a: "%s %s"%(a["dtype"],a["name"]),args)
        arguments = "(" + ", ".join(arg_strings) + ")"
        self._put(header + arguments + "{")
        for arg in args:
            if arg["by_val"]:
                self._generate_variable_alloc(arg["real_name"],arg["dtype"])
                self._generate_store(arg["name"],arg["real_name"],arg["dtype"],arg["dtype"]+"*")
            else:
                arg["reg_name"] = self._next_register()
                self._generate_variable_alloc(arg["reg_name"],arg["dtype"])
                self._generate_store(arg["name"],arg["reg_name"],arg["dtype"],arg["dtype"]+"*")
        self._generate(body)
        self._put("ret void")
        self._put("}")

    def _generate_conditional_branch(self,condition):
        if_equal = self._next_label();
        if_unequal = self._next_label();
        self._put("br i1 %s, label %%%s, label %%%s"%(condition,if_equal,if_unequal))
        return [if_equal,if_unequal]

    def _generate_unconditional_branch(self, label):
        self._put("br label %%%s"%label)

    def _generate_operation(self,op1,op2,operator):
        result = self._next_register()
        self._put("%s = %s %s %s, %s"%(result,operator,op1["dtype"],op1["value"],op2["value"]))
        return result

    def _generate_procedure_call(self,proc_name, args):
        call = "call void %s("%proc_name
        call += ", ".join(map(lambda arg: arg["dtype"] + " " + arg["value"], args))
        call += ")"
        self._put(call)

    def _generate_return(self):
        self._put("ret void");

    def _generate_label(self, label):
        self._put(label + ":")

    def _generate_init_heap(self):
        self._put("call void @init_heap()")

    def _generate_cleanup_heap(self):
        self._put("call void @cleanup_heap()")

    def _global_name(self,identifier):
        return "@" + identifier

    def _register_name(self,identifier):
        return "%" + identifier

    def _proc_name(self,identifier):
        return "@" + identifier

    def _ir_datatype(self, datatype):
        if datatype == "float":
            return "double"
        elif datatype == "integer":
            return "i32"
        elif datatype == "char":
            return "i8"
        elif datatype == "bool":
            return "i1"
        else: # string
            return "i8*"

    def _i32_to_i1(self,operand):
        if operand["value"] != "0":
             operand["value"] = "1"
        operand["dtype"] = "i1"
        return operand

    def _i32_to_double(self,operand):
        operand["value"] = operand["value"] + ".0e+00"
        operand["dtype"] = "double"
        return operand

    def _convert_dtype_for_assignment(self, source_reference, source_type, dest_type):
        if source_type == dest_type:
            return {"value":source_reference, "dtype":source_type}
        elif source_type == "double" and dest_type == "i32":
            return self._generate_fp_to_i32_conversion(source_reference)
        elif source_type == "i32" and dest_type == "double":
            return self._generate_i32_to_fp_conversion(source_reference)
        elif source_type == "i1" and dest_type == "i32":
            return self._generate_i1_to_i32_conversion(source_reference)
        elif source_type == "i32" and dest_type == "i1":
            return self._generate_i32_to_i1_conversion(source_reference)
        elif source_type == "i8**" and dest_type == "i8*":
            return {"value":source_reference, "dtype":source_type}
        else:
            raise Exception("problem!")

    def _to_ir_literal(self, node):
        token_value = node.token.value
        token_type = node.token.type
        if token_type == "NUMBER":
            if "." in token_value:
                return {
                        "value": token_value + "e+00",
                        "dtype": "double"
                        }
            else:
                return {
                        "value": token_value,
                        "dtype": "i32"
                        }
        elif token_type == "CHARACTER":
            if token_value == "":
                token_value = "\0"
            return {
                    "value": str(ord(token_value)),
                    "dtype": "i8"
                    }
        elif token_type == "BOOLEAN" or token_value in ["true","false"]:
            if token_value == "true":
                value = "1"
            else:
                value = "0"
            return {
                    "value": value,
                    "dtype": "i1"
                    }
        elif token_type == "STRING":
            return {
                    "value":node.ir_string_reference,
                    "dtype":"i8*",
                    "size":len(token_value)+1
                    }
        else:
            raise Exception("there's a problem.")

    def _get_expected_arguments(self, identifier):
        arg_symbols = self._symbol_table.get_expected_arguments(identifier)
        args = []
        for symbol in arg_symbols:
            data_type = self._ir_datatype(symbol["data_type"])
            #if (symbol["direction"] != "in" and symbol["data_type"] != "string") or symbol["type"] == "array":
            if symbol["direction"] != "in" or symbol["type"] == "array":
                data_type = data_type + "*"
            name = self._register_name(symbol["identifier"])
            if symbol["direction"] == "in" and symbol["type"] == "variable":
                by_val = True
                real_name = name
                name += "_"
            else:
                by_val = False
                real_name = None
            args.append({"name":name,"real_name":real_name,"dtype":data_type,"by_val":by_val})
        return args

    def _handle_type_conversions(self,op1,op2,operator):
        if operator in constants.EXPRESSION_OPS: # ['&','|']
            if op1["dtype"] != "i1":
                op1 = self._generate_i32_to_i1_conversion(op1["value"])
            if op2["dtype"] != "i1":
                op2 = self._generate_i32_to_i1_conversion(op2["value"])
        else:
            if op1["dtype"] == "double" and op2["dtype"] == "i32":
                op2 = self._generate_i32_to_fp_conversion(op2["value"])
            elif op2["dtype"] == "double" and op1["dtype"] == "i32":
                op1 = self._generate_i32_to_fp_conversion(op1["value"])
            else:
                pass
        return [op1,op2]

    def _handle_procedure_declaration(self, node):
        proc_header = node.children[0]
        proc_body = node.children[1]
        identifier = proc_header.children[0].token.value
        args = self._get_expected_arguments(identifier)
        ir_name = self._proc_name(identifier)
        self._generate_procedure_declaration(ir_name, args, proc_body)

    def _handle_variable_declaration(self, node, is_global):
        source_name = node.children[1].token.value
        source_dtype = node.children[0].token.value
        dtype = self._ir_datatype(source_dtype)
        is_array = len(node.children) == 3
        if is_array and is_global:
            array_size = node.children[2].token.value
            name = self._global_name(source_name)
            self._generate_global_array_declaration(name,dtype,array_size)
        elif is_array and not is_global:
            array_size = node.children[2].token.value
            name = self._register_name(source_name)
            self._generate_array_alloc(name,dtype,array_size)
        elif not is_array and is_global:
            name = self._global_name(source_name)
            self._generate_global_variable_declaration(name,dtype)
        else: # not array and not global
            name = self._register_name(source_name)
            self._generate_variable_alloc(name,dtype)

    def _handle_if_statement(self, node):
        expression = node.children[0]
        condition = self._handle_expression(expression)
        self._put(";--- if statement ---")
        [if_true,if_false] = self._generate_conditional_branch(condition["value"])
        continu = self._next_label()
        self._generate_label(if_true)
        self._generate(node.children[1])
        self._generate_unconditional_branch(continu)
        self._generate_label(if_false)
        if len(node.children) == 3:
            self._generate(node.children[2])
        self._generate_unconditional_branch(continu)
        self._generate_label(continu)

    def _obtain_identifier(self, node):
        if not node.name_matches("name"):
            return self._obtain_identifier(node.children[0])
        else:
            scope = self._scope_stack.as_string()
            name = node.children[0].token.value
            symbol = self._symbol_table.fetch(name,scope)
            identifier = {}
            identifier["dtype"] = self._ir_datatype(symbol["data_type"])
            if symbol["type"] == "array":
                identifier["size"] = symbol["array_length"]
            else:
                identifier["dtype"] += "*"
            if symbol["global"]:
                identifier["value"] = self._global_name(name)
            else:
                identifier["value"] = self._register_name(name)
            return identifier

    def _obtain_pointer(self, node):
        if not node.name_matches("name"):
            return self._obtain_pointer(node.children[0])
        else:
            identifier = node.children[0].token.value
            scope = self._scope_stack.as_string()
            symbol = self._symbol_table.fetch(identifier, scope)
            dtype = self._ir_datatype(symbol["data_type"])
            if symbol["global"]:
                ir_name = self._global_name(identifier)
            else:
                ir_name = self._register_name(identifier)
            if symbol["type"] == "array":
                size = symbol["array_length"]
                if len(node.children) == 2:
                    index = self._handle_expression(node.children[1])
                    return self._generate_getelementptr(ir_name,size,dtype,index["value"])
                else:
                    return self._generate_getelementptr(ir_name,size,dtype,"0")
            else:
                return {"value":ir_name, "dtype":dtype+"*"}

    def _determine_argument(self, node, expected_arg):
        scope = self._scope_stack.as_string()
        if expected_arg["direction"] == "in":
            if expected_arg["type"] == "array":
                i = self._obtain_identifier(node)
                return self._generate_getelementptr(i["value"],i["size"],i["dtype"],"0")
            else: # one-dimensional (variable or const)
                if expected_arg["data_type"] == "string":
                    return self._handle_expression(node)
                else: # non-string
                    return self._handle_expression(node)
        else: # out or inout
            if expected_arg["type"] == "array":
                i = self._obtain_identifier(node)
                return self._generate_getelementptr(i["value"],i["size"],i["dtype"],"0")
            else: # one-dimensional (variable or const)
                if expected_arg["data_type"] == "string":
                    return self._obtain_identifier(node)
                else: # non-string
                    return self._obtain_pointer(node)


    # call void @_Z3fooiPfPKc(i32 %2, float* %3, i8* %4)
    # void foo(int i, float f[10], const char* s)
    def _handle_procedure_call(self, node):
        identifier = node.children[0]
        args = []
        scope = self._scope_stack.as_string()
        expected_args = self._symbol_table.get_expected_arguments(identifier.token.value)
        arg_index = 0
        # execute any loads or expressions necessary to produce the arguments
        if len(node.children) == 2:
            arg_list = node.children[1]
            while True:
                arg_node = arg_list.children[0]
                expected_arg = expected_args[arg_index]
                arg_index += 1
                arg = self._determine_argument(arg_node,expected_arg)
                args.append(arg)
                if len(arg_list.children) == 2:
                    arg_list = arg_list.children[1]
                else:
                    break
        # print the code
        proc_name = self._proc_name(identifier.token.value)
        self._generate_procedure_call(proc_name,args)

    def _handle_loop(self, node):
        assignment = node.children[0]
        expression = node.children[1]
        expression_label = self._next_label()
        self._put(";--- loop statement ---")
        self._generate_unconditional_branch(expression_label)
        self._generate_label(expression_label)
        result = self._handle_expression(expression)
        [if_true,if_false] = self._generate_conditional_branch(result["value"])
        self._generate_label(if_true)
        if len(node.children) > 2:
            for child in node.children[2:]:
                self._generate(child)
        self._handle_assignment(assignment)
        self._generate_unconditional_branch(expression_label)
        self._generate_label(if_false)

    def _handle_assignment(self, node):
        destination = node.children[0]
        expression = node.children[1]
        dest_name = destination.children[0].token.value
        current_scope = self._scope_stack.as_string()
        dest_symbol = self._symbol_table.fetch(dest_name,current_scope)
        dtype = self._ir_datatype(dest_symbol["data_type"])
        source = self._handle_expression(expression)
        if source["dtype"] == "i8*":
            pass
        if dest_symbol["type"] == "array":
            index = self._handle_expression(destination.children[1])
            size = dest_symbol["array_length"]
            if dest_symbol["global"]:
                array_reference = self._global_name(dest_name)
            else:
                array_reference = self._register_name(dest_name)
            source = self._convert_dtype_for_assignment(source["value"],source["dtype"],dtype)
            if dest_symbol["is_argument"]:
                self._generate_array_store_from_ptr(array_reference,dtype,index["value"],source["value"])
            else:
                self._generate_array_store(array_reference,size,dtype,index["value"],source["value"])
        else:
            dest_register = self._register_name(dest_name)
            source = self._convert_dtype_for_assignment(source["value"],source["dtype"],dtype)
            self._generate_store(source["value"], dest_register, source["dtype"], dtype+"*")

    def _handle_operation(self,op1,op2,operator):
        dtype = op1["dtype"]
        if dtype == "double":
            ir_operator = constants.FP_IR_OPERATIONS[operator]
            return_type = constants.FP_IR_RETURN_TYPE[operator]
        elif dtype == "i32":
            ir_operator = constants.INT_IR_OPERATIONS[operator]
            return_type = constants.INT_IR_RETURN_TYPE[operator]
        elif dtype == "i1":
            ir_operator = constants.BOOL_IR_OPERATIONS[operator]
            return_type = constants.BOOL_IR_RETURN_TYPE[operator]
        else:
            raise Exception("problem")
        result = self._generate_operation(op1,op2,ir_operator)
        return {"value":result,"dtype":return_type}

    def _handle_expression(self, node):
        if node.is_binary_operation():
            op1 = self._handle_expression(node.children[0])
            op2 = self._handle_expression(node.children[1])
            operator = node.token.value
            [op1,op2] = self._handle_type_conversions(op1,op2,operator)
            return self._handle_operation(op1,op2,operator)
        elif node.name_matches('name'):
            identifier = node.children[0]
            symbol = self._symbol_table.fetch(identifier.token.value,self._scope_stack.as_string())
            name = self._register_name(symbol["identifier"])
            dtype = self._ir_datatype(symbol["data_type"])
            size = symbol["array_length"]
            if symbol["type"] == "array":
                if len(node.children) == 2:
                    index = self._handle_expression(node.children[1])
                    if symbol["is_argument"]:
                        return self._generate_array_load_from_arg(name,dtype,index["value"]) #name,size,dtype,index
                    else:
                        return self._generate_array_load(name,size,dtype,index["value"]) #name,size,dtype,index
                else:
                    return self._generate_getelementptr(name,size,dtype,"0") #name,size,dtype,index
            else:
                dst_name = self._next_register()
                self._generate_load(name,dst_name,dtype+"*") #src_name, dst_name, src_dtype
                return {"value": dst_name, "dtype": dtype}
        elif node.is_literal():
            if node.token.type_matches("STRING"):
                name = node.ir_string_reference
                size = len(node.token.value)+1
                dtype = "i8"
                return self._generate_getelementptr(name,size,dtype,"0")
            else:
                return self._to_ir_literal(node)
        else:
            return self._handle_expression(node.children[0])

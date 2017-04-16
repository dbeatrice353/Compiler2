from symboltable import ScopeStack
import constants

class CodeGenerator:
    def __init__(self):
        self._symbol_table = None
        self._register_counter = 0
        self._scope_stack = ScopeStack()
        self._output_file = "ir.ll"
        self._output_file_ptr = None

    def generate(self, node, symbol_table):
        self._output_file_ptr = open(self._output_file,"w")
        self._symbol_table = symbol_table
        self._register_counter = 0
        self._generate_global_variable_declarations(node)
        self._generate_procedure_declarations(node)
        self._generate_main_header()
        self._generate(node)
        self._generate_main_footer()
        self._output_file_ptr.close()

    def _next_register(self):
        name = "%r" + str(self._register_counter)
        self._register_counter += 1
        return name

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

    def _generate_procedure_declarations(self,node):
        if node.name_matches('declaration'):
            child = node.children[0]
            if child.name_matches('procedure_declaration'):
                self._handle_procedure_declaration(child)
        else:
            for child in node.children:
                self._generate_procedure_declarations(child)

    def _generate(self,node):
        if node.name_matches("expression"):
            self._handle_expression(node)
        elif node.name_matches("variable_declaration"):
            self._handle_variable_declaration(node,False)
        elif node.name_matches("procedure_declaration"):
            return
        else:
            for child in node.children:
                self._generate(child)

    def _put(self, statement):
        self._output_file_ptr.write(statement + "\n")

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

    def _generate_array_store(name,size,dtype,index,value):
        ptr = self._generate_getelementptr(name,size,dtype,index)
        self._generate_store(name,ptr,dtype,dtype+"*")

    def _generate_load(self, src_name, dst_name, src_dtype):
        self._put("%s = load %s %s"%(dst_name, src_type, src_name))

    def _generate_array_load(name,size,dtype,index):
        ptr = self._generate_getelementptr(name,size,dtype,index)
        self._generate_load(name,ptr,dtype)

    def _generate_getelementptr(self, name, size, dtype, index):
        result_reg = self._next_register()
        self._put("%s = getelementptr inbounds [%s x %s]* %s, i32 0, i64 %s"%(result_reg,str(size),dtype,name,str(index)))
        return result_reg

    def _generate_procedure_declaration(self,name,args):
        header = "define void %s"%name
        arg_strings = map(lambda a: "%s %s"%(a["dtype"],a["name"]),args)
        arguments = "(" + ", ".join(arg_strings) + ")"
        self._put(header + arguments + "{")
        for arg in args:
            arg["reg_name"] = self._next_register()
            self._generate_variable_alloc(arg["reg_name"],arg["dtype"])
        for arg in args:
            self._generate_store(arg["name"],arg["reg_name"],arg["dtype"],arg["dtype"]+"*")
        self._put("ret void")
        self._put("}")

    def _generate_operation(self,op1,op2,operator):
        result = self._next_register()
        self._put("%s = %s %s %s, %s"%(result,operator,op1["dtype"],op1["value"],op2["value"]))
        return result

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
            raise Exception("STRING")
        else:
            print "DEBUG: " + token_type + " " + token_value
            raise Exception("there's a problem.")

    def _get_expected_arguments(self, identifier):
        arg_symbols = self._symbol_table.get_expected_arguments(identifier)
        args = []
        for symbol in arg_symbols:
            data_type = self._ir_datatype(symbol["data_type"])
            if (symbol["direction"] != "in" and symbol["data_type"] != "string") or symbol["type"] == "array":
                data_type = data_type + "*"
            name = self._register_name(symbol["identifier"])
            args.append({"name":name,"dtype":data_type})
        return args

    def _handle_type_conversions(self,op1,op2,operator):
        if operator in constants.EXPRESSION_OPS: # ['&','|']
            if op1["dtype"] != "i1":
                op1 = self._i32_to_i1(op1)
            if op2["dtype"] != "i1":
                op2 = self._i32_to_i1(op2)
        else:
            if op1["dtype"] == "double" and op2["dtype"] == "i32":
                op2 = self._i32_to_double(op2)
            elif op2["dtype"] == "double" and op1["dtype"] == "i32":
                op1 = self._i32_to_double(op1)
            else:
                pass
        return [op1,op2]

    def _handle_procedure_declaration(self, node):
        proc_header = node.children[0]
        identifier = self._proc_name(proc_header.children[0].token.value)
        args = self._get_expected_arguments(identifier)
        self._generate_procedure_declaration(identifier, args)

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

    def _handle_assignment(self, node):
        """
        destination = node.children[0]
        expresson = node.children[1]
        result = self._handle_expression(expression)

        dest_name = self._register_name(destination.children[0].token.value)
        if len(destination.children) == 2: # array access
            index = self._register_name(destination.children[1].token.value)
            self._generate_array
        """
        pass

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
            if symbol["type"] == "array":
                index = self._handle_expression(node.children[1])
                size = symbol["array_length"]
                result = self._generate_array_load(name,size,dtype,index["value"]) #name,size,dtype,index
            else:
                dst_name = self._next_register()
                result = self._generate_load(name,dst_name,dtype) #src_name, dst_name, src_dtype
            return {
                    "value": result,
                    "dtype": dtype
                    }
        elif node.is_literal():
            return self._to_ir_literal(node)
        else:
            return self._handle_expression(node.children[0])

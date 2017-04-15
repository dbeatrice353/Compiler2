

class CodeGenerator:
    def __init__(self):
        self._symbol_table = None
        self._register_counter = 0

    def generate(self,node, symbol_table):
        self._symbol_table = symbol_table
        self._register_counter = 0
        self._generate(node)

    def _next_register(self):
        name = "%r" + str(self._register_counter)
        self._register_counter += 1
        return name

    def _generate(self,node):
        if node.name_matches('declaration'):
            child = node.children[0]
            if node.token:
                global_flag = True
            else:
                global_flag = False
            if child.name_matches('variable_declaration'):
                self._handle_variable_declaration(child,global_flag)
            if child.name_matches('procedure_declaration'):
                self._handle_procedure_declaration(child)
        else:
            for child in node.children:
                self._generate(child)

    def _put(self, statement):
        print statement

    def _generate_global_variable_declaration(self, reg_name, dtype):
        self._put("%s = global %s"%(reg_name, dtype))

    def _generate_global_array_declaration(self, reg_name, dtype, size):
        self._put("%s = global [%s x %s] zeroinitializer"%(reg_name,str(size),dtype))

    def _generate_variable_alloc(self, reg_name, dtype):
        self._put("%s = alloca %s"%(reg_name,dtype))

    def _generate_array_alloc(self, reg_name, dtype, size):
        self._put("%s = alloca [%s x %s]"%(reg_name,str(size),dtype))

    def _generate_store(self, src_name, dst_name, src_dtype, dst_dtype):
        self._put("store %s %s, %s %s"%(src_dtype, src_name, dst_dtype, dst_name))

    def _generate_load(self, src_name, dst_name, src_dtype):
        self._put("%s = load %s %s"%(dst_name, src_type, src_name))

    def _generate_procedure_declaration(self,name,args):
        header = "define void %s"%name
        arg_strings = map(lambda a: "%s %s"%(a["dtype"],a["name"]),args)
        arguments = "(" + ", ".join(arg_strings) + ")"
        self._put(header + arguments)
        for arg in args:
            arg["reg_name"] = self._next_register()
            self._generate_variable_alloc(arg["reg_name"],arg["dtype"])
        for arg in args:
            self._generate_store(arg["name"],arg["reg_name"],arg["dtype"],arg["dtype"]+"*")

    """
    define void @_Z4prociPfPKc(i32 %i, float* %f, i8* %string) #0 {
      %1 = alloca i32, align 4
      %2 = alloca float*, align 8
      %3 = alloca i8*, align 8
      store i32 %i, i32* %1, align 4
      store float* %f, float** %2, align 8
      store i8* %string, i8** %3, align 8
    """

    def _global_name(self,identifier):
        return "@" + identifier

    def _register_name(self,identifier):
        return "%" + identifier

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

    def _handle_procedure_declaration(self, node):
        proc_header = node.children[0]
        identifier = proc_header.children[0].token.value
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

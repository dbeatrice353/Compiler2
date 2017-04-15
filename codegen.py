

class CodeGenerator:
    def __init__(self):
        pass

    def generate(self,node):
        if node.name_matches('declaration'):
            child = node.children[0]
            if node.token:
                global_flag = True
            else:
                global_flag = False
            if child.name_matches('variable_declaration'):
                self._handle_variable_declaration(child,global_flag)
        else:
            for child in node.children:
                self.generate(child)

    def _generate(self,statement):
        print statement

    def _generate_global_variable_declaration(self, reg_name, dtype):
        self._generate("%s = global %s"%(reg_name, dtype))

    def _generate_global_array_declaration(self, reg_name, dtype, size):
        self._generate("%s = global [%s x %s] zeroinitializer"%(reg_name,str(size),dtype))

    def _generate_variable_alloc(self, reg_name, dtype):
        self._generate("%s = alloca %s"%(reg_name,dtype))

    def _generate_array_alloc(self, reg_name, dtype, size):
        self._generate("%s = alloca [%s x %s]"%(reg_name,str(size),dtype))

    def _generate_store(self, src_name, dst_name, src_dtype, dst_dtype):
        self._generate("store %s %s, %s %s"%(src_dtype, src_name, dst_dtype, dst_name))

    def _generate_load(self, src_name, dst_name, src_dtype):
        self._generate("%s = load %s %s"%(dst_name, src_type, src_name))

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

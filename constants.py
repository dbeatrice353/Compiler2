

RESERVED_KEY_WORDS = ['program','is','begin','procedure','end','global','in','out','inout','integer','bool','char','string','float','if','then','else','loop','return','not','false','true']
DATA_TYPES = ['integer','float','string','char','bool']
PARAM_DIRECTIONS = ['in','out','inout']
DECLARATION_INITS = ['global','procedure'] + DATA_TYPES

EXPRESSION_OPS = ['&','|']
ARITH_OPS = ['+','-']
RELATION_OPS = ['<','>=','<=','>','==','!=']
TERM_OPS = ['*','/']
BINARY_OPS = EXPRESSION_OPS + ARITH_OPS + RELATION_OPS + TERM_OPS

FP_IR_OPERATIONS = {
    "+":"fadd",
    "-":"fsub",
    "*":"fmul",
    "/":"fdiv",
    ">":"fcmp ogt",
    "<":"fcmp olt",
    "<=":"fcmp ole",
    ">=":"fcmp oge",
    "!=":"fcmp une",
    "==":"fcmp oeq"
}

INT_IR_OPERATIONS = {
    "+":"add nsw",
    "-":"sub nsw",
    "*":"mult nsw",
    "/":"sdiv nsw",
    ">":"icmp sgt",
    "<":"icmp slt",
    "<=":"icmp sle",
    ">=":"icmp sge",
    "!=":"icmp ne",
    "==":"icmp eq"
}

BOOL_IR_OPERATIONS = {
    "!=":"",
    "==":"",
    "|":"",
    "&":"",
}

FP_IR_RETURN_TYPE = {
    "+":"double",
    "-":"double",
    "*":"double",
    "/":"double",
    ">":"i1",
    "<":"i1",
    "<=":"i1",
    ">=":"i1",
    "!=":"i1",
    "==":"i1"
}

INT_IR_RETURN_TYPE = {
    "+":"i32",
    "-":"i32",
    "*":"i32",
    "/":"i32",
    ">":"i1",
    "<":"i1",
    "<=":"i1",
    ">=":"i1",
    "!=":"i1",
    "==":"i1"
}

BOOL_IR_RETURN_TYPE = {
    "!=":"i1",
    "==":"i1",
    "|":"i1",
    "&":"i1",
}



RESERVED_KEY_WORDS = ['program','is','begin','procedure','end','global','in','out','inout','integer','bool','char','string','float','if','then','else','loop','return','not','false','true']
DATA_TYPES = ['integer','float','string','char','bool']
PARAM_DIRECTIONS = ['in','out','inout']
DECLARATION_INITS = ['global','procedure'] + DATA_TYPES

EXPRESSION_OPS = ['&','|']
ARITH_OPS = ['+','-']
RELATION_OPS = ['<','>=','<=','>','==','!=']
TERM_OPS = ['*','/']
BINARY_OPS = EXPRESSION_OPS + ARITH_OPS + RELATION_OPS + TERM_OPS

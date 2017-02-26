

class SymbolTable:
    def __init__(self):
        records = []

    def new_symbol(self,symbol_record):
        records.append(symbol_record)

    def fetch(self,name,scope):
        results = filter( lambda record: record['name']==name and record['scope']==scope, self.records)
        if len(results):
            return results[0]
        else:
            return None

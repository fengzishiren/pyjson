# coding: utf-8
'''
@author: lunatic
'''
import json



class Token(object):
    def __init__(self, content, _type):
        self.content = content
        self.type = _type
    def __str__(self):
        return ' '.join((self.content, TAG.MAP[(self.type)]))

class TAG:
    OPEN_BRACE = 1  # {
    CLOSE_BRACE = 2  # }
    OPEN_BRACKET = 3  # [
    CLOSE_BRACKET = 4  # ]
    KEY = 5  # key ->string
    STRING = 6  # string
    COLON = 7  # :
    NUMBER = 8  # 10 8 18 9.10101
    BOOLEAN = 9  # true false
    COMMA = 10  # ,
    NULL = 11  # null
    
    MAP = {1:'{', 2:'}', 3:'[', 4:']', 5:'String', 6:'String', 7:':', 8:'Number', 9:'Bool', 10:',', 11:'NULL'}
    
tokens = [
    Token('{', TAG.OPEN_BRACE),
    Token('name', TAG.KEY),
    Token(':', TAG.COLON),
    Token('hzzhenglh', TAG.STRING),
    Token(',', TAG.COMMA),
    Token('profile', TAG.KEY),
    Token(':', TAG.COLON),
    Token('{', TAG.OPEN_BRACE),
    Token('name', TAG.KEY),
    Token(':', TAG.COLON),
    Token('hzzhenglh', TAG.STRING),
    Token('}', TAG.CLOSE_BRACE),
    Token(',', TAG.COMMA),
    Token('hobby', TAG.KEY),
    Token(':', TAG.COLON),
    Token('[', TAG.OPEN_BRACKET),
    Token('soccer', TAG.STRING),
    Token(',', TAG.COMMA),
    Token('basketball', TAG.STRING),
    Token(']', TAG.CLOSE_BRACKET),
    Token('}', TAG.CLOSE_BRACE),
]

class Lexer(object):
    def __init__(self):
        self.offset = 0
        self.end = tokens.__len__()
    def scan(self):
        if self.offset == self.end:
            return None;
        token = tokens[self.offset]
        self.offset += 1
        return token

class Parser(object):
    
    def __init__(self):
        self.lexer = Lexer()
        self.move()
        
    def move(self):
        self.token = self.lexer.scan()
        print self.token
    
    def program(self):
        ret = self.parse()
        if self.token != None:
            self.error('Expecting \'EOF\'')
        return ret
        
    def parse(self):
        if self.is_obj():
            return self.obj()
        if self.is_arr():
            return self.arr()
    
        self.error('Expect \'{\' or \'[\'')

    
    def match(self, _type):
        if self.token.type == _type:
            self.move()
        else:self.error('Expect \'%s\'' % TAG.MAP[_type])
             
    def obj(self):
        ret_dict = {}
        self.match(TAG.OPEN_BRACE)
        
        while True:
            key, val = self.pair()
            ret_dict[key] = val
            if self.is_sep():
                self.match(TAG.COMMA)
            else:
                break
        self.match(TAG.CLOSE_BRACE)
        return ret_dict
      
    def arr(self):
        ret_list = []
        self.match(TAG.OPEN_BRACKET)
        while True:
            val = self.value()
            ret_list.append(val)
            if self.is_sep():
                self.match(TAG.COMMA)
            else:
                break
        self.match(TAG.CLOSE_BRACKET)        
        return ret_list
        
    # "name":"hzzhenglh", ....
    def pair(self):
        key = self.token.content
        self.match(TAG.KEY)
        self.match(TAG.COLON)  # :
        val = self.value()
        return (key, val)
   
    def value(self):
        if self.is_val():
            content = self.token.content  
            self.move()
            return content
        else:return self.parse()
        
    def is_sep(self):
        print self.token
        return self.token.type == TAG.COMMA
    def is_obj(self):
        return self.token.type == TAG.OPEN_BRACE
    def is_arr(self):
        return self.token.type == TAG.OPEN_BRACKET       
    def is_val(self):
        """
        string, number, false, true, null,
        """
        return  self.token.type == TAG.BOOLEAN or\
                self.token.type == TAG.NUMBER or\
                self.token.type == TAG.STRING or\
                self.token.type == TAG.NULL
    
    def error(self, msg):
        raise Exception("Syntax Error! %s" % msg)
            
        
def main():
    ret = Parser().program()
    print ret
    print json.dumps(ret)

if __name__ == '__main__':
    main()

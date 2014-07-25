# coding: utf-8
'''
Created on 2014年7月23日

@author: lunatic
'''
import json
from lexer import Lexer, TAG


class Parser(object):
    
    def __init__(self, text):
        self.lexer = Lexer(text)
        self.move()
        
    def move(self):
        self.token = self.lexer.scan()
        #print self.token
    
    def program(self):
        ret = self.parse()
        if self.token != None:
            self.error('Expecting "EOF"')
        return ret
        
    def parse(self):
        if self.is_open_brace():
            return self.obj()
        if self.is_open_bracket():
            return self.arr()
    
        self.error('Expect "{" or "["')

    
    def match(self, __type):
        if self.token._type == __type:
            self.move()
        else:self.error('Expect "%s"' % TAG.MAP[__type])
             
    def obj(self):
        ret_dict = {}
        self.match(TAG.OPEN_BRACE)
        #Note: Mybe, Object is empty
        if self.is_close_brace():
            self.match(TAG.CLOSE_BRACE)        
            return ret_dict
        
        while not self.is_close_brace():
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
        #Note: Mybe, list is empty
        if self.is_close_bracket():
            self.match(TAG.CLOSE_BRACKET)        
            return ret_list
        
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
        return self.token._type == TAG.COMMA
    
    def is_open_brace(self):
        return self.token._type == TAG.OPEN_BRACE
    def is_open_bracket(self):
        return self.token._type == TAG.OPEN_BRACKET       
    def is_close_brace(self):
        return self.token._type == TAG.CLOSE_BRACE
    def is_close_bracket(self):
        return self.token._type == TAG.CLOSE_BRACKET
    def is_val(self):
        """
        string, number, false, true, null,
        """
        return  self.token._type == TAG.BOOLEAN or\
                self.token._type == TAG.NUMBER or\
                self.token._type == TAG.STRING or\
                self.token._type == TAG.NULL
    
    def error(self, msg):
        raise Exception('Syntax error: %s (%s)' % (msg, self.token.pos))
            
        
def main():
    text = "{\"firstName\":\"Brett\",\"lastName\":\"McLaughlin\",\"email\":\"aaaa\\\\\\\"bbbb\", \"age\":18, \"sex\":true, \"wife\":null}";
#     with open("testbig.json") as f:
#             text = '\n'.join(f.readlines())
    ret = Parser(text).program()
    print ret
    print json.loads(text)
    print json.dumps(ret)
    print text

if __name__ == '__main__':
    main()
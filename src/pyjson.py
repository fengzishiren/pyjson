# coding: utf-8
'''
Created on 2014年7月26日

@author: lunatic
'''

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
    MAP = {1:'{', 2:'}', 3:'[', 4:']', 5:'Key(String)', 6:'String', 7:':', 8:'Number', 9:'Bool', 10:',', 11:'NULL'}

class Pos:
    def __init__(self, row, col):
        self.row = row
        self.col = col
    def __str__(self):
        return '(%s, %s)' % (str(self.row + 1), str(self.col + 1))
    
class Token(object):
    def __init__(self, content, _type, pos):
        self.content = content
        self._type = _type
        self.pos = pos
        
    def __str__(self):
        return ', '.join(('Token: ', str(self.content), TAG.MAP[self._type], self.pos.__str__()))
    
class Lexer(object):
    TAG_MAP = {'{':TAG.OPEN_BRACE, '}':TAG.CLOSE_BRACE, '[':TAG.OPEN_BRACKET, ']':TAG.CLOSE_BRACKET, ':':TAG.COLON, ',':TAG.COMMA}
    # row data : escape char
    ESCAPE_DICT = {r'\"':'"', r'\\':'\\', r'\/':'/', r'\b':'\b', r'\f':'\f', r'\n':'\n', r'\r':'\r', r'\t':'\t'}  # , '\\u':'\u'}        

    def load(self, text):
        self.text = text
        self.offset, self.row, self.col = 0, 0, 0
        
    def forward(self):
        if self.text[self.offset] == '\n':
            self.row += 1
            self.col = 0
        else: 
            self.col += 1
        self.offset += 1
        
    def skip_space(self):
        while self.text.__len__() != self.offset\
             and self.text[self.offset].isspace():
            self.forward()
            
    def scan(self):
        self.skip_space()
        
        if self.text.__len__() == self.offset:
            return None
        
        start = self.offset
        _type = self.TAG_MAP.get(self.text[self.offset])
        if _type:
            self.forward()
            return Token(self.text[start: self.offset], _type, Pos(self.row, self.col - 1))
        '''
        'STRING', 'NUMBER', 'NULL', 'TRUE', 'FALSE',
        '''
        if self.text[self.offset] == '"':
            
            self.forward()
            content = ''
            # note: escape char 
            while self.text.__len__() != self.offset:
                if self.text[self.offset] == '\\':
                    #assert not end
                    self.not_end(self.offset + 1 != self.text.__len__(), 'Expect """', Pos(self.row, self.col))
                    #escape char
                    character = self.ESCAPE_DICT.get(self.text[self.offset:self.offset + 2])
                    if character == None:
                        self.error('Unsupport escape character', Pos(self.row, self.col))
                    else:
                        content += character
                        self.forward()
                elif self.text[self.offset] == '"':
                    break
                else:
                    content += self.text[self.offset]
                self.forward()
            #test not end
            self.not_end(self.text.__len__() != self.offset, 'Expect """', Pos(self.row, self.col))
            pos = Pos(self.row, self.col)
            # Note: skip "
            self.forward()  
            self.skip_space()
            #retest not end
            self.not_end(self.text.__len__() != self.offset, 'Expect ":" or "," or "}" or "]"', Pos(self.row, self.col))
                    
            _type = TAG.KEY if self.text[self.offset] == ':' else TAG.STRING
            
            return Token(content, _type, pos)
        else:
            while True:
                self.forward()
                if self.text.__len__() != self.offset and \
                    (self.text[self.offset].isalpha() or\
                    self.text[self.offset].isdigit()):
                    continue
                else: break 
            
            pos = Pos(self.row, self.col)
            self.not_end(self.text.__len__() != self.offset, 'Expect "," or "}" or "]"', pos)
            #process content
            content = self.text[start: self.offset]
            val = None
            if content == 'null':
                _type = TAG.NULL
            elif content == 'true' or content == 'false':
                _type = TAG.BOOLEAN
                val = True if content == 'true' else False
            else:
                _type = TAG.NUMBER
                try:
                    val = int(content)
                except:
                    try:
                        val = long(content)
                    except:
                        try:
                            val = float(content)
                        except:
                            self.error('Unrecognized "%s"' % content, pos)
            return Token(val, _type, pos)
                
     
    
    def not_end(self, condition, msg, pos):
        if not condition:
            self.error(msg, pos)       
        
    def error(self, msg, pos):
        raise Exception('Syntax error: %s (%s)' % (msg, pos))


class Parser(object):
    
    def __init__(self):
        self.lexer = Lexer()
        
    def move(self):
        self.token = self.lexer.scan()

    def parse_json(self, text):
        self.lexer.load(text)
        
        self.move()
        ret = self.parse()
        if self.token != None:
            self.error('Expecting "EOF"')
        return ret
    
    def parse(self):
        if self.token._type == TAG.OPEN_BRACE:
            return self.obj()
        if self.token._type == TAG.OPEN_BRACKET :
            return self.arr()
    
        self.error('Expect "{" or "["')

    
    def match(self, __type):
        if self.token._type == __type:
            self.move()
        else:self.error('Expect "%s"' % TAG.MAP[__type])
             
    def obj(self):
        ret_dict = {}
        self.match(TAG.OPEN_BRACE)
        
        while self.token._type != TAG.CLOSE_BRACE:
            key, val = self.pair()
            ret_dict[key] = val
            if self.token._type == TAG.COMMA:
                self.match(TAG.COMMA)
            else:
                break
            
        self.match(TAG.CLOSE_BRACE)
        return ret_dict
      
    def arr(self):
        ret_list = []
        self.match(TAG.OPEN_BRACKET)
        
        while self.token._type != TAG.CLOSE_BRACKET:
            val = self.value()
            ret_list.append(val)
            if self.token._type == TAG.COMMA:
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
            



if __name__ == '__main__':
    pass


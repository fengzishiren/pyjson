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
    KEY = 5  # key ->STRING
    STRING = 6  # STRING
    COLON = 7  # :
    NUMBER = 8  # 10 8 18 9.10101
    BOOLEAN = 9  # true false
    COMMA = 10  # ,
    NULL = 11  # null
    MAP = {1:'{', 2:'}', 3:'[', 4:']', 5:'Key(STRING)', 6:'STRING', 7:':', 8:'Number', 9:'Bool', 10:',', 11:'NULL'}

class Pos:
    def __init__(self, row, col):
        self.row = row
        self.col = col
    def __str__(self):
        return '(%s, %s)' % (str(self.row + 1), str(self.col + 1))
    
class Token(object):
    def __init__(self, content, _type, row, col):
        self.content = content
        self._type = _type
        self.pos = Pos(row, col)
        
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
        while self.text.__len__() != self.offset and self.text[self.offset].isspace():
            self.forward()
            
    def scan(self):
        self.skip_space()
        
        if self.text.__len__() == self.offset:
            return None
        
        start = self.offset
        _type = self.TAG_MAP.get(self.text[self.offset])
        if _type:
            tok = Token(self.text[start: self.offset], _type, self.row, self.col)
            self.forward()
            return tok
        '''
        'STRING', 'NUMBER', 'NULL', 'TRUE', 'FALSE',
        '''
        if self.text[self.offset] == '"':
            self.forward()
            row, col = self.row, self.col
            content = ''
            # note: escape char 
            while self.text.__len__() != self.offset:
                if self.text[self.offset] == '\\':
                    # assert not end
                    self.not_end(self.offset + 1 != self.text.__len__(), 'Expect """', self.row, self.col)
                    # escape char
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
            # test not end
            self.not_end(self.text.__len__() != self.offset, 'Expect """', self.row, self.col)
            # Note: skip "
            self.forward()
            self.skip_space()
            # retest not end
            self.not_end(self.text.__len__() != self.offset, 'Expect ":" or "," or "}" or "]"', self.row, self.col)
                    
            _type = TAG.KEY if self.text[self.offset] == ':' else TAG.STRING
            
            return Token(content, _type, row, col)
        else:
            # eg. null true false 
            # eg. 5280, 0.01234, 6.336E(+)4, 1.89E-4, 2E4
            while self.text.__len__() != self.offset and (self.text[self.offset].isalnum() 
                                                          or self.text[self.offset] == '.'
                                                          or self.text[self.offset] == '-'
                                                          or self.text[self.offset] == '+'):
                self.forward()
            self.not_end(self.text.__len__() != self.offset, 'Expect "," or "}" or "]"', self.row, self.col)
            
            if start == self.offset:
                self.error('Unrecognized "%s"' % self.text[start], self.row, self.col)
            # process content
            row, col = self.row, self.col
            content = self.text[start: self.offset]
            val = None
            if content == 'null':
                _type = TAG.NULL
            elif content == 'true' or content == 'false':
                _type = TAG.BOOLEAN
                val = True if content == 'true' else False
            else:
                _type = TAG.NUMBER
                if content.find('.') == -1 and content.find('E') == -1:
                    try:
                        val = int(content)
                    except:
                        try:
                            val = long(content)
                        except:
                            self.error('Unrecognized "%s"' % content, row, col)
                else:
                    try:
                        val = float(content)
                    except:
                        self.error('Unrecognized "%s"' % content, row, col)
            return Token(val, _type, row, col)
                
    
    def not_end(self, condition, msg, row, col):
        if not condition:
            self.error(msg, row, col)       
        
    def error(self, msg, row, col):
        raise Exception('Syntax error: %s (%s)' % (msg, Pos(row, col)))


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
        self.restrict(TAG.OPEN_BRACE, TAG.OPEN_BRACKET)
        if self.token._type == TAG.OPEN_BRACE:
            return self.obj()
        if self.token._type == TAG.OPEN_BRACKET :
            return self.arr()
    
        self.error('Expect "{" or "["')
    
    def match(self, __type):
        if self.token and self.token._type == __type:
            self.move()
        else:self.error('Expect "%s"' % TAG.MAP[__type])
             
    def obj(self):
        ret_dict = {}
        self.match(TAG.OPEN_BRACE)
        self.restrict(TAG.KEY, TAG.CLOSE_BRACE)
        
        if self.token._type == TAG.KEY:
            key, val = self.pair()
            ret_dict[key] = val
            while self.restrict(TAG.COMMA, TAG.CLOSE_BRACE) and self.token._type == TAG.COMMA:
                self.match(TAG.COMMA)
                key, val = self.pair()
                ret_dict[key] = val
                
        self.match(TAG.CLOSE_BRACE)
        return ret_dict
      
    def arr(self):
        ret_list = []
        self.match(TAG.OPEN_BRACKET)
        self.restrict(TAG.STRING, TAG.NULL, TAG.NUMBER, TAG.BOOLEAN, TAG.OPEN_BRACE, TAG.OPEN_BRACKET, TAG.CLOSE_BRACKET)

        if self.token._type != TAG.CLOSE_BRACKET:
            val = self.value()
            ret_list.append(val)
            while self.restrict(TAG.COMMA, TAG.CLOSE_BRACKET) and self.token._type == TAG.COMMA:
                self.match(TAG.COMMA)
                val = self.value()
                ret_list.append(val)
            
        self.match(TAG.CLOSE_BRACKET)        
        return ret_list
            
    def pair(self):
        self.restrict(TAG.KEY)
        key = self.token.content
        self.match(TAG.KEY)
        self.match(TAG.COLON)  # :
        val = self.value()
        return (key, val)
   
    def value(self):
        self.restrict(TAG.STRING, TAG.NULL, TAG.NUMBER, TAG.BOOLEAN, TAG.OPEN_BRACE, TAG.OPEN_BRACKET)
        if self.is_val():
            content = self.token.content  
            self.move()
            return content
        else:return self.parse()
        
    def is_val(self):
        """
        STRING, number, false, true, null,
        """
        return  self.token._type == TAG.BOOLEAN or\
                self.token._type == TAG.NUMBER or\
                self.token._type == TAG.STRING or\
                self.token._type == TAG.NULL
                
    def restrict(self, *types):
        if self.token and self.token._type in types:
            return True
        else:self.error('Expect %s' % ' '.join(['"%s"' % TAG.MAP[t] for t in types]))
    
    def error(self, msg):
        raise Exception('Syntax error: %s (%s)' % (msg, self.token.pos))
            

if __name__ == '__main__':
    pass


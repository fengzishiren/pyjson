# coding: utf-8
'''
Created on 2014年7月23日

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
    ESCAPE_DICT = {'\\"':'"', '\\\\':'\\', '\\/':'/', '\\b':'\b', '\\f':'\f', '\\n':'\n', '\\r':'\r', '\\t':'\t'}#, '\\u':'\u'}        
    
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

            while self.text.__len__() != self.offset:
                if self.text[self.offset] == '\\':
                    if self.offset + 1 == self.text.__len__():
                        self.error('Expect "\""', Pos(self.row, self.col))
                    else:
                        character = self.ESCAPE_DICT.get(self.text[self.offset:self.offset + 2])
                        # print 'character', character
                        if character == None:
                            self.error('Unsuppor escap character', Pos(self.row, self.col))
                        else:
                            content += character
                            self.forward()
                elif self.text[self.offset] == '"':
                    break
                else:
                    content += self.text[self.offset]
                self.forward()
                        
            if self.text.__len__() == self.offset:
                self.error('Expect "\""', Pos(self.row, self.col))
            
            # content = self.text[start+1:self.offset]#Note: skip "
            pos = Pos(self.row, self.col)
            
            self.forward()  # Note: skip "
            self.skip_space()
            
            if self.text.__len__() == self.offset:
                self.error('Expect ":" or "," or "}" or "]"', Pos(self.row, self.col))
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
            
            if self.text.__len__() == self.offset:
                self.error('Expect "," or "}" or "]"', pos)
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
                
            
    def error(self, msg, pos):
        raise Exception('Syntax error: %s (%s)' % (msg, pos))

if __name__ == '__main__':
    text = "{\"firstName\":\"Brett\",\"lastName\":\"McLaughlin\",\"email\":\"aaaa\\\"bbbb\", \"age\":18, \"sex\":true, \"wife\":null}";
    print text
    
    lexer = Lexer(text)
    while True:
        token = lexer.scan()
        if token == None:
            break
        print token
    for k, v in Lexer.ESCAPE_DICT.items():
        print k, ': ' , v
    print 'end'

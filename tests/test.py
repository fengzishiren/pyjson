# coding: utf-8
'''
Created on 2014年7月26日

@author: lunatic
'''
import json
import unittest
from pyjson import Parser

class Test(unittest.TestCase):


    def testJson(self):
        with open("testbig.json") as f:
            text = '\n'.join(f.readlines())
        ret = Parser().parse_json(text)
        print ret
        print json.dumps(ret)
        #print json.dumps(ret)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
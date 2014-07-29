# coding: utf-8
'''
Created on 2014年7月24日

@author: hzzhenglh
'''
import unittest
import json
from parser import Parser

class Test(unittest.TestCase):


    def testJson(self):
        with open("testbig.json") as f:
            text = '\n'.join(f.readlines())
        #text = "{\"firstName\":\"Brett\",\"lastName\":\"McLaughlin\",\"email\":\"aaaa\\\"\", \"age\":18, \"sex\":true, \"wife\":null}";

        ret = Parser(text).program()
        print ret
        print json.dumps(ret)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
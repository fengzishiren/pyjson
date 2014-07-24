# coding: utf-8
'''
Created on 2014年7月24日

@author: hzzhenglh
'''
import unittest


class Test(unittest.TestCase):


    def setUp(self):
        print 'up'
        pass


    def tearDown(self):
        print 'down'
        pass


    def testName(self):
        print 'mid'
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
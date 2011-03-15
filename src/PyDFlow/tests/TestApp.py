'''
@author: Tim Armstrong
'''
import unittest
import PyDFlow.app.paths as app_paths
from PyDFlow.app import *
import os.path
import os
import time

import logging
logging.basicConfig(level=logging.DEBUG)

testdir = os.path.dirname(__file__)
app_paths.add_path(os.path.join(testdir, "apps"))


@app((localfile), (None))
def write(str):
    return "myecho @output_0 '%s'" % str

@app((localfile), (localfile))
def cp(src):
    return "cp @src @output_0"
class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testCp(self):
        """
        Test a global utility
        """

        hw = localfile(os.path.join(testdir, "files/helloworld"))
        x = cp(hw)
        #TODO: for some reason this is a list.
        print x.get()
        self.assertEquals(x.open().readlines(), ["hello world!"])
        self.assertEquals(x.open().readlines(), ["hello world!"])
    
    def testUtil(self):
        # Write to a temporary file
        x = write("blah\nblah")
        self.assertEquals(x.open().readlines(), ['blah\n', 'blah\n'])
        xpath = x.get()
        x = None
        time.sleep(1)
        
        
        # write to a bound file
        y = localfile("here")
        y <<= write("sometext")
        self.assertEquals(y.open().readlines(), ['sometext\n'])
        ypath = y.get()
        y = None
        time.sleep(1)
        self.assertTrue(os.path.exists("here"), "bound file deleted accidentally")
        os.remove(ypath)
        time.sleep(1)
        
        self.assertFalse(os.path.exists("here"), "bound file should have been deleted")
        self.assertFalse(os.path.exists(xpath))
    
    def testTwoArg(self):
        @app((localfile), (localfile, localfile))
        def sort(f1, f2):
            return "sort @f1 @f2 -o @output_0"
        hw1 = localfile(os.path.join(testdir, "files/helloworld"))
        hw2 = localfile(os.path.join(testdir, "files/helloworld"))
        sort(hw1, hw2).get()
    
    def testRedir(self):
        pass
    
    def testMergeSort(self):
        import PyDFlow.examples.mergesort.mergesort as ms
        import random
        import tempfile
        import os
        files = []
        
        try:
            # Make a bunch of files with random integers
            NUM_FILES = 10
            NO_PER_FILE = 100
            for filenum in range(NUM_FILES):
                handle, path = tempfile.mkstemp()
                filehandle = os.fdopen(handle, 'w')
                files.append(path)
                for i in range(NO_PER_FILE):
                    filehandle.write("%d\n" % random.randint(1, 1000))                     
                filehandle.close()
            
            flfiles = map(ms.intfile, files)
            sorted = ms.merge_sort(flfiles)
            results = [int(x) for x in sorted.open().readlines()]
            self.assertEquals(len(results), NUM_FILES*NO_PER_FILE)
            for i in xrange(len(results) - 1):
                self.assertTrue(results[i] <= results[i+1])
        finally:
            for f in files:
                os.remove(f) 
                   
    def testSimpleMapper(self):
        import glob
        for g in glob.glob("testSimpleMapper*.txt"):
            os.remove(g)
        
        mp = SimpleMapper(localfile, "testSimpleMapper_", ".txt")
        
        mp[1] <<= write("hello world1")
        mp[4] <<= write("hello world4")
        mp.dog <<= write("hello dog")
        mp.cat <<= write("hello cat")
        
        for f in mp:
            f.get()
            
        self.assertEquals(open("testSimpleMapper_1.txt").readlines(),
                          ["hello world1\n"])
        self.assertEquals(open("testSimpleMapper_4.txt").readlines(),
                          ["hello world4\n"])
        self.assertEquals(open("testSimpleMapper_dog.txt").readlines(),
                          ["hello dog\n"])
        self.assertEquals(open("testSimpleMapper_cat.txt").readlines(),
                          ["hello cat\n"])
        
    def testSimpleMapper2(self):
        import glob
        for g in glob.glob("testSimpleMapper*.txt"):
            os.remove(g)
        
        mp = SimpleMapper(localfile, "testSimpleMapper_", ".txt")
        out = localfile("out.txt")
        out <<= cp(mp[1])
        
        mp[1] <<= write("hello world1")
    
        self.assertEquals(out.open().readlines(),
                          ["hello world1\n"])
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
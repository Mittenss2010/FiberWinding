#********************************************************************************
# Less then 80 words
# 2017-10-7 16:01
# Code by Charwee
#********************************************************************************

class switch(object):
    '''Switch'''
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        yield self.match
        raise StopIteration

    def match(self, *args):
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False

def screen_offset_calc():
    num = 0
    while (num < 10):
        num = num + 1
        yield num

def factorial():
      """ Factorial sequence using generators. """
      count = 1
      fact = 1
      while 1:
         yield fact
         count = count + 1
         fact = fact * count     
def x():
     print "Factorial program using generators."
     func = screen_offset_calc()
     i=0
     while i<18:
        print "Factorial of 1 =", func.next()
        i=i+1
     
     a = func.next()
     print int(a)*2
     
x()

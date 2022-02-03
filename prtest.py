from multiprocessing import Process,Queue
import time
class A:
    def __init__(self,val):
        self.y=val
def f1(q):
    
    time.sleep(0.5)
    
    for _ in range(10):
        x=q.get()
        print(f"x.y from f1: {x.y}")    
        x.y+=1
        print(x.y)
        q.put(x)    
        time.sleep(1)
def f2(q):
    x=A(3)
    q.put(x)
    for _ in range(10):
        x=q.get()
        print(f"x.y from f2: {x.y}")    
        x.y+=1
        time.sleep(1)
        q.put(x)
        
def main():
    q=Queue()
    p1=Process(target=f1,args=(q,))
    p2=Process(target=f2,args=(q,))
    p1.start();p2.start()

if __name__=="__main__":
    main()
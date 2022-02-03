from PIL import ImageGrab,ImageOps
import win32api,win32con
import threading
from multiprocessing import Process,Queue
import concurrent.futures
import queue
import time
import os
from coords_f import Coords
import functools as ft
import keyboard
from asciimatics.screen import ManagedScreen
from colorama import init as col_init,Fore

do_threading=False
#x_pad=343
#y_pad=386
x_pad=186 #343
y_pad=222 #222
lt=(x_pad+1,y_pad+1)
rb=(x_pad+643,y_pad+483)
col_init(autoreset=True)

def screenshot(_lt=lt,_rb=rb):
    #box=(_lt[0],_lt[1],_rb[0],_rb[1])
    #print((*_lt,*_rb))
    im=ImageGrab.grab((*_lt,*_rb))
    return im
def sum_screenshot(_lt,_rb,name=None):
    im=ImageGrab.grab((*_lt,*_rb))
    s=0
    for t in ImageOps.grayscale(im).getcolors():
        s+=sum(t)
    #im.save(f"{name}.png")
    return s
def capture_wish_boxes():
    for i,box in enumerate(Coords.Im.order_boxes):
        print(i,sum_screenshot(*box))

    
def take_screen():
   
    #time.sleep(3)
    screenshot(lt,rb)
#take_screen()

def leftClick(delay):
    leftDown(delay/2)
    leftUp(delay/2)
    #print("Click.")          #completely optional. But nice for debugging purposes.
def leftDown(delay):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(delay)
def leftUp(delay):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    time.sleep(delay)
def mousePos(*coord):
    x,y=coord
    win32api.SetCursorPos((x_pad+x,y_pad+y))
def moveClick(*coord,delay=0.05):
    #print(coord)
    mousePos(*coord)
    time.sleep(delay/2)
    leftClick(delay/2)
def get_coords():
    x,y=win32api.GetCursorPos()
    x=x-x_pad
    y=y-y_pad
    return (x,y)
def enum_reversed(x):
    for index in reversed(range(len(x))):
        yield index,x[index]

class Game:


    fc=Coords.Food
    recipes={"onigiri":[("rice",2),("nori",1)],"calroll": [("rice",1),("nori",1),("roe",1)],"maki":[("rice",1),("nori",1),("roe",2)],
            "salrol":[("rice",1),("nori",1),("salmon",2)],"sushi":[("rice",1),("nori",1),("shrimp",2)],
            "unaroll":[("rice",1),("nori",1),("unagi",2)],"dragroll":[("rice",2),("nori",1),("roe",1),("unagi",2)],
            "combo":[("rice",2),("nori",1),("unagi",1),("roe",1),("salmon",1),("shrimp",1)]}
    buy_pause=6.5
    class Ingredients:
        def __init__(self,name):
            food=Coords.Food
            ing_dict={"rice": food.rice,"shrimp": food.shrimp,"nori":food.nori,"roe":food.roe,"salmon":food.salmon,"unagi":food.unagi}
            self.name=name
            self.coords=ing_dict[name]
            self.buy_time=0
            self.buying=False
            
            if name in ["rice","nori","roe"]:
                self.def_supplies=10
                self.supplies=self.def_supplies
            else:
                self.def_supplies=5
                self.supplies=self.def_supplies
            self.na_pixel=Coords.Im.Phone.__dict__[name]
            if name=="rice":
                self.phone_instr=(Coords.Phone.Rice.main,Coords.Phone.Rice.rice)
                self.phone_exit=Coords.Phone.Rice.exit
            else:
                self.phone_instr=(Coords.Phone.Top.main,Coords.Phone.Top.__dict__[name])
                self.phone_exit=Coords.Phone.Top.exit
    class Table:
        def __init__(self,ind,eat_time):
            self.ind=ind
            self.made_time=None
            self.eat_duration=eat_time
            self.order="Empty"
            self.last_order=""
            self.order_box=[(tup[0]+x_pad,tup[1]+y_pad) for tup in Coords.Im.unpadded_order_boxes[ind]] 
            self.rolling=False
            
    class EndGame(Exception):
        pass
    class NextLevel(Exception):
        pass
    def __init__(self):

        self.rolled=True
        self.where_am_I="Init"
        self.rep_list=set()
        self.orders={i:"Empty" for i in range(6)}
        #self._eat_times={0: 12, 1: 15,2: 18,3: 21,4: 23,5: 25}
        #self._eat_times={0: 12, 1: 12,2: 15,3: 21,4: 20,5: 22}
        self._eat_times={i:8+4*i for i in range(6)} #{0: 12, 1: 12,2: 15,3: 21,4: 20,5: 22}
        self.tables={i:Game.Table(i,self._eat_times[i]) for i in range(6)}
        self.space_left=9
        self.ings={name:Game.Ingredients(name) for name in ["shrimp","rice","nori","roe","salmon","unagi"]}
        self.rec_coords={name:self.ings[name].coords for name in self.ings}
        self.winbox=[(tup[0]+x_pad,tup[1]+y_pad) for tup in Coords.Im.winbox] 
        self._cx,self._cy=win32api.GetCursorPos()
        self.message_buffer=[]
        if do_threading:
            self.order_queue=queue.Queue()
        
    def start_and_play(self):
        self.start_game()
        self.play()
    def wait_and_check(self,delay):
        time.sleep(delay)
        if keyboard.is_pressed("q"):
            raise self.EndGame
        if keyboard.is_pressed("n"):
            raise self.NextLevel
    
    
    def play(self):
        with ManagedScreen() as screen: 
            if do_threading:
                order_thread=threading.Thread(target=self.get_orders)
                output_thread=threading.Thread(target=self.update_status,args=[screen])
                make_thread=threading.Thread(target=self.make_foods)
                threads=[order_thread,make_thread]
            else:
                
                order_queue=Queue()
                table_queue=Queue()
                message_queue=Queue()
                msg_tab_queue=Queue()
                msg_sup_queue=Queue()
                order_thread=Process(target=self.get_orders,args=[order_queue,table_queue,message_queue,msg_tab_queue])
                make_thread=Process(target=self.make_foods,args=[order_queue,table_queue,message_queue,msg_sup_queue])
                output_thread=Process(target=self.update_status,args=[screen,message_queue])
                threads=[order_thread,make_thread]

            #
           # 
           
           
            for thread in threads:
                thread.start()
            #self.make_foods()
            start_next_level=self.update_status(screen,message_queue,msg_tab_queue,msg_sup_queue)
            order_queue.put(("Quit",None))
            table_queue.put("Quit")
            order_thread.join()
            make_thread.join()
            print("Order_thread quit")
            print("Output thread quit")
            #makebuy_thread.join()oo
            #print("Makebuy thread quit")
            return start_next_level
                
            try:
                pass
            except self.EndGame:
                    print("\n\n\n{:!^100}\n\n\n".format("Pressed q! Ending game"))
                    return False
            except self.NextLevel:
                    print("\n\n\n{:!^100}\n\n\n".format("We won! Starting new level"))
                    return True
            return False
    def start_game(self):
        delay=0.2
        for coord in Coords.start_sequence: 
            #print(coord)
            moveClick(*coord,delay=delay)
    def clear_tables(self):
        for coord in Coords.plates:
            moveClick(*coord,delay=0)
        #time.sleep(1)
    
    def make_foods(self,order_queue,table_queue,message_queue,msg_sup_queue):
        try:
            start=0
            while not keyboard.is_pressed("q"):
                self.where_am_I="make_foods"
                if order_queue.empty():
                   if time.time()>start+1: 
                        start=time.time()
                        self.clear_tables()
                else:
                    order,table=order_queue.get()
                    
                    if order=="Quit":
                        return
                    
                    self.update_message_buffer("Making {}!".format(order),message_queue)
                    can_make=True
                    for ingredient,count in Game.recipes[order]:
                        si=self.ings[ingredient]
                        if si.supplies<count:
                            if si.buying:
                                if time.time()-si.buy_time>Game.buy_pause:
                                    si.buying=False
                                    si.supplies+=si.def_supplies
                                    msg_sup_queue.put(self.ings)
                                else:
                                    can_make=False
                                    #self.update_message_buffer("Couldn't make {1}. {0} hasn't arrived yet.".
                                   # format(ingredient,order),message_queue)
                            else:
                                self.rep_list.add(ingredient)
                                self.update_message_buffer("Not enough {0} to make {1}!".format(ingredient,order),message_queue)
                                can_make=False
                    if can_make:

                        self.make_food(order,msg_sup_queue)     
                        table.made_time=time.time()
                        table.rolling=True
                        table.last_order=table.order
                        self.update_message_buffer(f"Made {order}",message_queue)
                        table_queue.put(table)
                        #self.space_left-=len(Game.recipes[ ood])
                    else:
                        order_queue.put((order,table))
                        self.buy_supplies(message_queue)
                    
                #print("New supplies:")
                #for ingredient,count in Game.recipes[order]:
                #   print("{0} = {1}".format(self.ings[ingredient].name,self.ings[ingredient].supplies))
            
            self.update_message_buffer("Make foods is quitting",message_queue)
        except Exception as e:
            for _ in range(100):
                self.update_message_buffer(str(e),message_queue)
    def make_food(self,food,msg_sup_queue):
        while screenshot().getpixel(Coords.Im.foodhold)!=Coords.Im.foodhold_empty:
            pass
        for ingredient,count in Game.recipes[food]:
            for _ in range(count):
                moveClick(*self.ings[ingredient].coords,delay=0)
            self.ings[ingredient].supplies-=count
            msg_sup_queue.put(self.ings)
        self.roll()
            
    def buy_supplies(self,message_queue):
        self.where_am_I="Buy supplies"
        for ing in self.ings.values(): #Zmena 1!
            if ing.supplies==0 and not ing.buying:
                self.rep_list.add(ing.name)
        try:   
            for ingredient in set(self.rep_list):
                si=self.ings[ingredient]
                moveClick(*Coords.Phone.main) #Open the phone
                moveClick(*si.phone_instr[0]); #zmena!
                if not si.buying and self.available(ingredient):
                    
                    moveClick(*si.phone_instr[1])
                    time.sleep(0.05)
                    im=screenshot()
                    if im.getpixel(Coords.Phone.normal)!=Coords.Im.Phone.normal_available:
                    
                        self.update_message_buffer("Normal nesedi: {0},{1}".format(im.getpixel(Coords.Phone.normal),
                        Coords.Im.Phone.normal_available),message_queue)
                        moveClick(*Coords.Phone.order_exit)
                        continue
                    moveClick(*Coords.Phone.normal) #Confirm the purchase
                    time.sleep(0.05)
                    im=screenshot()
                    if im.getpixel(Coords.Phone.normal)!=Coords.Im.Phone.normal_disappeared:
                    
                        self.update_message_buffer("Hasn't dissappeared",message_queue)
                        moveClick(*Coords.Phone.order_exit)
                        continue
                    self.update_message_buffer("Bought {0}".format(ingredient),message_queue)
                    si.buying=True
                    si.buy_time=time.time()
                    #si.supplies+=si.def_supplies
                    self.rep_list.remove(ingredient)
                else:
                    self.update_message_buffer("Couldn't buy {0}: not enough funds".format(ingredient)
                    ,message_queue)
                    moveClick(*self.ings[ingredient].phone_exit)
                    time.sleep(0.1)
                    #buy_supplies(self,rep_list[iind:])
                    #break
        except Exceptions as e:
            for _ in range(100):
                self.update_message_buffer(str(e),message_queue)
            
    def available(self,ingredient):
        im=screenshot()
        #print(im.getpixel(self.ings[ingredient].phone_instr[1]),self.ings[ingredient].na_pixel)
        return im.getpixel(self.ings[ingredient].phone_instr[1])!=self.ings[ingredient].na_pixel
        
    def roll(self):

        #   time.sleep(0.0)
        moveClick(201,387) 
        roll_start=time.time()
        self.clear_tables()
        
        while time.time()<roll_start+1.1:  #time.sleep(1.1)
            
            if keyboard.is_pressed("q"):
                raise self.EndGame
            if keyboard.is_pressed("n"):
                raise self.NextLevel
        self.rolled=True
        self.space_left=9
    
    def get_orders(self,order_queue,table_queue,message_queue,msg_tab_queue):
      #  print(f"Current orders: {[(ind,table.order) for ind,table in self.tables.items()]}")
        try:
            tables=self.tables
            while not keyboard.is_pressed("q"):
                while not table_queue.empty():
                    new_table=table_queue.get()
                    if new_table=="Quit":
                        return 
                    tables[new_table.ind]=new_table

                for ind,table in tables.items():
                        rval=sum_screenshot(*table.order_box)
                        if table.rolling: # precaution
                            if time.time()-table.made_time>table.eat_duration:
                                table.order="Empty"
                                table.rolling=False    
                        if rval!=Coords.Im.blank_vals[ind]:
                            if table.order=="Empty":
                                try:
                                    table.order=Coords.Im.food_vals[rval]
                                    order_queue.put((table.order,table))
                                    msg_tab_queue.put(self.tables)
                                    table.rolling=False
                                except KeyError as e:
                                    self.update_message_buffer("Unexcepted value when checking orders: "+str(e),message_queue)
                        else:
                            table.order="Empty"
        except Exception as E:
            for _ in range(10):
                self.update_message_buffer(str(e),message_queue)
       # print(f"Orders: {[table.order for table in self.tables.values()]}")
    def print_status(self,top_message,screen=None):
        os.system("cls")
        print(top_message)
        print("Orders: |",end="")
        for table in self.tables.values():
            if not table.rolling:
                print("{0}{1:^10}".format(Fore.GREEN,table.order),end="")
                
                #table.fresh=False
            else:
                print("{0:^10}".format(table.order),end="")
            print("|",end="")
        print("\nSupplies: |",end="")
        for ing in self.ings.values():
            print("{0}{1} : {2}".format(
            Fore.YELLOW if ing.buying else 
            (Fore.RED if ing.supplies==0 else 
            Fore.WHITE),
            ing.name,ing.supplies),end="")
            print("|",end="")
        print("\n")
        for message in self.message_buffer:
            print(message)

    def update_message_buffer(self,message,message_queue):
        message_queue.put([message,None])

    def update_status(self,screen,message_queue,msg_tab_queue,msg_sup_queue): 
        tables=self.tables
        ings=self.ings
        t_lastcheck=time.time()
        while not keyboard.is_pressed("q"):
            if time.time()>t_lastcheck+2:
                t_lastcheck=time.time()
                if sum_screenshot(*self.winbox) in Coords.Im.winbox_vals: # did we win?
                    return True
                
            screen.print_at(self.where_am_I,0,1)
            screen.print_at("Orders:",0,2)
            screen.print_at("|",0,3)
            tind=1 #10
            if not msg_tab_queue.empty():
                tables=msg_tab_queue.get()
            for table in tables.values():
                #screen.print_at("{0}{1:^8}".
                # format(Fore.GREEN if table.fresh else Fore.WHITE,table.order),tind,2)
                if not table.rolling:
                    screen.print_at("{0:^10}".format(table.order if table.order !="Empty" else " "),tind,3,colour=screen.COLOUR_GREEN)
                else:
                    screen.print_at("{0:^10}".format(table.last_order),tind,3,colour=screen.COLOUR_WHITE)
                tind+=9
                screen.print_at("|",tind,3)
                tind+=1
            tind=5
            screen.print_at("Supplies: ",0,tind)
            if not msg_sup_queue.empty():
                ings=msg_sup_queue.get()
            for ind,ing in enumerate(ings.values()):
                tind+=1
                if ind%2==0:
                    xcoord,ycoord=10,tind
                else:
                    xcoord,ycoord=35,tind-1    
                screen.print_at("{0:<8} : {1:<2}".format(
                ing.name,ing.supplies),xcoord,ycoord,
                colour=screen.COLOUR_YELLOW if ing.buying else 
                (screen.COLOUR_RED if ing.supplies==0 else 
                screen.COLOUR_WHITE))
            tind+=2
            #if len(self.message_buffer)>40:
            #    for i in range(len(self.message_buffer)//2):
            #        screen.print_at("{:<100}".format(""),0,tind+20+i)
            #        self.message_buffer.pop(i)
            mes_tind=tind+1
            while not message_queue.empty():
                nm=message_queue.get()
                if nm not in self.message_buffer:
                    self.message_buffer.append(nm)
            for ind,message in enumerate(self.message_buffer):
                tind+=1
                if message[1] == None:
                    self.message_buffer[ind][1]=time.time()
                    screen.print_at("{:<100}".format(message[0]),0,tind)
                elif time.time()<message[1]+5:
                    screen.print_at("{:<100}".format(message[0]),0,tind)
                else:
                    self.message_buffer[ind][1]="delete"
            for ind in range(len(self.message_buffer)-1,-1,-1):
                if self.message_buffer[ind][1]=="delete" or len(self.message_buffer)>20:
                    self.message_buffer.pop(ind)
            for ind in range(len(self.message_buffer),50):
                screen.print_at("{:<1000}".format(" "),0,mes_tind+ind)

            
            screen.refresh()
        return False

def new_game(start=True,og=None,ings=None,*,wait_for_key=False,level=1):
    if og==None:
        g=Game()
        if ings!=None:
            for i,ing in enumerate(g.ings.values()):
                ing.supplies=ings[i]
    else:
        g=og
    if start:
        g.start_game()
    while True:
        start_time=time.time()
        con=g.play()
        print("Level {1} took {0} s".format(time.time()-start_time,level))
        if con:
            if level==7:
                wait_for_key=True
            level+=1
            level_continue(wait_for_key)
            g=Game()
        else:
            print("Game ended")
            break
    return g
#204,264    
def level_continue(wait_for_key=False):
    wait_time=12
    dt=0.1
    end_time=time.time()+wait_time
    last_time=time.time()
    if wait_for_key:
        print("Level finished, press 'n' to continue")
        while not keyboard.is_pressed("n"):
            pass
    print("Level finished!")
    time.sleep(1)
    moveClick(313,253,delay=0.2)
    moveClick(313,253,delay=0.2)
    while time.time()<end_time:
        if time.time()-last_time>dt:
            print("\rStarting new level in {:.2f} seconds".format(end_time-time.time()),end="")
            last_time=time.time()
    
    
    moveClick(313,381,delay=0.1)
    moveClick(313,381,delay=0.1)
    moveClick(313,381,delay=0.00)
    #new_game(start=False)

if __name__=="__main__":
    new_game()
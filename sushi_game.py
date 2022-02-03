from PIL import ImageGrab,ImageOps
import win32api,win32con
import time
import os
from coords_f import Coords
import functools as ft
import keyboard
from asciimatics.screen import ManagedScreen
from colorama import init as col_init,Fore

#x_pad=343
#y_pad=386
x_pad=186 #827
y_pad=186 #667 
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
            while True:
                try:
                    self.update_status("Getting orders",screen)
                    #self.print_status("{0}\n".format("Getting orders"))
                    self.get_orders()
                    self.clear_tables()
                    self.update_status("Making food",screen)
                    self.make_foods()
                    self.wait_and_check(0.1)
                    self.update_status("Buying supplies",screen)
                    self.buy_supplies()
                    if sum_screenshot(*self.winbox) in Coords.Im.winbox_vals: # did we win?
                        raise self.NextLevel
                    
                    #self.message_buffer=[]
                except self.EndGame:
                    print("\n\n\n{:!^100}\n\n\n".format("Pressed q! Ending game"))
                    return False
                except self.NextLevel:
                    print("\n\n\n{:!^100}\n\n\n".format("We won! Starting new level"))
                    return True
    
    def start_game(self):
        delay=0.2
        for coord in Coords.start_sequence: 
            #print(coord)
            moveClick(*coord,delay=delay)
    def clear_tables(self):
        for coord in Coords.plates:
            moveClick(*coord,delay=0)
        #time.sleep(1)

    def make_foods(self,order_list=None):
        if order_list!=None:
            for i,order in enumerate(order_list):
                self.tables[i].order=order
        failed_orders={"Empty"}
        for table in reversed(list(self.tables.values())):
          
            can_make=True
            order=table.order
            if order in failed_orders:
                continue
            for ingredient,count in Game.recipes[order]:
                si=self.ings[ingredient]
                if si.supplies<count:
                    if si.buying:
                        if time.time()-si.buy_time>Game.buy_pause:
                            si.buying=False
                            si.supplies+=si.def_supplies
                        else:
                            can_make=False
                            self.update_message_buffer("Couldn't make {1}. {0} hasn't arrived yet.".format(ingredient,order))
                    else:
                        self.rep_list.add(ingredient)
                        self.update_message_buffer("Not enough {0} to make {1}!".format(ingredient,order))
                        can_make=False
            if can_make:

                self.make_food(order)     # updates rep_list
                table.order="Empty"
                table.made_time=time.time()
                table.rolling=True
                #self.space_left-=len(Game.recipes[ ood])
            else:
                failed_orders.add(order)
                
            #print("New supplies:")
            #for ingredient,count in Game.recipes[order]:
             #   print("{0} = {1}".format(self.ings[ingredient].name,self.ings[ingredient].supplies))
            
        

    def make_food(self,food):
        while screenshot().getpixel(Coords.Im.foodhold)!=Coords.Im.foodhold_empty:
            pass
        for ingredient,count in Game.recipes[food]:
            for _ in range(count):
                moveClick(*self.ings[ingredient].coords)
            self.ings[ingredient].supplies-=count
        self.roll()
            
    def buy_supplies(self):
        for ing in self.ings.values(): #Zmena 1!
            if ing.supplies==0 and not ing.buying:
                self.rep_list.add(ing.name)
        for ingredient in set(self.rep_list):
            si=self.ings[ingredient]
            moveClick(*Coords.Phone.main) #Open the phone
            moveClick(*si.phone_instr[0]); #zmena!
            if not si.buying and self.available(ingredient):
                
                moveClick(*si.phone_instr[1])
                time.sleep(0.05)
                im=screenshot()
                if im.getpixel(Coords.Phone.normal)!=Coords.Im.Phone.normal_available:
                   
                    self.update_message_buffer("Normal nesedi: {0},{1}".format(im.getpixel(Coords.Phone.normal),Coords.Im.Phone.normal_available))
                    moveClick(*Coords.Phone.order_exit)
                    continue
                moveClick(*Coords.Phone.normal) #Confirm the purchase
                time.sleep(0.05)
                im=screenshot()
                if im.getpixel(Coords.Phone.normal)!=Coords.Im.Phone.normal_disappeared:
                
                    self.update_message_buffer("Hasn't dissappeared")
                    moveClick(*Coords.Phone.order_exit)
                    continue
                self.update_message_buffer("Bought {0}".format(ingredient))
                si.buying=True
                si.buy_time=time.time()
                #si.supplies+=si.def_supplies
                self.rep_list.remove(ingredient)
            else:
                self.update_message_buffer("Couldn't buy {0}: not enough funds".format(ingredient))
                moveClick(*self.ings[ingredient].phone_exit)
                time.sleep(0.1)
                #buy_supplies(self,rep_list[iind:])
                #break
            
    def available(self,ingredient):
        im=screenshot()
        #print(im.getpixel(self.ings[ingredient].phone_instr[1]),self.ings[ingredient].na_pixel)
        return im.getpixel(self.ings[ingredient].phone_instr[1])!=self.ings[ingredient].na_pixel
        
    def roll(self):

        #   time.sleep(0.0)
        moveClick(201,387) 
        roll_start=time.time()
        self.clear_tables()
        self.get_orders()
        while time.time()<roll_start+1.1:  #time.sleep(1.1)
            
            if keyboard.is_pressed("q"):
                raise self.EndGame
            if keyboard.is_pressed("n"):
                raise self.NextLevel
        self.rolled=True
        self.space_left=9
    
    def get_orders(self):
      #  print(f"Current orders: {[(ind,table.order) for ind,table in self.tables.items()]}")

        for ind,table in self.tables.items():
            if table.order=="Empty": # Pozor, to znamená, že pokud to z nějakého důvodu zapomenu nastavit na empty, tak se objednávka už nikdy nezkontroluje
                
                rval=sum_screenshot(*table.order_box)
                if table.rolling:
                    if time.time()-table.made_time>table.eat_duration:
                        table.rolling=False    
                if rval!=Coords.Im.blank_vals[ind]:
                    try:
                        test_order=Coords.Im.food_vals[rval]
                        if table.rolling:
                            if test_order==table.last_order:
                                continue
                            else:
                                table.rolling=False
                        table.order=test_order
                        table.last_order=test_order
                        
                    except KeyError as e:
                        self.update_message_buffer("Unexcepted value when checking orders: "+str(e))
                else:
                    table.rolling=False    
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

    def update_message_buffer(self,message):
        self.message_buffer.append([message,None])

    def update_status(self,top_message,screen): 
        screen.print_at("Action: {:>15}".format(top_message),0,0)
        screen.print_at("Orders:",0,2)
        screen.print_at("|",0,3)
        tind=1 #10
        
        for table in self.tables.values():
            #screen.print_at("{0}{1:^8}".
            # format(Fore.GREEN if table.fresh else Fore.WHITE,table.order),tind,2)
            if not table.rolling:
                screen.print_at("{0:^10}".format(table.order if table.order is not "Empty" else " "),tind,3,colour=screen.COLOUR_GREEN)
            else:
                screen.print_at("{0:^10}".format(table.last_order),tind,3,colour=screen.COLOUR_WHITE)
            tind+=9
            screen.print_at("|",tind,3)
            tind+=1
        tind=5
        screen.print_at("Supplies: ",0,tind)
        
        for ind,ing in enumerate(self.ings.values()):
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

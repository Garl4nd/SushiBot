from PIL import ImageGrab,ImageOps
import pyautogui
import time
import keyboard
import win32api,win32con
class Timberbot:
    


    ref_root_coords=(737,605)
    ref_branch_topleft=(589,388)
    ref_branch_botright=(833,436)
    ref_left_of_tree=(583,510)
    ref_right_of_tree=(786,510)
    right_full_pix=(124, 113, 34)
    right_empty_pix= (246, 223, 180)
    left_full_pix=(222, 210, 107)
    left_empty_pix=(231, 218, 180)
    ref_full_branch_pix2=(118,58,33)
 
    def __init__(self):
        self.set_coords()
    def atbranch(self):
    #box=(_lt[0],_lt[1],_rb[0],_rb[1])
    #print((*_lt,*_rb))
        im=ImageGrab.grab((*self.branch_topleft,*self.branch_botright ) )
        lpix=im.getpixel((0,9))
        rpix=im.getpixel((im.width-1,im.height-1))
        print(lpix,rpix)
        #im.save("barea.png")
        return lpix,rpix
    def isbranch2(self):
    #box=(_lt[0],_lt[1],_rb[0],_rb[1])
    #print((*_lt,*_rb))
        print(self.sum_screenshot(self.branch_topleft,self.branch_botright))
        return self.sum_screenshot(self.branch_topleft,self.branch_botright)==852
    def isbranch3(self):
        im=ImageGrab.grab((*self.branch_topleft,*self.branch_botright ) ) 
        pix=im.getpixel((0,0))
        print(self.tupdif(self.branch_botright,self.branch_topleft))
        pix2=im.getpixel(self.tupdif(self.tupdif(self.branch_botright,self.branch_topleft),(1,1)))
        #print(pix,pix2)
        return pix==Timberbot.ref_full_branch_pix or pix2==Timberbot.ref_full_branch_pix2
    
    def sum_screenshot(self,_lt,_rb):
        im=ImageGrab.grab((*_lt,*_rb))
        s=0
        for t in ImageOps.grayscale(im).getcolors():
            s+=sum(t)
        #im.save(f"{name}.png")
        return s

    def tupsum(self,tup1,tup2):
        return tuple((x+y) for x,y in zip(tup1,tup2) )
    def tupdif(self,tup1,tup2):
        return tuple((x-y) for x,y in zip(tup1,tup2) )
    def play(self):
        self.set_coords()
        while not keyboard.is_pressed("q"):
            lpix,rpix=self.atbranch()
            if lpix==Timberbot.left_empty_pix :
                if rpix==Timberbot.right_full_pix: 
                    print("Right branch, go left")
                    self.moveClick(*self.left)   
                elif rpix==Timberbot.right_empty_pix:
                    print("Empty branches, go left")
                    self.moveClick(*self.left)   
            elif lpix==Timberbot.left_full_pix and rpix==Timberbot.right_empty_pix:
                print("Left branch, go right")
                self.moveClick(*self.right) 
    def moveClick(self,*coords,delay=0.001):
        
        #pyautogui.moveTo(*coords)
        #pyautogui.click()
        win32api.SetCursorPos(coords)
        time.sleep(delay/3)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
        time.sleep(delay/3)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
        time.sleep(delay/3)

        
        time.sleep(delay)
    def set_coords(self):
        try:
            root_x,root_y,*_=pyautogui.locateOnScreen("root.png")
        except TypeError:
            print("Counldn't find rect, setting to default")
            root_x=Timberbot.ref_root_coords[0]
            root_y=Timberbot.ref_root_coords[1]
        self.bias=self.tupdif((root_x,root_y),Timberbot.ref_root_coords)
        print("Biases: ",self.bias)
        self.branch_topleft=self.tupsum(Timberbot.ref_branch_topleft,self.bias)
        self.branch_botright=self.tupsum(Timberbot.ref_branch_botright,self.bias)
        self.left=self.tupsum(Timberbot.ref_left_of_tree,self.bias)
        self.right=self.tupsum(Timberbot.ref_right_of_tree,self.bias)


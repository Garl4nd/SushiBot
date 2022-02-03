from PIL import ImageGrab,ImageOps
from coords_f import Coords
#x_pad=343
#y_pad=386
x_pad=187 #827
y_pad=223 #667 
lt=(x_pad+1,y_pad+1)
rb=(x_pad+643,y_pad+483)

def screenshot(_lt=lt,_rb=rb):
    #box=(_lt[0],_lt[1],_rb[0],_rb[1])
    #print((*_lt,*_rb))
    im=ImageGrab.grab((*_lt,*_rb))
    im.save("Sc.png")
    return im
def fullscreen():
    im=ImageGrab.grab()
    im.save("fullscreen.png")
    return im
def sum_screenshot(_lt,_rb,name=None):
    im=ImageGrab.grab((*_lt,*_rb))
    s=0
    for t in ImageOps.grayscale(im).getcolors():
        s+=sum(t)
    if name:
        im.save(f"{name}.png")
    return s

def capture_wish_boxes():
    for i,box in enumerate(Coords.Im.order_boxes):
        print(i,sum_screenshot(*[(tup[0]+x_pad,tup[1]+y_pad) for tup in Coords.Im.unpadded_order_boxes[i]] ,f"b{i}"))

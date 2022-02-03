from dataclasses import dataclass
@dataclass
class Coords:

    @dataclass
    class Food:
        shrimp=(26,337)
        rice=(103,342)
        nori=(50,403)
        roe=(87,400)
        salmon=(33,455)
        unagi=(94,443)

    plates=[(87,212),(182,204),(284,203),(386,211),(498,212),(601,211)]
    start_sequence=[(318,205),(330,386),(331,396),(587,457),(407,381)]  

    @dataclass
    class Phone:
        main=(563,353) 
        
        @dataclass
        class Top:
            main=(554,270)
            shrimp=(489,227)
            unagi=(567,215)
            roe=(573,268)
            nori=(501,281)
            salmon=(510,326)
            exit=(595,336)
        @dataclass
        class Rice:
            main=(550,295)
            rice=(544,281)
            exit=(584,334)
        order_exit=(585, 332)
        normal=(487,291)
        express=(596,303)
        sake=(576,315)
    
    @dataclass
    class Im:
        @dataclass    
        class Phone:
            shrimp= (127, 102, 90)
            unagi= (109, 123, 127)
            roe= (127, 61, 0)
            nori= (33, 30, 11)
            salmon= (109, 123, 127)    
            rice=(95, 95, 95)
            normal_available=(187,237,166)
            normal_disappeared=(157,130,60)
        unpadded_order_boxes=[[(27,61),(88,77)],[(128,61),(189,77)],[(229,61),(290,77)],[(330,61),(391,77)],[(431,61),(492,77)],[(532,61),(593,77)]]
        order_boxes=[[(370, 447), (431, 463)],
                    [(471, 447), (532, 463)],
                    [(572, 447), (633, 463)],
                    [(673, 447), (734, 463)],
                    [(774, 447), (835, 463)],
                    [(875, 447), (936, 463)]]
        blank_vals=[6556,5954,11192,10692,7046,8101]
        food_vals={2947: 'maki', 3413: 'calroll', 2940: 'onigiri',2744: "salrol",3191: "sushi",3163:"unaroll",3577:"dragroll",4429:"combo"}
        foodhold=(223,392)
        foodhold_empty=(238, 206, 169)
        winbox=[(211,121),(430,144)]
        winbox_vals=[5489,6209] #6209 #5489
        #@dataclass
        #class Orders

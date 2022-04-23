import time
import math

try:
    import board
    import digitalio
except ImportError:
    # Dummy class for pico digital io
    class digitalio:
        class Direction:
            """Defines the direction of a digital pin"""

            def __init__(self) -> None:
                """Enum-like class to define which direction the digital values are
                going."""
                ...
            INPUT= 0
            """Read digital data in"""  

            OUTPUT= 1
            """Write digital data out"""
        class DigitalInOut:
            direction = 0
            value = 0

            def __init__(self, gpio):
                pass

    class board:
        GP0= 1
        GP1= 1
        GP2= 1
        GP3= 1
        GP4= 1
        GP5= 1
        GP6= 1
        GP7= 1
        GP8= 1
        GP9= 1
        GP10= 1
        GP11= 1
        GP12= 1
        GP13= 1
        GP14= 1
        GP15= 1
        GP16= 1
        GP17= 1
        GP18= 1
        GP19= 1
        GP20= 1
        GP21= 1
        GP22= 1



def inv_value(value,inv):
    if inv:
        value = not value
    return value

class demux_74HC4514:
    def __init__(self, pin_map):
        self.enc_dict = {
            0: 1<<0,
            1: 1<<1, 
            2: 1<<2,
            3: 1<<3, 
            4: 1<<4,
            5: 1<<5, 
            6: 1<<6,
            7: 1<<7,
            8: 1<<8,
            9: 1<<9, 
            10: 1<<10,
            11: 1<<11,    
            12: 1<<12,
            13: 1<<13, 
            14: 1<<14,
            15: 1<<15,                            
        }

        # list out keys and values separately
        self.A_list = list(self.enc_dict.keys())
        self.Y_list = list(self.enc_dict.values())

        self.pin_A0 = pin_map['input']['A0'][0]
        self.pin_A1 = pin_map['input']['A1'][0]
        self.pin_A2 = pin_map['input']['A2'][0]
        self.pin_A3 = pin_map['input']['A3'][0]

        self.pin_A0.direction = digitalio.Direction.OUTPUT
        self.pin_A1.direction = digitalio.Direction.OUTPUT
        self.pin_A2.direction = digitalio.Direction.OUTPUT
        self.pin_A3.direction = digitalio.Direction.OUTPUT

        self.pin_A0_inv = pin_map['input']['A0'][1]
        self.pin_A1_inv = pin_map['input']['A1'][1]
        self.pin_A2_inv = pin_map['input']['A2'][1]
        self.pin_A3_inv = pin_map['input']['A3'][1]


    def encode(self, input):
        #'Out to in'
        position = self.Y_list.index(input)
        return self.A_list[position]

    def decode(self, input):
        #'in to out'
        #output = 0b1111
        #output = output & (~(1 << input) & 0xF)
        #return output
        return(self.enc_dict[input])

    def set_output(self, output_pos):
        #Set input pins so that E_row 'row' is enabled!

        #output = ~(0b0001<<output_pos) & 0xF
        input = self.encode(output_pos) #Input corresponds to the states of A0 and A1 as: 0bA1A0
        level_A0 = bool((input>>0) & 0b1)
        level_A1 = bool((input>>1) & 0b1)
        level_A2 = bool((input>>2) & 0b1)
        level_A3 = bool((input>>3) & 0b1)

        #enable gpios
        print("74HC4514 input:")
        print('pin_A0={}'.format(level_A0))
        print('pin_A1={}'.format(level_A1))
        print('pin_A2={}'.format(level_A2))
        print('pin_A3={}'.format(level_A3))

        self.pin_A0.value = inv_value(level_A0, self.pin_A0_inv)
        self.pin_A1.value = inv_value(level_A1, self.pin_A1_inv)
        self.pin_A2.value = inv_value(level_A2, self.pin_A2_inv)
        self.pin_A3.value = inv_value(level_A3, self.pin_A3_inv)

class Demux_74HC139:
    def __init__(self, pin_map):

        self.enc_dict = {
            0b00: 0b1110,
            0b01: 0b1101, 
            0b10: 0b1011,
            0b11: 0b0111}

        # list out keys and values separately
        self.A_list = list(self.enc_dict.keys())
        self.Y_list = list(self.enc_dict.values())

        self.pin_1A0 = pin_map['input']['1A0'][0]
        self.pin_1A1 = pin_map['input']['1A1'][0]
        self.pin_2A0 = pin_map['input']['2A0'][0]
        self.pin_2A1 = pin_map['input']['2A1'][0]

        self.pin_1E = pin_map['input']['1E'][0]
        self.pin_2E = pin_map['input']['2E'][0]

        self.pin_1A0_inv = pin_map['input']['1A0'][1]
        self.pin_1A1_inv = pin_map['input']['1A1'][1]
        self.pin_2A0_inv = pin_map['input']['2A0'][1]
        self.pin_2A1_inv = pin_map['input']['2A1'][1]

        self.pin_1E_inv = pin_map['input']['1E'][1]
        self.pin_2E_inv = pin_map['input']['2E'][1]

        self.pin_1A0.direction = digitalio.Direction.OUTPUT
        self.pin_1A1.direction = digitalio.Direction.OUTPUT
        self.pin_2A0.direction = digitalio.Direction.OUTPUT
        self.pin_2A1.direction = digitalio.Direction.OUTPUT

        self.pin_1E.direction = digitalio.Direction.OUTPUT
        self.pin_2E.direction = digitalio.Direction.OUTPUT
    
    def __enable_rowgrp(self):
        #Enable the outputs (set E pin to low)
        self.pin_1E.value = True

    def __enable_colgrp(self):
        #Enable the outputs (set E pin to low)
        self.pin_2E.value = True

    def __disable_rowgrp(self):
        #Enable the outputs (set E pin to low)
        self.pin_1E.value = False

    def __disable_colgrp(self):
        #Enable the outputs (set E pin to low)
        self.pin_2E.value = False

    def encode(self, input):
        #'Out to in'
        position = self.Y_list.index(input)
        return self.A_list[position]

    def decode(self, input):
        #'in to out'
        #output = 0b1111
        #output = output & (~(1 << input) & 0xF)
        #return output
        return(self.enc_dict[input])

    def set_output(self, ch, output_pos):
        #Set input pins so that E_row 'row' is enabled!

        output = ~(0b0001<<output_pos) & 0xF
        input = self.encode(output) #Input corresponds to the states of A0 and A1 as: 0bA1A0
        level_A0 = bool((input>>0) & 0b1)
        level_A1 = bool((input>>1) & 0b1)
        
        #enable gpios
        print("74HC139 input:")
        print('pin_{}A0={}'.format(ch,level_A0))
        print('pin_{}A1={}'.format(ch,level_A1))

        if ch == 1:
            self.pin_1A0.value = inv_value(level_A0, self.pin_1A0_inv)
            self.pin_1A1.value = inv_value(level_A1, self.pin_1A1_inv)
        elif ch == 2:
            self.pin_2A0.value = inv_value(level_A0, self.pin_2A0_inv)
            self.pin_2A1.value = inv_value(level_A1, self.pin_2A1_inv)
        else:
            raise ValueError('invalid ch number')

    def enable_output(self, ch):

        #This is called when an enable of the pixels is wanted (after all setups)
        
        #Enable the outputs (set E pin to low -> set pin to high since this is inverted in 74HC02D)
        if ch == 1:
            self.pin_1E.value = inv_value(True, self.pin_1E_inv)
        elif ch == 2:
            self.pin_2E.value = inv_value(True, self.pin_2E_inv)
        else:
            raise ValueError('invalid ch number')
            

    def disable_output(self, ch):
        #Disable the outputs (set E pin to High -> set pin to low since this is inverted in 74HC02D)
        if ch == 1:
            self.pin_1E.value = inv_value(False, self.pin_1E_inv)
        elif ch == 2:
            self.pin_2E.value = inv_value(False, self.pin_2E_inv)
        else:
            raise ValueError('invalid ch number')

class FlipFlop:
    col_pin_map = {
    'input': {
        'A0': (digitalio.DigitalInOut(board.GP6), False),    #Connect to A0_cols header pin 13
        'A1': (digitalio.DigitalInOut(board.GP7), False),    #Connect to A1_cols header pin 14
        'A2': (digitalio.DigitalInOut(board.GP8), False),    #Connect to A2_cols header pin 15
        'A3': (digitalio.DigitalInOut(board.GP9), True),    #Connect to 2A/2B header pin 18. INVERTED
    },
    'output_r': {
        'C0_r': 1<<1,    #Q1
        'C1_r': 1<<2,    #Q2
        'C2_r': 1<<3,    #Q3
        'C3_r': 1<<4,    #Q4   
        'C4_r': 1<<5,    #Q5
        'C5_r': 1<<6,    #Q6
        'C6_r': 1<<7,    #Q7
    },
    'output_s': {
        'C0_s': 1<<9,    #Q9
        'C1_s': 1<<10,    #Q10
        'C2_s': 1<<11,    #Q11
        'C3_s': 1<<12,    #Q12
        'C4_s': 1<<13,    #Q13
        'C5_s': 1<<14,    #Q14
        'C6_s': 1<<15,    #Q15
        }
    }

    row_pin_map = {
        'input': {
            'A0': (digitalio.DigitalInOut(board.GP10), False),   #Connect to A0_rows header pin 5
            'A1': (digitalio.DigitalInOut(board.GP11), False),   #Connect to A1_rows header pin 7
            'A2': (digitalio.DigitalInOut(board.GP12), False),   #Connect to A2_rows header pin 6
            'A3': (digitalio.DigitalInOut(board.GP13), False),   #not used?
        },
        'output_r': {
            'R0_r': 1<<1,    #Q1
            'R1_r': 1<<2,    #Q2
            'R2_r': 1<<3,    #Q3
            'R3_r': 1<<4,    #Q4
            'R4_r': 1<<5,    #Q5
            'R5_r': 1<<6,    #Q6
            'R6_r': 1<<7,    #Q7
        },
        'output_s': {
            'R0_s': 1<<9,    #Q9
            'R1_s': 1<<10,    #Q10
            'R2_s': 1<<11,    #Q11
            'R3_s': 1<<12,    #Q12
            'R4_s': 1<<13,    #Q13
            'R5_s': 1<<14,    #Q14
            'R6_s': 1<<15,    #Q15
            }
        }


    enable_pin_map = {
        'input': {
            '1A0': (digitalio.DigitalInOut(board.GP0), False),  #Connect to 1A0 header pin 8
            '1A1': (digitalio.DigitalInOut(board.GP1), False),  #Connect to 1A1 header pin 9
            '2A0': (digitalio.DigitalInOut(board.GP2), False),  #Connect to 2A0 header pin 16
            '2A1': (digitalio.DigitalInOut(board.GP3), False),  #Connect to 2A1 header pin 17
            '1E':  (digitalio.DigitalInOut(board.GP4), False),   #Connect to 1A and/or 1B header pin 10/11. Inverted! High for enable!
            '2E':  (digitalio.DigitalInOut(board.GP5), True),   #Connect to header pin 19 (controlled by a pulse curcuit with cap ensures short on-time) High for pulse / enable
        },
        'output_row': {
            'E_row0': 0,
            'E_row1': 1,
            'E_row2': 2,       
            'E_row3': 3,
        },
        'output_col': {
            'E_col0': 0,   
            'E_col1': 1, 
            'E_col2': 2, 
            'E_col3': 3,
        }              
    }

    def __init__(self):
        self.enable = Demux_74HC139(self.enable_pin_map)
        self.col_demux = demux_74HC4514(self.col_pin_map)
        self.row_demux = demux_74HC4514(self.row_pin_map)


    def set_pixel(self,pixel,value):
        #Check row in pixel (tuple)
        row = pixel[0]
        row_grp = row // 7
        row_gpr_pixel = row % 7
        print("row:")
        print(row_grp,row_gpr_pixel)

        col = pixel[1]
        col_grp = col // 7
        col_gpr_pixel = col % 7
        print("col:")
        print(col_grp,col_gpr_pixel)

        #Set enable group demux        
        key = 'E_row{}'.format(row_grp)
        self.enable.set_output(1,self.enable_pin_map['output_row'][key])
        print(key)

        key = 'E_col{}'.format(col_grp)
        self.enable.set_output(2,self.enable_pin_map['output_col'][key])
        print(key)

        #Set 74HC4514 (pixel) demux
        print("pixels:")    
        if value == 0:
            key_append = 'r'
        elif value == 1:
            key_append = 's'
        else:
            pass

        key = 'C{}_{}'.format(col_gpr_pixel,key_append)
        key_set_reset = 'output_{}'.format(key_append)
        self.col_demux.set_output(self.col_pin_map[key_set_reset][key])       
        print(key_set_reset, key)

        key = 'R{}_{}'.format(row_gpr_pixel,key_append)
        key_set_reset = 'output_{}'.format(key_append)
        self.row_demux.set_output(self.row_pin_map[key_set_reset][key])       
        print(key_set_reset, key)

        #Set enable pins
        
        #Row enable, this will be held enabled from now
        self.enable.enable_output(1)

        # #Col enable, this sends a pulse 
        self.enable.enable_output(2)
        time.sleep(0.03)
        self.enable.disable_output(2)

def main():

    print('Flip Flop HEJ!')

    flipflop = FlipFlop()

    col = list(range(0,28,1))
    row = list(range(0,1,1))

    for r in row:
        for c in col:
            flipflop.set_pixel((r,c),1)     #(row,col)

if __name__ == '__main__':
    main()

import time
import math

import board
import digitalio

from flip_flop import flip_flop

# Dummy class for pico digital io
# class digitalio:
#     class Direction:
#         """Defines the direction of a digital pin"""

#         def __init__(self) -> None:
#             """Enum-like class to define which direction the digital values are
#             going."""
#             ...
#         INPUT= 0
#         """Read digital data in"""  

#         OUTPUT= 1
#         """Write digital data out"""
#     class DigitalInOut:
#         def __init__(self, gpio):
#             pass

#         direction: bool

#         value: bool


col_pin_map = {
    'input': {
        'A0': digitalio.DigitalInOut(board.GP6),    #Connect to A0_cols header pin 13
        'A1': digitalio.DigitalInOut(board.GP7),    #Connect to A1_cols header pin 14
        'A2': digitalio.DigitalInOut(board.GP8),    #Connect to A2_cols header pin 15
        'A3': digitalio.DigitalInOut(board.GP9),    #Connect to 2A/2B header pin 18. INVERTED
    },
    'output_r': {
        'C1_r': 1<<1,    #Q1
        'C2_r': 1<<2,    #Q2
        'C3_r': 1<<3,    #Q3
        'C4_r': 1<<4,    #Q4   
        'C5_r': 1<<5,    #Q5
        'C6_r': 1<<6,    #Q6
        'C7_r': 1<<7,    #Q7
    'output_s': {
        'C1_s': 1<<9,    #Q9
        'C2_s': 1<<10,    #Q10
        'C3_s': 1<<11,    #Q11
        'C4_s': 1<<12,    #Q12
        'C5_s': 1<<13,    #Q13
        'C6_s': 1<<14,    #Q14
        'C7_s': 1<<15,    #Q15
        }
    }
}

row_pin_map = {
    'input': {
        'A0': digitalio.DigitalInOut(board.GP10),   #Connect to A0_rows header pin 5
        'A1': digitalio.DigitalInOut(board.GP11),   #Connect to A1_rows header pin 7
        'A2': digitalio.DigitalInOut(board.GP12),   #Connect to A2_rows header pin 6
        'A3': digitalio.DigitalInOut(board.GP13),   #not used?
    },
    'output_r': {
        'R1_r': 1<<1,    #Q1
        'R2_r': 1<<2,    #Q2
        'R3_r': 1<<3,    #Q3
        'R4_r': 1<<4,    #Q4
        'R5_r': 1<<5,    #Q5
        'R6_r': 1<<6,    #Q6
        'R7_r': 1<<7,    #Q7
    'output_s': {
        'R1_s': 1<<9,    #Q9
        'R2_s': 1<<10,    #Q10
        'R3_s': 1<<11,    #Q11
        'R4_s': 1<<12,    #Q12
        'R5_s': 1<<13,    #Q13
        'R6_s': 1<<14,    #Q14
        'R7_s': 1<<15,    #Q15
        }
    }
}


enable_pin_map = {
    'input': {
        '1A0': digitalio.DigitalInOut(board.GP0),  #Connect to 1A0 header pin 8
        '1A1': digitalio.DigitalInOut(board.GP1),  #Connect to 1A1 header pin 9
        '2A0': digitalio.DigitalInOut(board.GP2),  #Connect to 2A0 header pin 16
        '2A1': digitalio.DigitalInOut(board.GP3),  #Connect to 2A1 header pin 17
        '1E': digitalio.DigitalInOut(board.GP4),   #Connect to 1A and/or 1B header pin 10/11. Inverted! High for enable!
        '2E': digitalio.DigitalInOut(board.GP5),   #Connect to header pin 19 (controlled by a pulse curcuit with cap ensures short on-time) High for pulse / enable
    },
    'output': {
        'E_row1': 0,
        'E_row2': 1,
        'E_row3': 2,       
        'E_row4': 3,
        'E_col1': 0,   
        'E_col2': 1, 
        'E_col3': 2, 
        'E_col4': 3,
    }              
}

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

        self.pin_A0 = pin_map['input']['A0']
        self.pin_A1 = pin_map['input']['A1']
        self.pin_A2 = pin_map['input']['A2']
        self.pin_A3 = pin_map['input']['A3']

        self.pin_A0.direction = digitalio.Direction.OUTPUT
        self.pin_A1.direction = digitalio.Direction.OUTPUT
        self.pin_A2.direction = digitalio.Direction.OUTPUT
        self.pin_A3.direction = digitalio.Direction.OUTPUT


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
        print('pin_A0={}'.format(level_A0))
        print('pin_A1={}'.format(level_A1))
        print('pin_A2={}'.format(level_A2))
        print('pin_A3={}'.format(level_A3))

        self.pin_A0.value = level_A0
        self.pin_A1.value = level_A1
        self.pin_A2.value = level_A2
        self.pin_A3.value = level_A3
    
    def set_output_inv(self, output_pos):
        #Set input pins so that E_row 'row' is enabled!

        #output = ~(0b0001<<output_pos) & 0xF
        input = self.encode(output_pos) #Input corresponds to the states of A0 and A1 as: 0bA1A0
        level_A0 = bool((input>>0) & 0b1)
        level_A1 = bool((input>>1) & 0b1)
        level_A2 = bool((input>>2) & 0b1)
        level_A3 = not bool((input>>3) & 0b1)

        #enable gpios
        print('pin_A0={}'.format(level_A0))
        print('pin_A1={}'.format(level_A1))
        print('pin_A2={}'.format(level_A2))
        print('pin_A3={}'.format(level_A3))

        self.pin_A0.value = level_A0
        self.pin_A1.value = level_A1
        self.pin_A2.value = level_A2
        self.pin_A3.value = level_A3

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

        self.pin_1A0 = pin_map['input']['1A0']
        self.pin_1A1 = pin_map['input']['1A1']
        self.pin_2A0 = pin_map['input']['2A0']
        self.pin_2A1 = pin_map['input']['2A1']

        self.pin_1E = pin_map['input']['1E']
        self.pin_2E = pin_map['input']['2E']

        #Can we assign the input pins pin_1A0 to digitalio.DigitalInOut() directly in the pin mapping dictionary instead?
        # self.pin_1A0 = digitalio.DigitalInOut(pin_map['input']['1A0'])  
        # self.pin_1A1 = digitalio.DigitalInOut(pin_map['input']['1A1']) 

        # self.pin_2A0 = digitalio.DigitalInOut(pin_map['input']['2A0']) 
        # self.pin_2A1 = digitalio.DigitalInOut(pin_map['input']['2A1']) 

        # self.pin_1E = digitalio.DigitalInOut(pin_map['input']['1E']) 
        # self.pin_2E = digitalio.DigitalInOut(pin_map['input']['2E']) 

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
        print('pin_{}A0={}'.format(ch,level_A0))
        print('pin_{}A1={}'.format(ch,level_A1))

        if ch == 1:
            self.pin_1A0.value = level_A0
            self.pin_1A1.value = level_A1
        elif ch == 2:
            self.pin_2A0.value = level_A0
            self.pin_2A1.value = level_A1
        else:
            raise ValueError('invalid ch number')

    def enable_output(self, ch):

        #This is called when an enable of the pixels is wanted (after all setups)
        
        #Enable the outputs (set E pin to low -> set pin to high since this is inverted in 74HC02D)
        if ch == 1:
            self.pin_1E.value = True
        elif ch == 2:
            self.pin_2E.value = True
        else:
            raise ValueError('invalid ch number')
            

    def disable_output(self, ch):
        #Disable the outputs (set E pin to High -> set pin to low since this is inverted in 74HC02D)
        if ch == 1:
            self.pin_1E.value = False
        elif ch == 2:
            self.pin_2E.value = False
        else:
            raise ValueError('invalid ch number')



def main():

    print('Hello World!')

    pulse_sleep = 0.1

    enable = Demux_74HC139(enable_pin_map)
    enable.set_output(1,enable_pin_map['output']['E_row1'])
    enable.set_output(2,enable_pin_map['output']['E_col1'])

    #Set = yellow up
    #Reset = black up

    #Only half the board seems to be working. ?

    col_demux = demux_74HC4514(col_pin_map)
    col_demux.set_output_inv(col_pin_map['output_s']['C1_s'])

    row_demux = demux_74HC4514(row_pin_map)
    row_demux.set_output(row_pin_map['output_r']['R1_r'])

    #Row enable, this will be held enabled from now
    enable.enable_output(1)

    #Col enable, this sends a pulse 
    #enable.enable_output(2)
    #time.sleep(pulse_sleep)
    #enable.disable_output(2)
    col_r =  col_pin_map['output_s']
    for key in col_r:
        col_demux.set_output_inv(col_r[key])
        print(key, '->', col_r[key])
        enable.enable_output(2)
        time.sleep(pulse_sleep)
        enable.disable_output(2)
    #Call enable.enable_output() after all is set up.


if __name__ == '__main__':
    main()

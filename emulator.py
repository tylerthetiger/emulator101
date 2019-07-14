#!/usr/bin/env python2
import sys
import struct
from fixedint import *
DEBUG=1
def DEBUG_PRINT(a):
    if DEBUG==1:
        print(a)
def parity(value,bits):
    bits = 0
    for i in range(0,16):
        if value[i]:
            bits+=1
    return bits%2==0
class ConditionCodes:
    def __init__(self):
        self.z = self.s = self.p = self.cy = self.ac = self.pad = 0
class EmuState:
    def __init__(self):
        self.a = UInt8()
        self.b=  UInt8()
        self.c = UInt8()
        self.d = UInt8()
        self.e = UInt8()
        self.h = UInt8()
        self.l = UInt8()
        self.sp = UInt16()
        self.pc = UInt16()
        self.memory=self.int_enable=0
        #need to check if any of these should be initialized (e.g. are interrupts enabled on startup?)
        self.cc = ConditionCodes()

class Emulator:
    def __init__(self, buffer):
        self.state = EmuState()
        self.state.memory = buffer
    '''
    EmulateInstruction will grab the current pc instruction
    decode it, perform it and update register values
    '''
#    def EmulateInstruction(self):

    def Step(self):
        opcode = ord(self.state.memory[self.state.pc])
        #self.state.pc+=1
        print hex(opcode)
        if opcode == 0x31:
            code = self.state.memory[self.state.pc:]
            self.state.sp = struct.unpack("<H", self.state.memory[1:3])[0]
            print "SP: {}".format(hex(self.state.sp))
            self.state.pc +=3
        elif opcode == 0xf3:
            print "DISABLE INTERRUPTS"
            self.state.int_enable = 0
            self.state.pc+=1
        elif opcode == 0x21:
            code = self.state.memory[self.state.pc:]
            B = ord(code[2])
            C = ord(code[1])
            self.state.l = C
            self.state.h = B
            self.state.pc+=3
        elif opcode == 0x2b:
            hl = UInt16( (self.state.h<<8)+self.state.l)
            hl-=1
            self.state.h = hl >> 8
            self.state.l = hl &0xff
            self.state.pc+=1        
        elif opcode == 0xb5:
            # ORA L
            #not possible to have overflow/carry here, so no need to do 16 bit math
            self.state.a = self.state.a | self.state.l
            self.state.cc.z = self.state.a == 0
            self.state.cc.s = self.state.a>127
            self.state.cc.cy = 0
            self.state.ac = 0
            self.state.p = parity(self.state.a,8)
            self.state.pc+=1
        elif opcode == 0x20:
            #emulator101.com has this as a nop, but looks like it's actually a JNZ
            raise Exception("WIP")
        elif opcode == 0x7c:
            a = self.state.a
            self.state.a = self.state.h
            self.state.h = a
            self.state.pc+=1
        else:
            print "instruction {} not implemented...".format(hex(opcode))
def main():
  if len(sys.argv)<2:
    print "usage: disasm.py <z80 binary file>"
    sys.exit(-1)
  filename = sys.argv[1]
  buffer=""
  with open(filename, "rb") as f:
    buffer = f.read()
  print "read in {} bytes".format(len(buffer))
  pc=0
  a = Emulator(buffer)
  for i in range(0,10):
    a.Step()
  #print a.state.cc.z
  #while (pc>=0 and pc<=len(buffer)):
  #temp=chr(1)
  #temp+=buffer[1:]
  #for i in range(0,10):
    #pc=Disassemble8080Op(buffer,pc)


if __name__=="__main__":
  main()
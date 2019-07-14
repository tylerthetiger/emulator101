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
    for i in range(0,bits):
        if value[i]:
            bits+=1
    return bits%2==0
    '''
    Z (zero) set to 1 when the result is equal to zero
    S (sign) set to 1 when bit 7 (the most significant bit or MSB) of the math instruction is set
    P (parity) is set when the answer has even parity, clear when odd parity
    CY (carry) set to 1 when the instruction resulted in a carry out or borrow into the high order bit
    AC (auxillary carry) is used mostly for BCD (binary coded decimal) math. Read the data book for more details, Space Invaders doesn't use it.
    '''
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
        self.IX = UInt16()
        self.IY = UInt16()
        self.memory=self.int_enable=0
        #need to check if any of these should be initialized (e.g. are interrupts enabled on startup?)
        self.cc = ConditionCodes()

class Emulator:
    def __init__(self, buffer):
        self.state = EmuState()
        self.state.memory = list()
        for a in buffer:
            self.state.memory+=a
        # memory map = http://www.arcaderestoration.com/memorymap/9087/Tapper.aspx
        self.state.memory += chr(0)* (0xF87F - len(buffer)) #we need to pad out the memory to match the mem map, let's just fill with 0's

    def getNextByte(self):
        #quick helper to get the next (i.e. after the pc) byte of memory
        return ord(self.state.memory[self.state.pc+1])
    def getNextTwoBytes(self):
        code = self.state.memory[self.state.pc:]
        return struct.unpack("<H", ''.join(code[1:3]))[0]
        #return ord(self.state.memory[self.state.pc+1:self.state.pc+2])

    '''
    EmulateInstruction will grab the current pc instruction
    decode it, perform it and update register values
    '''
#    def EmulateInstruction(self):

    def Step(self):
        
        opcode = ord(self.state.memory[self.state.pc])
        print "PC: {}     Opcode: {}".format(hex(self.state.pc),hex(opcode))
        print "Accumulator: {} z flag: {}".format(self.state.a,self.state.cc.z)
        #self.state.pc+=1
      #  print hex(opcode)
        if opcode == 0x31:
            #0x31	LXI SP, D16	3		SP.hi <- byte 3, SP.lo <- byte 2
            code = self.state.memory[self.state.pc:]
            #self.state.sp = struct.unpack("<H", self.state.memory[1:3])[0]
            self.state.sp = struct.unpack("<H", ''.join(code[1:3]))[0]
            
            print "SP: {}".format(hex(self.state.sp))
            self.state.pc +=3
        elif opcode == 0xf3:
            #0xf3	DI	1		special
            print "DISABLE INTERRUPTS"
            self.state.int_enable = 0
            self.state.pc+=1
        elif opcode == 0x21:
            #0x21	LXI H,D16	3		H <- byte 3, L <- byte 2
            code = self.state.memory[self.state.pc:]
            B = ord(code[2])
            C = ord(code[1])
            self.state.l = C
            self.state.h = B
            self.state.pc+=3
        elif opcode == 0x2b:
#0x2b	DCX H	1		HL = HL-1
            hl = UInt16( (self.state.h<<8)+self.state.l)
            print "BEFORE: hl: {} h: {} l: {}".format(hex(hl),hex(self.state.h),hex(self.state.l))
            hl-=1
            self.state.h = hl >> 8
            self.state.l = hl &0xff
     
            print "AFTER: hl: {} h: {} l: {}".format(hex(hl),hex(self.state.h),hex(self.state.l))

            self.state.pc+=1        
        elif opcode == 0xb5:
            # 0xb5	ORA L	1	Z, S, P, CY, AC	A <- A | L
            #not possible to have overflow/carry here, so no need to do 16 bit math
            self.state.a = UInt8(self.state.a | self.state.l)
            self.state.cc.z = self.state.a == 0
            self.state.cc.s = self.state.a>127
            self.state.cc.cy = 0
            self.state.ac = 0
            self.state.p = parity(self.state.a,8)
            self.state.pc+=1
        elif opcode == 0x20:
            #JZ e, relative jump for some reason that it jumps to e-2
            e = Int8(self.getNextByte()+2)
           # e = Int8(ord(self.state.memory[self.state.pc+1:self.state.pc+2])+2)
            print "e is {}".format(e)
            if self.state.cc.z==True:
                print "not taking the jump because Z flag is true"
                self.state.pc +=2
            else:
                print "taking the jump"
                self.state.pc+=e
            #emulator101.com has this as a nop, but looks like it's actually a JNZ
        elif opcode == 0x7c:
            #0x7c	MOV A,H	1		A <- H
            #sshould this affect the flags?
            self.state.a = self.state.h
            self.state.pc+=1
        elif opcode == 0xd3:
            #OUT (n), A     <- write out accumlator to ..?
          #  n = UInt8(ord(self.state.memory[self.state.pc+1:self.state.pc+2]))
            n = UInt8(self.getNextByte())
            print "NOT IMPLEMENTED - should write {} to {}".format(hex(self.state.a),hex(n))
            self.state.pc+=2
        elif opcode == 0x3e:
            #0x3e	MVI A,D8	2		A <- byte 2
            #condition bits not affected even tho dest is the accumulator
            self.state. a = self.getNextByte()
            #self.state.a = ord(self.state.memory[self.state.pc+1:self.state.pc+2])
            self.state.pc+=2
        elif opcode == 0x6:
           # 0x06	MVI B, D8	2		B <- byte 2
           self.state.b = self.getNextByte()
           self.state.pc+=2
        elif opcode == 0xaf:
            #0xaf	XRA A	1	Z, S, P, CY, AC	A <- A ^ A
            self.state.a = UInt8(self.state.a ^ self.state.a)
            self.state.cc.z = self.state.a == 0
            self.state.cc.s = self.state.a>127
            self.state.cc.cy = 0
            self.state.ac = 0
            self.state.p = parity(self.state.a,8)
            self.state.pc+=1
        elif opcode == 0x3c:
            #0x3c	INR A	1	Z, S, P, AC	A <- A+1
            self.state.cc.ac = 0
            self.state.cc.a = UInt8(self.state.a+1)
            self.state.cc.z = self.state.a == 0
            self.state.cc.cy = self.state.a==0 #only way for it to be 0 is if it was from a carry
            self.state.parity = parity(self.state.a,8)
            self.state.pc+=1
        elif opcode == 0x10:
            #DJNZ e
            e = Int8(self.getNextByte()+2)
            print "e is {}".format(e)
            #no condition bits affected (even for the dec b)
            self.state.b = self.state.b - 1
            if self.state.b == 0:
                print "not taking djnz jump"
                self.state.pc+=2
            else:
                print "taking a djnz jump"
                self.state.pc+=e
        elif opcode == 0xcd:
            #0xcd	CALL adr	3		(SP-1)<-PC.hi;(SP-2)<-PC.lo;SP<-SP-2;PC=adr
            print hex(self.state.sp)
            PChi = UInt8( self.state.pc>>8 )
            PClo = UInt8(self.state.pc&0xff)
            self.state.memory[self.state.sp-1] = PChi 
            self.state.memory[self.state.sp-2] =  PClo
            code = self.state.memory[self.state.pc:]
            #self.state.sp = struct.unpack("<H", self.state.memory[1:3])[0]
            self.state.pc = struct.unpack("<H", ''.join(code[1:3]))[0]
            print "new pc from call is {}".format(hex(self.state.pc))
        elif opcode == 0xdd:
            #(SP-2) < - IXL, (SP-!) < - IXH
            if self.getNextByte() != 0xe5:
                print 'next byte is {}'.format(hex((self.getNextByte())))
                raise Exception("found a 0xdd instruction that wasnt 0xdde5, dont know what to do")
            print ("IX is {}".format(self.state.IX))
            IXL = self.state.IX &0xff
            IXH = (self.state.IX >>8)
            self.state.memory[self.state.sp-2] = IXL
            self.state.memory[self.state.sp-1] = IXH
            self.state.pc +=2 #0xdde5 is the instruction


        else:
            print "instruction {} not implemented...".format(hex(opcode))
            raise Exception("unimplemented instruction")
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
  while a.state.pc <= 0x100 or 1==1:
    a.Step()
  #print a.state.cc.z
  #while (pc>=0 and pc<=len(buffer)):
  #temp=chr(1)
  #temp+=buffer[1:]
  #for i in range(0,10):
    #pc=Disassemble8080Op(buffer,pc)


if __name__=="__main__":
  main()
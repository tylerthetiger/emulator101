#!/usr/bin/env python2
import sys
import struct
from fixedint import *
DEBUG = 1


def DEBUG_PRINT(a):
  if DEBUG == 1:
    print(a)


def parity(value, bits):
  bits = 0
  for i in range(0, bits):
    if value[i]:
      bits += 1
  return bits % 2 == 0
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
    self.b = UInt8()
    self.c = UInt8()
    self.d = UInt8()
    self.e = UInt8()
    self.h = UInt8()
    self.l = UInt8()
    self.sp = UInt16()
    self.pc = UInt16()
    self.IX = UInt16()
    self.IY = UInt16()
    self.memory = self.int_enable = 0
    #need to check if any of these should be initialized (e.g. are interrupts enabled on startup?)
    self.cc = ConditionCodes()


class Emulator:

  def __init__(self, buffer):
    self.state = EmuState()
    self.state.memory = list()
    for a in buffer:
      self.state.memory += a
    # memory map = http://www.arcaderestoration.com/memorymap/9087/Tapper.aspx
    self.state.memory += chr(0) * (
      0x10000 - len(buffer)
      #  0xF87F - len(buffer)
    )  #we need to pad out the memory to match the mem map, let's just fill with 0's

  def push(self, value):
    # print "pushing {} to {}".format(hex(value),hex(self.state.sp))
    self.state.memory[self.state.sp] = chr(value)
    self.state.sp -= 1
    #print 'sp is now {}'.format(hex(self.state.sp))
  def pop(self):
    #print 'sp is {}'.format(hex(self.state.sp))
    value = self.state.memory[self.state.sp]
    self.state.sp += 1
    return ord(value)

  def cmp(self, val):  # 0xbc	CMP H	1	Z, S, P, CY, AC	A - H
    tempA16 = UInt16(self.state.a)
    tempA16 -= val
    tempA8 = UInt8(self.state.a)
    tempA8 -= self.state.h
    self.state.cc.z = tempA16 == 0
    self.state.cc.p = parity(tempA8, 8)
    self.state.cc.ac = val > tempA8
    self.state.cc.cy = False
    self.state.pc += 1

  def ora(self, val):
    # 0xb5	ORA L	1	Z, S, P, CY, AC	A <- A | L
    #not possible to have overflow/carry here, so no need to do 16 bit math
    self.state.a = UInt8(self.state.a | val)
    self.state.cc.z = self.state.a == 0
    self.state.cc.s = self.state.a > 127
    self.state.cc.cy = 0
    self.state.ac = 0
    self.state.p = parity(self.state.a, 8)
    self.state.pc += 1

  def getNextByte(self):
    #quick helper to get the next (i.e. after the pc) byte of memory
    return ord(self.state.memory[self.state.pc + 1])

  def getNextTwoBytes(self):
    code = self.state.memory[self.state.pc:]
    return struct.unpack("<H", ''.join(code[1:3]))[0]
    #return ord(self.state.memory[self.state.pc+1:self.state.pc+2])

#eventually i will want to have breakpoints and the ability to show the registers
  def dumpCurrentState(self):
    return

  '''
    EmulateInstruction will grab the current pc instruction
    decode it, perform it and update register values
    '''

  #    def EmulateInstruction(self):

  def Step(self):
    opcode = ord(self.state.memory[self.state.pc])
    print "PC: {}     Opcode: {}   SP: {}".format(
        hex(self.state.pc), hex(opcode), hex(self.state.sp))
    print "Accumulator: {} z flag: {}".format(self.state.a, self.state.cc.z)
    if self.state.cc.z == True:
      print self.state.b
     # raise Exception("ASDF")
    #self.state.pc+=1
    #  print hex(opcode)
    if opcode == 0x31:
      #0x31	LXI SP, D16	3		SP.hi <- byte 3, SP.lo <- byte 2
      code = self.state.memory[self.state.pc:]
      #self.state.sp = struct.unpack("<H", self.state.memory[1:3])[0]
      self.state.sp = struct.unpack("<H", ''.join(code[1:3]))[0]

      print "SP: {}".format(hex(self.state.sp))
      self.state.pc += 3
    elif opcode == 0xf3:
      #0xf3	DI	1		special
      print "DISABLE INTERRUPTS"
      self.state.int_enable = 0
      self.state.pc += 1
    elif opcode == 0x21:
      #0x21	LXI H,D16	3		H <- byte 3, L <- byte 2
      code = self.state.memory[self.state.pc:]
      B = ord(code[2])
      C = ord(code[1])
      self.state.l = C
      self.state.h = B
      self.state.pc += 3
    elif opcode == 0x2b:
      #0x2b	DCX H	1		HL = HL-1
      hl = UInt16((self.state.h << 8) + self.state.l)
      print "BEFORE: hl: {} h: {} l: {}".format(
          hex(hl), hex(self.state.h), hex(self.state.l))
      hl -= 1
      self.state.h = hl >> 8
      self.state.l = hl & 0xff

      print "AFTER: hl: {} h: {} l: {}".format(
          hex(hl), hex(self.state.h), hex(self.state.l))

      self.state.pc += 1
    elif opcode == 0xb0:
      self.ora(self.state.b)
    elif opcode == 0xb1:
      self.ora(self.state.c)
    elif opcode == 0xb2:
      self.ora(self.state.d)
    elif opcode == 0xb3:
      self.ora(self.state.e)
    elif opcode == 0xb4:
      self.ora(self.state.h)
    elif opcode == 0xb5:
      self.ora(self.state.l)
      # 0xb5	ORA L	1	Z, S, P, CY, AC	A <- A | L
      #not possible to have overflow/carry here, so no need to do 16 bit math
    elif opcode == 0xb6:
      hl = UInt16((self.state.h << 8) + self.state.l)
      self.ora(hl)
    elif opcode == 0xb7:
      self.ora(self.state.a)
    elif opcode == 0x20:
      #JZ e, relative jump for some reason that it jumps to e-2
      e = Int8(self.getNextByte() + 2)
      # e = Int8(ord(self.state.memory[self.state.pc+1:self.state.pc+2])+2)
      print "e is {}".format(e)
      if self.state.cc.z == True:
        print "not taking the jump because Z flag is true"
        self.state.pc += 2
      else:
        print "taking the jump"
        self.state.pc += e
      #emulator101.com has this as a nop, but looks like it's actually a JNZ
    elif opcode == 0x7c:
      #0x7c	MOV A,H	1		A <- H
      #sshould this affect the flags?
      self.state.a = self.state.h
      self.state.pc += 1
    elif opcode == 0xd3:
      #OUT (n), A     <- write out accumlator to ..?
      #  n = UInt8(ord(self.state.memory[self.state.pc+1:self.state.pc+2]))
      n = UInt8(self.getNextByte())
      print "NOT IMPLEMENTED - should write {} to {}".format(
          hex(self.state.a), hex(n))
      self.state.pc += 2
    elif opcode == 0x3e:
      #0x3e	MVI A,D8	2		A <- byte 2
      #condition bits not affected even tho dest is the accumulator
      self.state.a = self.getNextByte()
      #self.state.a = ord(self.state.memory[self.state.pc+1:self.state.pc+2])
      self.state.pc += 2
    elif opcode == 0x6:
      # 0x06	MVI B, D8	2		B <- byte 2
      self.state.b = self.getNextByte()
      self.state.pc += 2
    elif opcode == 0xaf:
      #0xaf	XRA A	1	Z, S, P, CY, AC	A <- A ^ A
      self.state.a = UInt8(self.state.a ^ self.state.a)
      self.state.cc.z = self.state.a == 0
      self.state.cc.s = self.state.a > 127
      self.state.cc.cy = 0
      self.state.ac = 0
      self.state.p = parity(self.state.a, 8)
      self.state.pc += 1
    elif opcode == 0x3c:
      #0x3c	INR A	1	Z, S, P, AC	A <- A+1
      self.state.cc.ac = 0
      self.state.cc.a = UInt8(self.state.a + 1)
      self.state.cc.z = self.state.a == 0
      self.state.cc.cy = self.state.a == 0  #only way for it to be 0 is if it was from a carry
      self.state.parity = parity(self.state.a, 8)
      self.state.pc += 1
    elif opcode == 0x10:
      #DJNZ e
      e = Int8(self.getNextByte() + 2)
      print "e is {}".format(e)
      #no condition bits affected (even for the dec b)
      self.state.b = self.state.b - 1
      if self.state.b == 0:
        print "not taking djnz jump"
        self.state.pc += 2
      else:
        print "taking a djnz jump"
        self.state.pc += e
    elif opcode == 0xcd:
      #0xcd	CALL adr	3		(SP-1)<-PC.hi;(SP-2)<-PC.lo;SP<-SP-2;PC=adr
      print hex(self.state.sp)
      PChi = UInt8(self.state.pc >> 8)
      PClo = UInt8(self.state.pc & 0xff)
      print "pchi is {} pclo is {}".format(hex(PChi), hex(PClo))
      self.push(PClo)
      self.push(PChi)

      #self.state.memory[self.state.sp-1] = PChi
      #self.state.memory[self.state.sp-2] =  PClo
      code = self.state.memory[self.state.pc:]
      #self.state.sp = struct.unpack("<H", self.state.memory[1:3])[0]
      self.state.pc = struct.unpack("<H", ''.join(code[1:3]))[0]
      print "new pc from call is {}".format(hex(self.state.pc))
    elif opcode == 0xdd:
      nextbyte = self.getNextByte()
      if nextbyte == 0xe5:
        #page 117
        # print 'next byte is {}'.format(hex((self.getNextByte())))
        print("IX is {}".format(self.state.IX))
        IXL = UInt8(self.state.IX & 0xff)
        IXH = UInt8((self.state.IX >> 8))
        self.push(IXL)
        self.push(IXH)
        self.state.pc += 2  #0xdde5 is the instruction
      elif nextbyte == 0x66:
        #reg indirect for H
        #ram:01b5 dd 66 05        LD         H,(IX+0x5)
        offset = ord(self.state.memory[self.state.pc + 2])
        value = self.state.memory[self.state.IX+offset]
        self.state.h = ord(value)
        self.state.pc +=3
      elif nextbyte == 0x56:
        offset = ord(self.state.memory[self.state.pc + 2])
        value = self.state.memory[self.state.IX+offset]
        self.state.d = ord(value)
        self.state.pc+=3
      elif nextbyte == 0x5e:
        offset = ord(self.state.memory[self.state.pc + 2])
        value = self.state.memory[self.state.IX+offset]
        self.state.e = ord(value)
        self.state.pc+=3
      elif nextbyte == 0x4e:
        offset = ord(self.state.memory[self.state.pc + 2])
        value = self.state.memory[self.state.IX+offset]
        self.state.c = ord(value)
        self.state.pc+=3
      elif nextbyte == 0x46:
        offset = ord(self.state.memory[self.state.pc + 2])
        value = self.state.memory[self.state.IX+offset]
        self.state.b = ord(value)
        self.state.pc+=3
        
    #return ord(self.state.memory[self.state.pc+1])
      elif nextbyte == 0x6e:
        #regindirect for L
        l = self.state.l
        h = self.state.h
        print "l is:{} h is: {}".format(type(l), type(h))
        print "l is {} h is {}".format(l, h)
        hl = UInt16((self.state.h << 8) + self.state.l)
        offset = ord(self.state.memory[self.state.pc + 2])
        val = self.state.memory[hl + offset]
        self.state.l = ord(val)
        self.state.pc += 3  #3 because of 0xdd 66 then offset
      elif nextbyte == 0x6e:
        #regindirect for L
        l = self.state.l
        h = self.state.h
        print "l is:{} h is: {}".format(type(l), type(h))
        print "l is {} h is {}".format(l, h)
        hl = UInt16((self.state.h << 8) + self.state.l)
        offset = ord(self.state.memory[self.state.pc + 2])
        val = self.state.memory[hl + offset]
        self.state.l = val
        self.state.pc += 3  #3 because of 0xdd 66 then offset
           

      else:
        print "next byte is: {}".format(hex(self.getNextByte()))
        #self.state.memory[self.state.sp-2] = IXL
        #self.state.memory[self.state.sp-1] = IXH
        #okay this opcode is going to be a little bit harder to implement
        #(SP-2) < - IXL, (SP-!) < - IXH
        if (self.getNextByte() and 64 != 64) or (self.getNextByte() and 6 != 0):
          errMsg = "0xdd {} dont know how to handle that instruction!".format(
              hex(self.getNextByte()))
          print hex(self.state.pc)

          raise Exception(errMsg)
        raise Exception("asdlkfj")
        # page 75 of the manual shows this instruction
        #                print "LD r, (IX+d)"

    elif opcode == 0xe1:
      #pop HL is pop l then h
      self.state.l = self.pop()
      print type(self.state.l)
      print "self.state.l is {}".format(self.state.l)
      self.state.h = self.pop()
      self.state.pc += 1
    elif opcode == 0x78:
      #0x78	MOV A,B	1		A <- B
      self.state.a = self.state.b
      self.state.pc += 1
    elif opcode == 0xb8:
      self.cmp(self.state.b)
    elif opcode == 0xb9:
      self.cmp(self.state.c)
    elif opcode == 0xba:
      self.cmp(self.state.d)
    elif opcode == 0xbb:
      self.cmp(self.state.e)
    elif opcode == 0xbc:
      self.cmp(self.state.h)
    elif opcode == 0xbd:
      self.cmp(self.state.l)
    elif opcode == 0xbe:
      self.cmp(self.state.m)
    elif opcode == 0xbf:
      self.cmp(self.state.a)
    elif opcode == 0xc0:
      #0xc0	RNZ	1		if NZ, RET
      if self.state.cc.z == False:
        ret = self.pop()
        print "in rnz returning to {}".format(hex(ret))
        self.state.pc = ret
      print "in RNZ not returning"
      self.state.pc += 1
    elif opcode == 0x79:
      #0x79	MOV A,C	1		A <- C
      self.state.a = self.state.c
      self.state.pc += 1
    elif opcode == 0xed:
      nextbyte = self.getNextByte()
      if nextbyte==0xb0:
        print "instruction is ldir"
        #Repeats LDI (LD (DE),(HL), then increments DE, HL, and decrements BC) until BC=0. Note that if BC=0 before this instruction is called, it will loop around until BC=0 again.
        #i think i might actually be good up to this point...but 
        de = UInt16((self.state.d << 8) + self.state.e)
        hl = UInt16((self.state.h << 8) + self.state.l)
        bc = UInt16((self.state.b << 8) + self.state.c)
        print "bc: {} de: {} hl: {} len(memory):{}".format(hex(bc),hex(de),hex(hl),hex(len(self.state.memory)))
        print "(de): {}".format(hex(ord(self.state.memory[de])))
        print "(hl): {}".format(hex(ord(self.state.memory[hl])))
        raise Exception("ASDF") #TODO fix this instruction
        self.state.memory[de] = self.state.memory[hl]
        de+=1
        hl+=1
        bc-=1
        if bc == -1:
          bc = pow(2,16)
        self.state.d = de >> 8
        self.state.e = de&0xff
        self.state.h = hl >> 8
        self.state.l = hl & 0xff
        self.state.b = bc>>8
        self.state.c = bc&0xff
        while bc!=0:
          de = UInt16((self.state.d << 8) + self.state.e)
          hl = UInt16((self.state.h << 8) + self.state.l)
          bc = UInt16((self.state.b << 8) + self.state.c)
        #  print "bc: {} de: {} hl: {} len(memory):{}".format(hex(bc),hex(de),hex(hl),hex(len(self.state.memory)))
          self.state.memory[de] = self.state.memory[hl]
          de+=1
          hl+=1
          bc-=1
          self.state.d = de >> 8
          self.state.e = de&0xff
          self.state.h = hl >> 8
          self.state.l = hl & 0xff
          self.state.b = bc>>8
          self.state.c = bc&0xff
        self.state.cc.p = 0
        self.state.pc+=2
      else:
        raise Exception("instruction {}{} not implemented".format(hex(opcode),hex(nextbyte)))
        
    else:
      print "instruction {} not implemented...".format(hex(opcode))
      raise Exception("unimplemented instruction")


def main():
  if len(sys.argv) < 2:
    print "usage: disasm.py <z80 binary file>"
    sys.exit(-1)
  filename = sys.argv[1]
  buffer = ""
  with open(filename, "rb") as f:
    buffer = f.read()
  print "read in {} bytes".format(len(buffer))
  pc = 0
  a = Emulator(buffer)
  while a.state.pc <= 0x100 or 1 == 1:
    a.Step()
  #print a.state.cc.z
  #while (pc>=0 and pc<=len(buffer)):
  #temp=chr(1)
  #temp+=buffer[1:]
  #for i in range(0,10):
  #pc=Disassemble8080Op(buffer,pc)


if __name__ == "__main__":
  main()

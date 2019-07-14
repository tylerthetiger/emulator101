#!/usr/bin/env python2
import sys
def NotImplemented(instr):
  raise Exception("Instr {} not implemented - are you disassembling data not code?".format(hex(instr)))

'''
buffer is the bytestring to read from and pc is the current instruction to disassemble
'''
#WIP - probably not going to bother finishing the disassembler portion
def Disassemble8080Op(buffer,pc):
  if(pc>len(buffer)):
    raise Exception("asked to disassemble PC {} but file is of size {}".format(hex(len(bufffer)), hex(pc)))
  curInst = ord(buffer[pc])
  opBytes = 1
  print "i should be disassembling the byte {}".format(hex(curInst))
  code = buffer[pc:]
  if curInst == 0x0:
    print "NOP"
  elif curInst == 0x1:
    opBytes=3
    B = format(ord(code[2]),'02x')
    C= format(ord(code[1]),'02x')
    print "LXI  B,#${}{}".format(B,C)
  elif curInst == 0x2:
    print "STAX B"
  elif curInst == 0x3:
    print "INX B"
  elif curInst == 0x4:
    print "INR B"
  elif curInst == 0x5:
    print "DCR B"
  elif curInst == 0x6:
    opBytes=2
    B=format(ord(code[1]),'02x')
    print "MVI B,#${}".format(B)
  elif curInst == 0x7:
    print "RLC"
  elif curInst == 0x8:
    NotImplemented(curInst)
  elif curInst == 0x9:
    print "DAD B"
  elif curInst == 0xa:
    print "LDAX B"
  elif curInst == 0xb:
    print "DCX B"
  elif curInst == 0xc:
    print "INR C"
  elif curInst == 0xd:
    print "DCR C"
  elif curInst == 0xe:
    opBytes = 2
    C=format(ord(code[1]),'02x')
    print "MVI C,#${}".format(C)
  elif curInst == 0xf:
    print "RRC"
  elif curInst == 0x10:
    NotImplemented(curInst)
  elif curInst == 0x11:
    opBytes = 3
    B = format(ord(code[2]),'02x')
    C = format(ord(code[1]),'02x')
    print "LXI D,#${}{}".format(B,C)
  elif curInst == 0x12:
    print "STAX D"
  elif curInst == 0x13:
    print "INX D"
  elif curInst == 0x14:
    print "INR D"
  elif curInst == 0x15:
    print "DCR D"
  elif curInst == 0x16:
    opBytes=2
    C = format(ord(code[1]),'02x')
    print "MVI D,$#{}".format(C)
  elif curInst == 0x17:
    print "RAL"
  elif curInst == 0x18:
    NotImplemented(curInst)
  elif curInst == 0x19:
    print "DAD D"
  elif curInst == 0x1a:
    print "LDAX D"
  elif curInst == 0x1b:
    print "DCX D"
  elif curInst == 0x1c:
    print "INR E"
  elif curInst == 0x1d:
    print "DCR E"
  elif curInst == 0x1e:
    opBytes = 2
    C=format(ord(code[1]),'02x')
    print "MVI E,$#{}".format(C)
  elif curInst == 0x1f:
    print "RAR"
  elif curInst == 0x20:
    NotImplemented(curInst)
  elif curInst == 0x21:
    opBytes = 3
    B = format(ord(code[2]),'02x')
    C = format(ord(code[1]),'02x')
    print "SHLD $".format(B,C)
  elif curInst == 0x22:
    opBytes = 3
    B = format(ord(code[2]),'02x')
    C = format(ord(code[1]),'02x')
    print "LXI H,$#".format(B,C)
  elif curInst == 0x23:
    print "INX H"
  elif curInst == 0x24:
    print "INR H"
  elif curInst == 0x25:
    print "DCR H"
  elif curInst == 0x26:
    opBytes = 2
    C=format(ord(code[1]),'02x')
    print "MVI H,$#".format(C)
  elif curInst == 0x27:
    print "DAA"
  elif curInst == 0x28:
    NotImplemented(curInst)
  elif curInst == 0x29:
    print "DAD H"
  elif curInst == 0x2a:
    opBytes = 3
    B = format(ord(code[2]),'02x')
    C = format(ord(code[1]),'02x')
    print "LHLD ${}{}".format(B,C)
  elif curInst == 0x2b:
    print "DCX H"
  elif curInst == 0x2c:
    print "INR L"
  elif curInst == 0x2d:
    print "DCR L"
  elif curInst == 0x2e:
    opBytes = 2
    C = format(ord(code[1]),'02x')
    print "MVI L, $#{}".format(C)
  elif curInst == 0x2f:
    print "CMA"
  elif curInst == 0x30:
    NotImplemented(curInst)
  elif curInst == 0x31:
    opBytes = 3
    B = format(ord(code[2]),'02x')
    C = format(ord(code[1]),'02x')
    print "LXI SP,$#{}{}".format(C,B)
  elif curInst == 0x32:
    opBytes = 3
    B = format(ord(code[2]),'02x')
    C = format(ord(code[1]),'02x')
    print "STA $#{}{}".format(C,B)
  elif curInst == 0x33:
    print "INX SP"
  elif curInst == 0x34:
    print "INR M"
  elif curInst == 0x35:
    print "DCR M"
  elif curInst == 0x36:
    opBytes = 2
    B = format(ord(code[1]),'02x')
    print "MVI M,$#{}".format(B)
  elif curInst == 0x37:
    print "STC"
  elif curInst == 0x38:
    NotImplemented(curInst)
  elif curInst == 0x39:
    print "DAD SP"
  elif curInst == 0x3a:
    opBytes = 3
    B = format(ord(code[2]),'02x')
    C = format(ord(code[1]),'02x')
    print "LDA $#{}{}".format(C,B)
  elif curInst == 0x3b:
    print "DCX SP"
  elif curInst == 0x3c:
    print "INR A"
  elif curInst == 0x3d:
    print "DCR A"
  elif curInst == 0x3e:
    opBytes = 2
    C = format(ord(code[1]),'02x')
    print "MVI a, $#{}".format(C)
  elif curInst == 0x3f:
    print "CMC"
  elif curInst == 0x70:
    print "MOV M,B"
  elif curInst == 0x71:
    print "MOV M,C"
  elif curInst == 0x72:
    print "MOV M,D"
  elif curInst == 0x73:
    print "MOV M,E"
  elif curInst == 0x74:
    print "MOV M,H"
  elif curInst == 0x75:
    print "MOV M,L"
  elif curInst == 0x76:
    print "HLT"
  elif curInst == 0x77:
    print "MOV M,A"
  elif curInst == 0x78:
    print "MOV A,B"
  elif curInst == 0x79:
    print "MOV A,C"
  elif curInst == 0x7a:
    print "MOV A,E"
  elif curInst == 0x7b:
    print "MOV A,E"
  elif curInst == 0x7c:
    print "MOV A,H"
  elif curInst == 0x7d:
    print "MOV A,L"
  elif curInst == 0x7e:
    print "MOV A,M"
  elif curInst == 0x7f:
    print "MOV A,A"

  elif curInst == 0xf3:
    print "DI"
  else:
    NotImplemented(curInst)
  return pc+opBytes

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
  while (pc>=0 and pc<=len(buffer)):
  #temp=chr(1)
  #temp+=buffer[1:]
  #for i in range(0,10):
    pc=Disassemble8080Op(buffer,pc)


if __name__=="__main__":
  main()
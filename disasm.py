import sys
'''
buffer is the bytestring to read from and pc is the current instruction to disassemble
'''
def Disassemble8080Op(buffer,pc):
  if(pc>len(buffer)):
    raise Exception("asked to disassemble PC {} but file is of size {}".format(hex(len(bufffer)), hex(pc)))
  curInst = ord(buffer[pc])
  opBytes = 1
  print "i should be disassembling the byte {}".format(hex(curInst))
  code = buffer[pc:]
  if curInst == 0:
    print "NOP"
  
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
  #while (pc>=0 and pc<=len(buffer)):
  for i in range(0,10):
    pc=Disassemble8080Op(buffer,pc)


if __name__=="__main__":
  main()

   #include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
   typedef struct ConditionCodes {    
    uint8_t    z:1;    
    uint8_t    s:1;    
    uint8_t    p:1;    
    uint8_t    cy:1;    
    uint8_t    ac:1;    
    uint8_t    pad:3;    
   } ConditionCodes;

   typedef struct State8080 {    
    uint8_t    a;    
    uint8_t    b;    
    uint8_t    c;    
    uint8_t    d;    
    uint8_t    e;    
    uint8_t    h;    
    uint8_t    l;    
    uint16_t    sp;    
    uint16_t    pc;    
    uint8_t     *memory;    
    struct      ConditionCodes      cc;    
    uint8_t     int_enable;    
   } State8080;    

int Parity(char a) {
    int num = 0;
    num = a&128 ? num+1 : num;
    num = a&64 ? num+1 : num;
    num = a&32 ? num+1 : num;
    num = a&16 ? num+1 : num;
    num = a&8 ? num+1 : num;
    num = a&4 ? num+1 : num;
    num = a&2 ? num+1 : num;
    num = a&1 ? num+1 : num;
    if (num==0||num==2||num==4||num==6||num==8) return 1;
    else return 0;
}
   void Emulate8080Op(State8080* state)    
   {    
    unsigned char *opcode = &state->memory[state->pc];
        printf("emulating %x\n", *opcode);

    switch(*opcode)    
    {    
        case 0x00: break;                   //NOP is easy!    
        case 0x01:                          //LXI   B,word    
            state->c = opcode[1];    
            state->b = opcode[2];    
            state->pc += 2;                  //Advance 2 more bytes    
            break;    
        /*....*/    
        case 0x41: state->b = state->c; break;    //MOV B,C    
        case 0x42: state->b = state->d; break;    //MOV B,D    
        case 0x43: state->b = state->e; break;    //MOV B,E    
            case 0x2F:                    //CMA (not)    
        state->a = ~state->a    
        //Data book says CMA doesn't effect the flags    
        break;

    case 0xe6:                    //ANI    byte    
        {    
        uint8_t x = state->a & opcode[1];    
        state->cc.z = (x == 0);    
        state->cc.s = (0x80 == (x & 0x80));    
        state->cc.p = parity(x, 8);    
        state->cc.cy = 0;           //Data book says ANI clears CY    
        state->a = x;    
        state->pc++;                //for the data byte    
        }    
        break;    
            case 0x0f:                    //RRC    
        {    
            uint8_t x = state->a;    
            state->a = ((x & 1) << 7) | (x >> 1);    
            state->cc.cy = (1 == (x&1));    
        }    
        break;

    case 0x1f:                    //RAR    
        {    
            uint8_t x = state->a;    
            state->a = (state->cc.cy << 7) | (x >> 1);    
            state->cc.cy = (1 == (x&1));    
        }    
        break;    
          case 0xfe:                      //CPI  byte    
        {    
        uint8_t x = state->a - opcode[1];    
        state->cc.z = (x == 0);    
        state->cc.s = (0x80 == (x & 0x80));    
        //It isn't clear in the data book what to do with p - had to pick    
        state->cc.p = parity(x, 8);    
        state->cc.cy = (state->a < opcode[1]);    
        state->pc++;    
        }    
        break;

         case 0x80:      //ADD B    
        {    
            // do the math with higher precision so we can capture the    
            // carry out    
            uint16_t answer = (uint16_t) state->a + (uint16_t) state->b;

            // Zero flag: if the result is zero,    
            // set the flag to zero    
            // else clear the flag    
            if ((answer & 0xff) == 0)    
                state->cc.z = 1;    
            else    
                state->cc.z = 0;    

            // Sign flag: if bit 7 is set,    
            // set the sign flag    
            // else clear the sign flag    
            if (answer & 0x80)    
                state->cc.s = 1;    
            else    
                state->cc.s = 0;    

            // Carry flag    
            if (answer > 0xff)    
                state->cc.cy = 1;    
            else    
                state->cc.cy = 0;    

            // Parity is handled by a subroutine    
            state->cc.p = Parity( answer & 0xff);    

            state->a = answer & 0xff;    
        }    

    //The code for ADD can be condensed like this    
    case 0x81:      //ADD C    
        {    
            uint16_t answer = (uint16_t) state->a + (uint16_t) state->c;    
            state->cc.z = ((answer & 0xff) == 0);    
            state->cc.s = ((answer & 0x80) != 0);    
            state->cc.cy = (answer > 0xff);    
            state->cc.p = Parity(answer&0xff);    
            state->a = answer & 0xff;    
        }
            case 0x86:      //ADD M    
        {    
            uint16_t offset = (state->h<<8) | (state->l);    
            uint16_t answer = (uint16_t) state->a + state->memory[offset];    
            state->cc.z = ((answer & 0xff) == 0);    
            state->cc.s = ((answer & 0x80) != 0);    
            state->cc.cy = (answer > 0xff);    
            state->cc.p = Parity(answer&0xff);    
            state->a = answer & 0xff;    
        }
                case 0xc2:                      //JNZ address    
            if (0 == state->cc.z)    
                state->pc = (opcode[2] << 8) | opcode[1];    
            else    
                // branch not taken    
                state->pc += 2;    
            break;

        case 0xc3:                      //JMP address    
            state->pc = (opcode[2] << 8) | opcode[1];    
            break;    
            case 0xcd:                      //CALL address    
            {    
            uint16_t    ret = state->pc+2;    
            state->memory[state->sp-1] = (ret >> 8) & 0xff;    
            state->memory[state->sp-2] = (ret & 0xff);    
            state->sp = state->sp - 2;    
            state->pc = (opcode[2] << 8) | opcode[1];    
            }    
                break;

        case 0xc9:                      //RET    
            state->pc = state->memory[state->sp] | (state->memory[state->sp+1] << 8);    
            state->sp += 2;    
            break;  

        default: {
            printf("i don't know how to emulate this instruction\n");
            exit(1);
        }      

    }    
    state->pc+=1;    
   }  


 int main (int argc, char**argv)     {
        FILE *f= fopen(argv[1], "rb");    
    if (f==NULL)    
    {    
        printf("error: Couldn't open %s\n", argv[1]);    
        exit(1);    
    }

    //Get the file size and read it into a memory buffer    
    fseek(f, 0L, SEEK_END);    
    int fsize = ftell(f);    
    fseek(f, 0L, SEEK_SET);    

    unsigned char *buffer=malloc(fsize);    

    fread(buffer, fsize, 1, f);    
    fclose(f);  

State8080 state;
state.memory = buffer;
state.pc = 0;
while (state.pc < fsize) {
    Emulate8080Op(&state);
    }
    return 0;
}
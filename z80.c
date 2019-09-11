#define CHIPS_IMPL
#include <stdio.h>
#include "z80.h"
    uint8_t mem[1<<16] = { 0 };

    uint64_t tick(int num_ticks, uint64_t pins, void* user_data) {
        if (pins & Z80_MREQ) {
            if (pins & Z80_RD) {
                Z80_SET_DATA(pins, mem[Z80_GET_ADDR(pins)]);
            }
            else if (pins & Z80_WR) {
                mem[Z80_GET_ADDR(pins)] = Z80_GET_DATA(pins);
            }
        }
        else if (pins & Z80_IORQ) {
            // FIXME: perform device I/O
        }
        return pins;
    }

int main() {
FILE *fp = fopen("tapperMainCpu.bin","rb");
if (fp==NULL) { printf("coulnd't open file\n"); return -1;}
int byte;
int n=0;
while (1) {
byte=fgetc(fp);
if (byte==EOF) break;
mem[n++]=byte;
}
printf("read in %d bytes\n",n);
z80_t cpu;
z80_desc_t desc;
desc.tick_cb = &tick;
z80_init(&cpu,&desc);
for (int i=0;i<10;i++) {
z80_exec(&cpu,10);
printf("%lx\n", cpu.bc_de_hl_fa);
}
return 0;
}

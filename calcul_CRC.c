#include <stdio.h>
#include <stdlib.h>

typedef unsigned char INT8U;
typedef unsigned short INT16U;

INT16U cal_crc_half(INT8U *pin, INT8U len);

int main()
{
    unsigned char str[] = "^P003ID";
    unsigned short crc;
    crc = cal_crc_half(str, 8);
    // gives crc = 0xAB6D

    printf("CRC of %s: %d\n", str, crc);
    
    return 0;
}


INT16U cal_crc_half(INT8U *pin, INT8U len){
    INT16U crc;
    INT8U da;
    INT8U *ptr;
    INT8U bCRCHign;
    INT8U bCRCLow;
    INT16U crc_ta[16]= { /* CRC look up table */
        0x0000,0x1021,0x2042,0x3063,0x4084,0x50a5,0x60c6,0x70e7,
        0x8108,0x9129,0xa14a,0xb16b,0xc18c,0xd1ad,0xe1ce,0xf1ef
    };
    ptr=pin;
    crc=0;
    len--;
    while(len--!=0){
        da=((INT8U)(crc>>8))>>4; /* CRC high four bits */
        crc<<=4; /* The CRC is shifted to the right by 4 bits, which is equivalent to taking the lower 12 bits of the CRC. */
        crc^=crc_ta[da^(*ptr>>4)]; /* Add the upper 4 bits of the CRC and the first half of the byte and look up the table to calculate the CRC, then add the remainder of the last CRC. */
        da=((INT8U)(crc>>8))>>4; /* CRC high four bits */
        crc<<=4; /* The CRC is shifted to the right by 4 bits, which is equivalent to taking the lower 12 bits of the CRC. */
        crc^=crc_ta[da^(*ptr&0x0f)]; /* Add the upper 4 bits of the CRC and the last half of the byte and look up the table to calculate the CRC, then add the remainder of the last CRC. */
        ptr++;
    }
    bCRCLow = crc;
    bCRCHign= (INT8U)(crc>>8);
    if(bCRCLow==0x28||bCRCLow==0x0d||bCRCLow==0x0a) {
        bCRCLow++;
    }
    if(bCRCHign==0x28||bCRCHign==0x0d||bCRCHign==0x0a) {
        bCRCHign++;
    }
    crc = ((INT16U)bCRCHign)<<8;
    crc += bCRCLow;
    return(crc);
}

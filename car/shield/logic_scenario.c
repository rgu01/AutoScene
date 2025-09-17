// Run as
//    test: 
//    echo "\n\n" && gcc -Wall shield.c -o shield.o && ./shield.o
//    library:
//    gcc -c -fPIC shield.c -o shield.o && gcc -shared -o libshield.so shield.o

#include <stdio.h>
#include <math.h>
#include <string.h>

typedef int int32_t;
typedef char bool;
typedef int id_t;
typedef int uint16_t;
typedef int uint8_t;

#define true 1
#define false 0

bool get_action(double px, double py, double vx, double vy, double ax, double ay){
    /* test code */
    if(px == 0.0 && px == 0.0 && vx == 0.0 && vx == 0.0){
        if(ax == 1.0 && ay == -1.0){
            return true;
        }
        else{
            return false;
        }
    }

    return false;
}
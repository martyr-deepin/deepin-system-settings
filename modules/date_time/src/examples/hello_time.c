#include <stdio.h>
#include <time.h>

int main(int argc, char **argv) 
{
    time_t time_value = time(NULL);

    struct tm *tm_local_value = localtime(&time_value);

    printf("DEBUG %d %s %d\n", 
           time_value, 
           tm_local_value->tm_zone, 
           tm_local_value->tm_gmtoff / 3600);

    return 0;
}

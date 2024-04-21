#include "mbed.h"

#include "RealTimeThread.h"

// spawn a new thread for the real-time task
RealTimeThread realTimeThread;

// main thread is just blinking the led on the nucleo
int main()
{
    DigitalOut led1(LED1);
    while (true) {
        led1 = !led1;
        thread_sleep_for(1000);
    }
}
#include "RealTimeThread.h"

RealTimeThread::RealTimeThread() : _Button(RTT_BUTTON, PullUp)
                                 , _Thread(osPriorityHigh, 4096)
{
    _Button.fall(callback(this, &RealTimeThread::toggleDoExecute));

    _Thread.start(callback(this, &RealTimeThread::threadTask));
    _Ticker.attach(callback(this, &RealTimeThread::sendThreadFlag), microseconds{RTT_PERIOD_US});
}

RealTimeThread::~RealTimeThread()
{
    _Ticker.detach();
    _Thread.terminate();
}

void RealTimeThread::toggleDoExecute()
{
    _do_execute = !_do_execute;
    if (_do_execute)
        _do_reset = true;
}

void RealTimeThread::threadTask()
{
    // additional LED
    DigitalOut led(RTT_LED);
    led = 0;

    // timer to measure delta time
    Timer timer;
    timer.start();
    microseconds time_previous_us{0};

    // sampling time
    const float Ts = static_cast<float>(RTT_PERIOD_US) * 1.0e-6f;

    // serial stream either to matlab or to the openlager
    SerialStream serialStream(RTT_NUM_OF_FLOATS,
                              RTT_TX,
                              RTT_RX,
                              RTT_BAUDRATE);

    // analog inputs
    AnalogIn ain1(RTT_AIN1);
    AnalogIn ain2(RTT_AIN2);

    // analog output
    AnalogOut aout(RTT_AOUT1);

    // chirp generator
    const float f0 = 0.1f;
    const float f1 = 1.0f / 2.0f / Ts;
    const float t1 = 20.0f;
    const float amplitude = 0.9f * (3.3f / 2.0f);
    const float offset = 3.3f / 2.0f;
    Chirp chirp(f0, f1, t1, Ts);
    float sinarg = 0.0f;

    // give the openLager 1000 msec time to start
    thread_sleep_for(1000);

    while (true) {
        ThisThread::flags_wait_any(_ThreadFlag);

        // logic so that _do_execute can also be triggered by the start byte via matlab
        static bool is_start_byte_received = false;
        if (!is_start_byte_received && serialStream.startByteReceived()) {
            is_start_byte_received = true;
            toggleDoExecute();
        }

        // measure delta time
        const microseconds time_us = timer.elapsed_time();
        const float dtime_us = duration_cast<microseconds>(time_us - time_previous_us).count();
        time_previous_us = time_us;

        // read analog inputs
        float uc_1 = ain1.read() * 3.3f;
        float uc_2 = ain2.read() * 3.3f;
        float u_e = offset;

        // here lifes the main logic of the mini segway
        if (_do_execute) {

            // perform frequency response measurement
            if (chirp.update()) {
                const float exc = chirp.getExc();
                // const float fchirp = chirp.getFreq();
                sinarg = chirp.getSinarg();
                u_e = amplitude * exc + offset;
            } else {
                // toggleDoExecute();
                _do_execute = false;
            }

            // write analog output
            aout.write(u_e / 3.3f);

            // send data to serial stream (openlager or laptop / pc)
            serialStream.write( dtime_us ); //  0
            serialStream.write( u_e );      //  1
            serialStream.write( uc_1 );     //  2
            serialStream.write( uc_2 );     //  3
            serialStream.write( sinarg );   //  4
            serialStream.send();

            led = 1;
        } else {

            // write analog output
            aout.write(u_e / 3.3f);

            if (_do_reset) {
                _do_reset = false;

                serialStream.reset();
                chirp.reset();

                led = 0;
            }
        }
    }
}

void RealTimeThread::sendThreadFlag()
{
    _Thread.flags_set(_ThreadFlag);
}
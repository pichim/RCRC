#ifndef REALTIME_THREAD_H_
#define REALTIME_THREAD_H_

#include <chrono>

#include "config.h"

// #include "eigen/Dense.h"

#include "Chirp.h"
#include "DebounceIn.h"
#include "SerialStream.h"
#include "ThreadFlag.h"

using namespace std::chrono;

class RealTimeThread
{
public:
    explicit RealTimeThread();
    virtual ~RealTimeThread();

private:
    Thread _Thread;
    Ticker _Ticker;
    ThreadFlag _ThreadFlag;

    DebounceIn _Button;    
    bool _do_execute{false};
    bool _do_reset{false};

    void toggleDoExecute();
    void threadTask();
    void sendThreadFlag();
};
#endif /* REALTIME_THREAD_H_ */
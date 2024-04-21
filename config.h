#ifndef CONFIG_H_
#define CONFIG_H_

// task period
// #define RTT_PERIOD_US 2500   //   400 Hz
// #define RTT_PERIOD_US 2000   //   500 Hz
// #define RTT_PERIOD_US 1000   //  1000 Hz
// #define RTT_PERIOD_US 500    //  2000Hz
#define RTT_PERIOD_US 333    //  3000Hz
// #define RTT_PERIOD_US 200    //  5000Hz
// #define RTT_PERIOD_US 100    // 10000Hz
// #define RTT_PERIOD_US  50    // 20000Hz

// streaming device, openlager or laptop / pc
// #define RTT_TX USBTX // usb to computer
// #define RTT_RX USBRX
#define RTT_TX PB_6 // via additional cable to computer or openlager
#define RTT_RX PB_7
#define RTT_BAUDRATE 2000000
#define RTT_NUM_OF_FLOATS 30

// additonal button
#define RTT_BUTTON PB_0

// additional led
#define RTT_LED PA_12

// analog inputs
#define RTT_AIN1 PA_0
#define RTT_AIN2 PA_1

// analog output
#define RTT_AOUT1 PA_4  

#endif /* CONFIG_H_ */
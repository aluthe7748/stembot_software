import signal
import socket
import math
import RPi.GPIO as GPIO

# SIGINT Handler

def shutdown(signal, frame):

    print '\n   Stopping UDP...'
    sock.close()

    print '   Stopping PWM...'
    port.stop()
    stbd.stop()
    vert.stop()

    print '   Cleaning up...'
    GPIO.cleanup(PORT)
    GPIO.cleanup(STBD)
    GPIO.cleanup(VERT)

    print '   Exiting...'
    exit(0)

#-------#
# SETUP #
#-------#
signal.signal(signal.SIGINT, shutdown)

# UDP Constants

ADDR = ('192.168.1.4', 1337)

# PWM Constants

ZERO = 7.5
FREQ = 50

# Thruster PIN numbers (can be changed as long as they are then plugged into the right pin during set up)
# brown wire -> ground
# yellow/orange -> pi (PWM)
# red goes to nothing

#TODO: update for 4 thrusters (add one)
PORT = 12 #TODO add surge
STBD = 18 #TODO add surge
VERT = 16 #TODO chnge to portheave/stbdheave

# PS3 Vector

x = 0
y = 0
z = 0

# UDP Setup

print '   Setting UDP mode...'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print '   Setting UDP bind...'
sock.bind(ADDR)

# PWM Setup
print '   Setting GPIO mode...'
GPIO.setmode(GPIO.BOARD)

print '   Setting GPIO pins...'
GPIO.setup(PORT, GPIO.OUT)
GPIO.setup(STBD, GPIO.OUT)
GPIO.setup(VERT, GPIO.OUT)
#TODO update for 4 thrusters (add)

print '   Setting PWM frequency...'
port = GPIO.PWM(PORT, FREQ)
stbd = GPIO.PWM(STBD, FREQ)
vert = GPIO.PWM(VERT, FREQ)
#TODO update for 4 thrusters (add)

print '   Setting PWM duty cycle...'
port.start(ZERO)
stbd.start(ZERO)
vert.start(ZERO)
#TODO update for 4 thrusters (add)

# The Loop

print '   Running...'
while 1:

    # Blocking Receive

    # Looking for ps3 input: if we have one, great. If not don't do anything
    try:
        data = sock.recv(2)
    except socket.error as (code, msg):
        pass

    # Update Current Trust Vector (based on input)

    if data[0] == 'x':
        x = ord(data[1]) - 127
    elif data[0] == 'y':
        y = ord(data[1]) - 127
    elif data[0] == 'z':
        z = ord(data[1]) - 127
    else:
        print '!?!?!?'
        print data
        print '!?!?!?'

    # Circularize and Rotate

    #Calculates the PWM for easch thruster
    #TODO only works for the old stembot with 3 thrusters. we need to fix it to work with 4?

    #calculates based on input from ps3 controller
    r = math.hypot(x, y)
    r = r if r < 127 else 127
    t = math.atan2(y, x)
    t -= math.pi / 4
    p = r * math.sin(t)
    s = r * math.cos(t)

    # Transforms PWM value (us) to Duty Cycle
    #TODO update to 4 thrusters (should be able to use the same equation) consider renaming v to portheave and stbdheave (maybedivide by 2?)
    p = .02 * p + ZERO
    s = .02 * s + ZERO
    v = .02 * z + ZERO
    #TODO (add)

    # Write the new PWM to "Thrusters"
    #TODO update for 4 Thrusters
    port.ChangeDutyCycle(p)
    stbd.ChangeDutyCycle(s)
    vert.ChangeDutyCycle(v)

    # Did it Crash?
    #TODO update to 4 thrusters (add)
    print '   p: %5.2f  |  s: %5.2f  |  v: %5.2f' % (p, s, v)

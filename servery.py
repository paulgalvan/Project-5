from flask import Flask, render_template
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# GPIO setup 
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)  # Left Motor Forward
GPIO.setup(32, GPIO.OUT)  # Left Motor Backward
GPIO.setup(33, GPIO.OUT)  # Right Motor Forward
GPIO.setup(35, GPIO.OUT)  # Right Motor Backward
GPIO.setup(11, GPIO.OUT)  # LED Pin

# Set up PWM for motor speed control
left_pwm_fwd = GPIO.PWM(12, 500)
left_pwm_bwd = GPIO.PWM(32, 500)
right_pwm_fwd = GPIO.PWM(33, 500)
right_pwm_bwd = GPIO.PWM(35, 500)

left_pwm_fwd.start(0)
left_pwm_bwd.start(0)
right_pwm_fwd.start(0)
right_pwm_bwd.start(0)

GPIO.output(11, GPIO.LOW)  # Ensure LED is off initially
led_state = False  # Track LED state

def control_left_motor(speed, direction):
    if direction == 1:
        left_pwm_bwd.ChangeDutyCycle(0)
        left_pwm_fwd.ChangeDutyCycle(speed)
    elif direction == -1:
        left_pwm_fwd.ChangeDutyCycle(0)
        left_pwm_bwd.ChangeDutyCycle(speed)

def control_right_motor(speed, direction):
    if direction == 1:
        right_pwm_bwd.ChangeDutyCycle(0)
        right_pwm_fwd.ChangeDutyCycle(speed)
    elif direction == -1:
        right_pwm_fwd.ChangeDutyCycle(0)
        right_pwm_bwd.ChangeDutyCycle(speed)

@app.route('/')
def home():
    return render_template('control.html')

@app.route('/move/<direction>')
def move(direction):
    speed = 100
    if direction == 'forward':
        control_left_motor(speed, -1)  # Reverse direction
        control_right_motor(speed, -1)  # Reverse direction
    elif direction == 'backward':
        control_left_motor(speed, 1)  # Reverse direction
        control_right_motor(speed, 1)  # Reverse direction
    elif direction == 'left':
        control_left_motor(speed, -1)
        control_right_motor(speed, 1)
        time.sleep(0.3)
        control_left_motor(0, 1)
        control_right_motor(0, 1)
    elif direction == 'right':
        control_left_motor(speed, 1)
        control_right_motor(speed, -1)
        time.sleep(0.3)
        control_left_motor(0, 1)
        control_right_motor(0, 1)
    elif direction == 'stop':
        control_left_motor(0, 1)
        control_right_motor(0, 1)
    return f"Action: {direction}"


@app.route('/toggle_led', methods=['POST'])
def toggle_led():
    global led_state
    led_state = not led_state
    GPIO.output(11, GPIO.HIGH if led_state else GPIO.LOW)
    return "LED On" if led_state else "LED Off"

@app.route('/shutdown')
def shutdown():
    left_pwm_fwd.stop()
    left_pwm_bwd.stop()
    right_pwm_fwd.stop()
    right_pwm_bwd.stop()
    GPIO.cleanup()
    return "System shutdown!"

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        GPIO.cleanup()

'''class Rule:

    def __init__(self, state1, state2, signal, action):
        self.state1 = state1
        self.state2 = state2
        self.signal = signal
        self.action = action

def signal_is_digit(signal):
    return 48 <= ord(signal) <= 57
'''
import time
import RPi.GPIO as GPIO


class Keypad:

    rows = [18, 23, 24, 25]
    columns = [17, 27, 22]
    symbols = {'nokey' : 'No Key', '1817' : 1, '1827' : 2, '1822' : 3, '2317' : 4, '2327' : 5, '2322' : 6, '2417' : 7, '2427' : 8, '2422' : 9, '2517' : '*', '2527' : 0, '2522' : '#'}


    def setup(self):

        GPIO.setmode(GPIO.BCM)

        for x in self.rows:
            GPIO.setup(x, GPIO.OUT)

        for y in self.columns:
            GPIO.setup(y, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

    def do_polling(self):

        match = False
        keystring = 'nokey'

        for r in self.rows:
            GPIO.output(r, GPIO.HIGH)

            for c in self.columns:
                if GPIO.input(c) == GPIO.HIGH:
                    x = True
                    keystring = str(r) + str(c)

            if match:
                break

            GPIO.output(r, GPIO.LOW)

        return self.symbols[keystring]

    def get_next_signal(self):

        count = 0
        prevkey = 'start'
        key = None

        while count < 20:
            key = self.do_polling()
            if key != 'No key':
                if prevkey == 'start':
                    prevkey = key
                    count += 1

                elif prevkey == key:
                    count += 1

                else:
                    prevkey = 'start'
                    count += 1
        time.sleep(0.010)
        print('keypad key =', key)
        return key


class Ledboard:
    def __init__(self): #Set the proper mode via: GPIO.setmode(GPIO.BCM).
        self.pins = [13, 16, 26]  # Set the proper mode via: GPIO.setmode(GPIO.BCM).
        self.pin_led_states = [
            [1, 0, -1], # 1
            [0, 1, -1], # 2
            [1, -1, 0], # 3
            [0, -1, 1], # 4
            [-1, 1, 0], # 5
            [-1, 0, 1], # 6
            [-1,-1,-1]
        ]
        GPIO.setmode(GPIO.BCM)

    def set_pin(self, pin_index, pin_state):

        if pin_state == -1:
            GPIO.setup(self.pins[pin_index], GPIO.IN)
        else:
            GPIO.setup(self.pins[pin_index], GPIO.OUT)
            GPIO.output(self.pins[pin_index], pin_state)


    def turn_on_led(self, Lid):  # Skru på lys
        for pin_index, pin_state in enumerate(self.pin_led_states[Lid-1]):
            self.set_pin(pin_index, pin_state)

    def shut_off_lights(self):  # Skru av lys
        for i in range(0,3):
            self.set_pin(i, 0)

    #Turn on one of the 6 LEDs by making the appropriate combination of input and output
    #declarations, and then making the appropriate HIGH / LOW settings on the output pins.
    def light_led(self, Lid, Ldur):  # Lys opp ett lys
        for pin_index, pin_state in enumerate(self.pin_led_states[Lid]):
            self.set_pin(pin_index, pin_state)
        self.turn_on_led(Lid)
        print("Lights led", Lid, "for", Ldur, "sekunder")
        time.sleep(Ldur)
        self.shut_off_lights()

    def light_all(self, Ldur):  # Skru på alle lys
        timeout = time.time() + Ldur
        while time.time() <= timeout:
            for i in range(1, 7):
                self.turn_on_led(i)
        self.shut_off_lights()

    def flash_all_leds(self, flashes=5, dif=0.25):  # Flash alle lys
        print("All leds flashing")
        for i in range(0, flashes):
            self.light_all(dif)
            time.sleep(dif)

    def twinkle_all_leds(self, Ldur):  # Twinkle lys
        timeout = time.time() + Ldur
        print("All leds twinkle")
        while time.time() <= timeout:
            for i in range(1, 7):
                self.light_led(i, 0.2)
        self.shut_off_lights()

    def startup_leds(self):  # Start opp
        for i in range(1, 7):
            self.light_led(i, 0.2)
        self.flash_all_leds(3, 0.1)
        print("Power up animation")

    def rightPassword_leds(self):  # !Right pass
        for i in range(1, 7):
            self.light_led(i, 0.1)
        print("Tried password animation")

    def exit_leds(self):  # Slå av
        self.flash_all_leds(3, 0.1)
        for i in range(1, 7):
            self.light_led(i, 0.2)
        print("Power down animation")




















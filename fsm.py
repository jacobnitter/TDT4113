import time
import RPi.GPIO as GPIO


class rules:

    def __init__(self, state1, state2, signal, action):
        self.state1 = state1
        self.state2 = state2
        self.signal = signal
        self.action = action


def signal_is_digit(signal):
    return 48 <= ord(signal) <= 57


class Keypad:

    rows = [18, 23, 24, 25]
    columns = [17, 27, 22]
    symbols = {
        'nokey': 'No Key',
        '1817': 1,
        '1827': 2,
        '1822': 3,
        '2317': 4,
        '2327': 5,
        '2322': 6,
        '2417': 7,
        '2427': 8,
        '2422': 9,
        '2517': '*',
        '2527': 0,
        '2522': '#'}

    def __init__(self):
        """Starter"""

        GPIO.setmode(GPIO.BCM)

        for row in self.rows:
            GPIO.setup(row, GPIO.OUT)

        for col in self.columns:
            GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def do_polling(self):

        """finner key"""

        match = False
        keystring = 'nokey'

        for row in self.rows:
            GPIO.output(row, GPIO.HIGH)

            for col in self.columns:
                if GPIO.input(col) == GPIO.HIGH:
                    Test = True
                    keystring = str(row) + str(col)

            if match:
                break

            GPIO.output(row, GPIO.LOW)

        return self.symbols[keystring]

    def get_next_signal(self):

        """finner neste signal"""

        count = 0
        prevkey = 'start'
        key = None

        while count < 1:
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
        time.sleep(4)
        print('keypad key =', key)
        return key


class Ledboard:
    """leadboard-klasse"""
    def __init__(self):  # Set the proper mode via: GPIO.setmode(GPIO.BCM).
        # Set the proper mode via: GPIO.setmode(GPIO.BCM).
        self.pins = [13, 19, 26]
        self.pin_led_states = [
            [1, 0, -1],  # 1
            [0, 1, -1],  # 2
            [1, -1, 0],  # 3
            [0, -1, 1],  # 4
            [-1, 1, 0],  # 5
            [-1, 0, 1],  # 6
            [-1, -1, -1]
        ]
        GPIO.setmode(GPIO.BCM)

    def set_pin(self, pin_index, pin_state):
        """setter pins"""

        if pin_state == -1:
            GPIO.setup(self.pins[pin_index], GPIO.IN)
        else:
            GPIO.setup(self.pins[pin_index], GPIO.OUT)
            GPIO.output(self.pins[pin_index], pin_state)

    def turn_on_led(self, Lid):  # Skru på lys
        for pin_index, pin_state in enumerate(self.pin_led_states[Lid - 1]):
            self.set_pin(pin_index, pin_state)

    def shut_off_lights(self):  # Skru av lys
        for i in range(0, 3):
            self.set_pin(i, 0)

    # Turn on one of the 6 LEDs by making the appropriate combination of input and output
    # declarations, and then making the appropriate HIGH / LOW settings on the
    # output pins.
    def light_led(self, Lid, Ldur):  # Lys opp ett lys
        for pin_index, pin_state in enumerate(self.pin_led_states[Lid]):
            self.set_pin(pin_index, pin_state)
        self.turn_on_led(Lid)
        print("Lights led", Lid, "for", Ldur, "sekunder")
        time.sleep(Ldur)
        self.shut_off_lights()

    def light_all(self, Led_duration):  # Skru på alle lys
        timeout = time.time() + Led_duration
        while time.time() <= timeout:
            for i in range(1, 7):
                self.turn_on_led(i)
        self.shut_off_lights()

    def flash_all_leds(self, flashes=5, dif=0.25):  # Flash alle lys
        print("All leds flashing")
        for i in range(0, flashes):
            self.light_all(dif)
            time.sleep(dif)

    def twinkle_all_leds(self, Led_duration):  # Twinkle lys
        timeout = time.time() + Led_duration
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


class FSM:
    def __init__(self, agent):
        self.rules = []
        self.agent = agent
        self.currentState = None

    def add_rule(self, rule):
        self.rules.append(rule)

    def get_next_signal(self):  # query the agent for the next signal
        """får neste signal"""
        return self.agent.get_next_signal()

    # go through the rule set, in order, applying each rule until one of the rules is fired.
    # finne regelen som stemmer?
    def run_rules(self, input):
        """går over alle regler"""
        for i in range(len(self.rules)):
            if self.apply_rule(self.rules[i], input):
                break  # Slutt å lete gjennom regler

    # check whether the conditions of a rule are met.
    def apply_rule(self, rule, input):
        """bruker rule"""
        if self.currentState == rule.state1 and (input in rule.signal):
            self.fire_rule(rule, input)
            return True
        return False

    # use the consequent of a rule to a) set the next state of the FSM, and b)
    # call the appropriate agent action method.
    def fire_rule(self, rule, input):
        """kjører en rule"""
        self.currentState = rule.state2
        rule.action()

    # begin in the FSM’s default initial state and then repeatedly call get
    # next signal and run rules until the FSM enters its default final state.
    def main_loop(self):
        """metode som ikke brukes"""
        pass


class Agent:
    """agent-klasse"""
    def __init__(self, keypad, led_board, pathname):
        self.keypad = keypad  # a pointer to the keypad
        self.led_board = led_board  # pointer to the LED Board
        self.temp_password = ""
        self.pathname = pathname  # pathname to the file holding the KPC’s password
        self.override_signal = None
        self.led_id = ""  # slots for holding the LED id
        self.led_time = ""
        self.signal = ""

    def null_action(self):  # Resetter agenten (?) og passord(?)
        """metode som ikke gjør noe"""
        pass

    # Return the override-signal, if it is non-blank; otherwise query the
    # keypad for the next pressed key.
    def get_next_signal(self):
        """får neste signal"""
        if self.override_signal is not None:
            temp = self.override_signal
            self.override_signal = None
            print("Inne i override")
            return temp
        self.signal = self.keypad.get_next_signal()
        print("Input:", self.signal)
        return self.signal

    def verify_login(self):  # lese filen og sjekke om passordet stemmer
        """sjekker pasasorc"""
        file = open(self.pathname, "r")
        password = file.read()  # leser inn filen og oppretter en streng med ordene
        print("Passord =", password)
        file.close()
        print("Temp_passord =", self.temp_password)
        if password == self.temp_password:  # sjekker om passordet lagret i filen er lik passordet tastet inn
            self.override_signal = 'True'
            return True
        self.override_signal = 'False'
        return False

    def validate_passcode_change(self, password):
        """sjekker passord"""
        if password.isdigit() and len(password) > 3:
            return True
        return False

    def startup(self):  # Få lys til å blinke og reset password
        """startup"""
        self.clear_password()
        self.led_board.startup_leds()

    def login(self):  # Twinkle lights og verify login
        """logger inn"""
        self.verify_login()
        self.led_board.rightPassword_leds()

    def exit_action(self):
        """exit action"""
        self.led_board.exit_leds()

    # PASSORD
    def init_passcode_entry(self):
        """init"""
        self.passcode_buffer = []
        self.led_board.light_led()

    def add_symbol_password(self):
        """legger til symbol til passord"""
        print("get", self.signal)
        if self.signal == '*' or self.signal == '#':
            print("* eller #")
            pass
        else:
            # Legg til det vi skriver inn i keypaden
            self.temp_password += str(self.signal)
            print("temp_password =", self.temp_password)

    def clear_password(self):
        """fjerner gammelt passord"""
        self.temp_password = ""

    def cach_password(self):
        """lagrer mulig nytt passord"""
        if self.validate_passcode_change(self.temp_password):
            f = open(self.pathname, "w")
            f.write(self.temp_password)
            f.close()
            self.flash_leds()  # If password changed
        self.twinkle_leds()  # If fail
        self.reset_led()

    # LYS
    def set_led_id(self):  # ENDRE
        """setter id til led"""
        self.led_id = self.signal  # Setter id til det vi har trykket på keypaden

    def set_led_time(self):  # ENDRE
        """Endred tid"""
        print("ledtime:", self.led_time)
        print("signal:", self.signal)
        # Legger til taller vi har skrevet inn i ledd helt til vi trykker *
        self.led_time += str(self.signal)

    def reset_led(self):
        """resetter led"""
        print("Led_ligth is reset")
        self.led_time = ""

    def light_one_led(self):
        """slår påå en led"""
        self.led_board.light_led(int(self.led_id), int(self.led_time))

    def flash_leds(self):
        """flasher led"""
        self.led_board.flash_all_leds(1)

    def twinkle_leds(self):
        """Twinkler led"""
        self.led_board.twinkle_all_leds(1)


class Makerules(FSM):
    """Klassen som lagre regler"""
    def __init__(self, agent):
        FSM.__init__(self, agent)
        all_input = [
            '0',
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            '*',
            '#']
        all_num_input = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        num_input = ['6', '7', '8', '9']
        number_input = ['0', '1', '2', '3', '4', '5']
        input = ""

        # REGLER LOGG PÅ
        self.add_rule(
            rules(
                "s-init",
                "s-read",
                all_input,
                self.agent.startup))  # Starter opp og lys lyser
        # Sjekker passord og får lys til å lyse
        self.add_rule(rules("s-read", "s-verify", ['*'], self.agent.login))
        self.add_rule(
            rules(
                "s-read",
                "s-init",
                ['#'],
                self.agent.null_action))  # Resetter agent
        self.add_rule(
            rules(
                "s-read",
                "s-read",
                all_num_input,
                self.agent.add_symbol_password))  # Legger til et tall (input) i temp-passord
        # Hvis ikke passord er rett resettes agent og vi går tilbake til start
        self.add_rule(
            rules(
                "s-verify",
                "s-init",
                ['False'],
                self.agent.null_action))
        # Hvis passord er rett går vi videre til active og aktiverer agent
        self.add_rule(
            rules(
                "s-verify",
                "s-active",
                ['True'],
                self.agent.null_action))

        # REGLER ENDRE PASSORD
        self.add_rule(
            rules(
                "s-active",
                "s-read-2",
                ['*'],
                self.agent.clear_password))  # Starter å resette passord
        # Hvis ikke går vi tilbake til active
        self.add_rule(
            rules(
                "s-read-2",
                "s-active",
                ['#'],
                self.agent.null_action))
        self.add_rule(
            rules(
                "s-read-2",
                "s-read-2",
                all_num_input,
                self.agent.add_symbol_password))  # Skriver inn tall som blir en del av nytt passord
        self.add_rule(
            rules(
                "s-read-2",
                "s-active",
                ['*'],
                self.agent.cach_password))  # Cacher det nye passordet

        # REGLER LOGG AV
        # Skriver # blir det lysshow og vi logger av, går tilbake
        self.add_rule(
            rules(
                "s-active",
                "s-init",
                ['#'],
                self.agent.exit_action))

        # REGLER STYRE LYS
        # Skriver inn et tall og kan gjøre denne mange ganger
        self.add_rule(
            rules(
                "s-active",
                "s-ledligth",
                number_input,
                self.agent.set_led_id))
        # Hvis vi trykker på 6 .. 9, * og # skal være lov
        self.add_rule(
            rules(
                "s-active",
                "s-active",
                num_input,
                self.agent.null_action))
        self.add_rule(
            rules(
                "s-ledligth",
                "s-ledligth",
                all_num_input,
                self.agent.set_led_time))
        self.add_rule(
            rules(
                "s-ledligth",
                "s-almost_done",
                ['*'],
                self.agent.light_one_led))  # Lyser rett led lys
        self.add_rule(
            rules(
                "s-almost_done",
                "s-active",
                all_input,
                self.agent.reset_led))  # Tilbake til active

        # begin in the FSM’s default initial state and then repeatedly call get
        # next signal and run rules until the FSM enters its default final
        # state.

    def main_loop(self):
        """kjører koden"""
        self.currentState = "s-init"
        while True:  # not self.agent.exit:
            print("Ny knapp trykket")
            print("State: ", self.currentState)
            input = str(self.agent.get_next_signal())
            self.run_rules(input)

            if self.currentState == "s-active" and input == '#':
                print("Ferdig")
                break


if __name__ == "__main__":
    print("Kjorer")
    KEY_PAD = Keypad()
    LED_BOARD = Ledboard()

    AGENT = Agent(KEY_PAD, LED_BOARD, "password.txt")
    FSM = Makerules(AGENT)
    FSM.main_loop()

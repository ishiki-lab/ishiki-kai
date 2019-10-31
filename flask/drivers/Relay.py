# No idea what type of relay it is but presuming it's the 'Dual Relay Bricklet'
# https://www.tinkerforge.com/en/doc/Software/Bricklets/DualRelay_Bricklet_Python.html
# ...simple enough

class Relay:
    def __init__(self):
        print("A relay object exists...")

    def on(self):
        print("Relay on!")

    def off(self):
        print("Relay off!")

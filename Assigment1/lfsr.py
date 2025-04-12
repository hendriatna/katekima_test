class LFSR:
    def __init__(self, size=4, state=None, taps=None):
        self.size = size
        self.initial_state = state if state is not None else [1] * size
        self.state = self.initial_state[:]
        self.taps = taps if taps is not None else [0, 1]  # default taps

    def set_size(self, size):
        self.size = size
        self.initial_state = [1] * size
        self.state = self.initial_state[:]

    def get_size(self):
        return self.size

    def set_state(self, state):
        if len(state) != self.size:
            raise ValueError("State length must match LFSR size.")
        self.state = state[:]
        self.initial_state = state[:]

    def get_state(self):
        return self.state[:]

    def set_taps(self, taps):
        if any(t >= self.size for t in taps):
            raise ValueError("Tap index exceeds register size.")
        self.taps = taps

    def get_taps(self):
        return self.taps

    def reset(self):
        self.state = self.initial_state[:]

    def next_bit(self):
        # XOR the tap bits
        feedback = 0
        for t in self.taps:
            feedback ^= self.state[t]
        # Shift right and insert feedback bit at the front (MSB)
        out_bit = self.state[-1]
        self.state = [feedback] + self.state[:-1]

        return out_bit

# basic lfsr function
def basic_lfsr(size=4, state=None, taps=[0, 1], steps=10):
    #if state exiist, copy state or make array with size and value 1
    #ex: if size 5 > [1, 1, 1, 1, 1]
    reg = state[:] if state else [1] * size
    output = []

    for _ in range(steps):
        #print array req and convert to string
        print(f"State: {''.join(map(str, reg))}", end=', ')
        feedback = 0
        for t in taps:
            # 0 XOR reg in position taps, and set to feedback
            feedback ^= reg[t]
        #set last array to out_bit
        out_bit = reg[-1]
        #add out_bit to output array
        output.append(out_bit)
        #insert feedback in front of array, and delete last array
        reg = [feedback] + reg[:-1]

        print(f"Output: {out_bit}")

    return output


# start the run file
if __name__ == "__main__":
    size = 4
    taps = [0, 3]
    init_state = [0, 1, 1, 0]
    steps = 20

    # initiate general LFSR
    lfsr = LFSR(size=size, state=init_state, taps=taps)

    # Compare outputs
    print("Expected (basic LFSR):")
    expected = basic_lfsr(size=size, state=init_state, taps=taps, steps=steps)
    print(expected)

    print("Actual (general LFSR):")
    actual = []
    for _ in range(steps):
        print(f"State: {''.join(map(str, lfsr.get_state()))}", end=', ')
        bit = lfsr.next_bit()
        actual.append(bit)
        print(f"Output: {bit}")
    print(actual)

    assert actual == expected, "Mismatch between general and basic LFSR!"
    print("✅ Output matched!")

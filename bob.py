from cryptography.fernet import Fernet
import random
import json

class Gate(object):

    def __init__(self, circuit, g_id, gate_json):
        self.circuit = circuit
        self.g_id = g_id
        self.inputs = gate_json["inputs"]
        self.table = gate_json["table"] # the garbled output table

        self.output = None

    def grab_inputs(self):
        return [self.circuit.gates[g].fire() for g in self.inputs]

    def fire(self):
        if self.output is None:
            keys = self.grab_inputs()

            fs = [Fernet(keys[1]), Fernet(keys[0])]

            decrypt_table = self.table
            for f in fs:
                new_table = []
                for ciphertext in decrypt_table:
                    dec = None
                    try:
                        dec = f.decrypt(ciphertext)
                    except:
                        pass
                    if dec is not None:
                        new_table.append(dec)
                decrypt_table = new_table

            if len(decrypt_table) != 1:
                raise ValueError("decrypt_table should be length 1 after decrypting")

            self.output = decrypt_table[0]

        return self.output

class OnInputGate(Gate):
    def __init__(self, circuit, g_id, gate_json):
        Gate.__init__(self, circuit, g_id, gate_json)

    def grab_inputs(self):
        return [self.circuit.inputs[i] for i in self.inputs]

class Circuit(object):
    def __init__(self, circuit_json):
        self.num_inputs = circuit_json["num_inputs"]
        self.gates = {}

        for g_id, g in circuit_json["on_input_gates"].items():
            self.gates[g_id] = OnInputGate(self, g_id, g)

        for g_id, g in circuit_json["gates"].items():
            self.gates[g_id] = Gate(self, g_id, g)

        self.output_gate_ids = circuit_json["output_gate_ids"]

    def fire(self, inputs):
        self.inputs = inputs
        output = {}
        for g_id in self.output_gate_ids:
            output[g_id] = self.gates[g_id].fire()
        return output


with open('circuit.json') as data_file:    
    data = json.load(data_file)
    
mycirc = Circuit(data)

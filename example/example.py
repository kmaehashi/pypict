import os


# CAPI
import pypict.capi  # NOQA

output = pypict.capi.execute(
    [os.path.dirname(os.path.realpath(__file__)) + '/example.model', '/o:2'])
print('Pair-wise cases using CAPI:')
print(output)
print()


# High-level API
import pypict.api  # NOQA

task = pypict.api.Task()
task.model.add_parameter(2)
task.model.add_parameter(3)
print('Pair-wise cases using high-level API:')
print(list(task.generate()))
print()


# Comamnd API
import pypict.cmd  # NOQA

out = pypict.cmd.from_model('''
X: 1, 2
Y: 3, 4
''')
print('Pair-wise cases using Command API:')
print(out)

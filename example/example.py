import os


###
### CAPI
###
import pypict.capi

task = pypict.capi.createTask()
print('Task handle', task)
pypict.capi.deleteTask(task)
print()

output = pypict.capi.execute(
    [os.path.dirname(os.path.realpath(__name__)) + '/example.model', '/o:2'])
print('Pair-wise cases using CAPI:')
print(output)
print()


###
### High-level API
###
import pypict.api

task = pypict.api.Task()
task.model.add_parameter(2)
task.model.add_parameter(3)
print('Pair-wise cases using high-level API:')
print(list(task.generate()))
print()


###
### Comamnd API
###
import pypict.cmd

out = pypict.cmd.from_model('''
X: 1, 2
Y: 3, 4
''')
print('Pair-wise cases using Command API')
print(out)

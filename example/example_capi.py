from pypict import capi


task = capi.createTask()
print('Task handle:', task)
model = capi.createModel()
print('Model handle:', model)
capi.setRootModel(task, model)

p1 = capi.addParameter(model, 2, 2, (1, 1))
print('Param 1 handle:', p1)
p2 = capi.addParameter(model, 3, 2, (2, 1, 1))
print('Param 2 handle:', p2)
print('Parameter count:', capi.getTotalParameterCount(task))

print('Exclude [0, 2]')
capi.addExclusion(task, ((p1, 0), (p2, 2)))
print('Exclude [1, 0]')
capi.addExclusion(task, ((p1, 1), (p2, 0)))

capi.addSeed(task, ((p1, 0), (p2, 0)))
capi.generate(task)
capi.resetResultFetching(task)
row = capi.allocateResultBuffer(task)
print('Result Buffer:', row)

while True:
    remaining_rows = capi.getNextResultRow(task, row)
    if remaining_rows == 0:
        break
    print('Result Row:', list(row))

print('Cleaning up...')
capi.freeResultBuffer(row)
capi.deleteTask(task)
capi.deleteModel(model)

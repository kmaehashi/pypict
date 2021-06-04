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

capi.addSeed(task, ((p1, 0), (p2, 0)))
capi.generate(task)
capi.resetResultFetching(task)
row = capi.allocateResultBuffer(task)
print('Result Buffer:', row)

while True:
    remaining_rows = capi.getNextResultRow(task, row)
    print('Result Row:', list(row))
    if remaining_rows == 1:
        break

print('Cleaning up...')
capi.freeResultBuffer(row)
capi.deleteTask(task)
capi.deleteModel(model)

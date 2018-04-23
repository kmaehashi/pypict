import unittest

from pypict import capi


class TestCAPI(unittest.TestCase):
    def test_createTask_deleteTask(self):
        task = capi.createTask()
        self.assertNotEqual(0, task)
        capi.deleteTask(task)

    def test_createModel_deleteModel(self):
        model = capi.createModel()
        self.assertNotEqual(0, model)
        capi.deleteModel(model)

    def test_setRootModel(self):
        task = capi.createTask()
        model = capi.createModel()
        capi.setRootModel(task, model)
        capi.deleteTask(task)
        capi.deleteModel(model)

    def test_addParameter_getTotalParameterCount(self):
        task = capi.createTask()
        model = capi.createModel()
        capi.setRootModel(task, model)
        self.assertEqual(0, capi.getTotalParameterCount(task))
        capi.addParameter(model, 2)
        self.assertEqual(1, capi.getTotalParameterCount(task))
        capi.addParameter(model, 4, order=3)
        self.assertEqual(2, capi.getTotalParameterCount(task))
        capi.addParameter(model, 3, order=2, valueWeights=(5, 1, 1))
        self.assertEqual(3, capi.getTotalParameterCount(task))
        capi.deleteTask(task)
        capi.deleteModel(model)

    def test_attachChildModel(self):
        model1 = capi.createModel()
        model2 = capi.createModel()
        model3 = capi.createModel()
        capi.attachChildModel(model1, model2)
        capi.attachChildModel(model1, model3, 3)

        # Children (model2 and model3) are deleted altogether.
        capi.deleteModel(model1)
        #capi.deleteModel(model2)
        #capi.deleteModel(model3)

    def test_usecase_simple(self):
        task = capi.createTask()
        model = capi.createModel()
        capi.setRootModel(task, model)
        p1 = capi.addParameter(model, 2, 2, (1, 1))  # axis-X
        p2 = capi.addParameter(model, 3, 2, (2, 1, 1))  # axis-Y
        paramCount = capi.getTotalParameterCount(task)
        self.assertEqual(2, paramCount)

        capi.addExclusion(task, ((p1, 0), (p2, 2)))
        capi.addExclusion(task, ((p1, 1), (p2, 0)))

        capi.addSeed(task, ((p1, 0), (p2, 0)))

        capi.generate(task)
        capi.resetResultFetching(task)

        row = capi.allocateResultBuffer(task)
        self.assertNotEqual(0, row)

        fullRows = ['0,0', '0,1', '0,2', '1,0', '1,1', '1,2']
        excludedRows = ['0,2', '1,0']
        expectedRows = set(fullRows) - set(excludedRows)
        actualRows = []
        rowsRemaining = len(expectedRows)
        while True:
            self.assertEqual(rowsRemaining, capi.getNextResultRow(task, row))
            if rowsRemaining == 0:
                break
            actualRows.append(','.join([str(x) for x in row]))
            rowsRemaining -= 1
        self.assertEqual(sorted(expectedRows), sorted(actualRows))

        capi.freeResultBuffer(row)
        capi.deleteTask(task)
        capi.deleteModel(model)

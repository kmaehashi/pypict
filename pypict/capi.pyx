# distutils: language = c++

"""
Python wrapper for PICT C/API.
"""

from libc.stdlib cimport malloc, free
from libc.stddef cimport wchar_t
from libc.stdint cimport uint32_t
from cpython.mem cimport PyMem_Free


cdef extern from "<string>" namespace "std":
    cdef cppclass wstring:
        wstring()
        wchar_t* data()


cdef extern from "Python.h":
    wchar_t* PyUnicode_AsWideCharString(object, Py_ssize_t*)
    object PyUnicode_FromWideChar(wchar_t*, Py_ssize_t)


cdef extern from "pictapi.h":

    ##
    ## Types
    ##

    ctypedef void *       PICT_HANDLE;
    ctypedef size_t       PICT_VALUE;
    ctypedef size_t *     PICT_RESULT_ROW;
    ctypedef unsigned int PICT_RET_CODE;

    ctypedef struct PICT_EXCLUSION_ITEM:
        PICT_HANDLE Parameter
        PICT_VALUE ValueIndex

    ctypedef struct PICT_SEED_ITEM:
        PICT_HANDLE Parameter
        PICT_VALUE ValueIndex

    ##
    ## Return codes
    ##

    int PICT_SUCCESS
    int PICT_OUT_OF_MEMORY
    int PICT_GENERATION_ERROR

    ##
    ## Defaults
    ##

    int PICT_PAIRWISE_GENERATION
    int PICT_DEFAULT_RANDOM_SEED

    ##
    ## Interface
    ##

    PICT_HANDLE PictCreateTask()

    void PictSetRootModel(
        const PICT_HANDLE task,
        const PICT_HANDLE model)

    PICT_RET_CODE PictAddExclusion(
        const PICT_HANDLE task,
        const PICT_EXCLUSION_ITEM exlusionItems[],
        size_t exclusionItemCount)

    PICT_RET_CODE PictAddSeed(
        const PICT_HANDLE task,
        const PICT_SEED_ITEM seedItems[],
        size_t seedItemCount)

    PICT_RET_CODE PictGenerate(
        const PICT_HANDLE task)

    PICT_RESULT_ROW PictAllocateResultBuffer(
        const PICT_HANDLE task)

    void PictFreeResultBuffer(
        const PICT_RESULT_ROW resultRow)

    void PictResetResultFetching(
        const PICT_HANDLE task)

    size_t PictGetNextResultRow(
        const PICT_HANDLE task,
        PICT_RESULT_ROW resultRow)

    void PictDeleteTask(
        const PICT_HANDLE task)

    PICT_HANDLE PictCreateModel(
        unsigned int randomSeed)

    PICT_HANDLE PictAddParameter(
        const PICT_HANDLE model,
        size_t valueCount,
        unsigned int order,
        unsigned int valueWeights[])

    size_t PictGetTotalParameterCount(
        const PICT_HANDLE task)

    PICT_RET_CODE PictAttachChildModel(
        const PICT_HANDLE modelParent,
        const PICT_HANDLE modelChild,
        unsigned int order)

    void PictDeleteModel(
        const PICT_HANDLE model)


cdef extern from "pypict_pict_clidll.h":
    int PictExecuteCLI "execute" (int argc, wchar_t* args[], wstring& output)


##################################################
# Constants
##################################################


PAIRWISE_GENERATION = PICT_PAIRWISE_GENERATION
DEFAULT_RANDOM_SEED = PICT_DEFAULT_RANDOM_SEED


##################################################
# Error Handling
##################################################


cdef void check_retcode(PICT_RET_CODE code) except *:
    if code == PICT_SUCCESS:
        return
    elif code == PICT_OUT_OF_MEMORY:
        raise MemoryError()
    elif code == PICT_GENERATION_ERROR:
        raise RuntimeError('internal engine error')
    raise RuntimeError('unexpected error ({})'.format(code))


##################################################
# Interface (API)
##################################################


cpdef size_t createTask() except *:
    """createTask() -> int"""
    handle = PictCreateTask()
    if handle == NULL:
        raise MemoryError()
    return <size_t>handle


cpdef void setRootModel(task: size_t, model: size_t) except *:
    """setRootModel(task: int, model: int) -> None"""
    PictSetRootModel(<PICT_HANDLE>task, <PICT_HANDLE>model)


cpdef void addExclusion(task: size_t, items: tuple) except *:
    """addExclusion(task: int, items: Iterable[tuple[int, int]]) -> None"""
    cdef size_t count = len(items)
    cdef PICT_EXCLUSION_ITEM* packed = NULL
    if count == 0:
        return
    packed = <PICT_EXCLUSION_ITEM*>malloc(sizeof(PICT_EXCLUSION_ITEM) * count)
    if packed == NULL:
        raise MemoryError()
    try:
        for i, (param, idx) in enumerate(items):
            packed[i].Parameter = <PICT_HANDLE><size_t>param
            packed[i].ValueIndex = <PICT_VALUE>idx
        check_retcode(PictAddExclusion(<PICT_HANDLE>task, packed, count))
    finally:
        free(packed)


cpdef void addSeed(task: size_t, items: tuple) except *:
    """addSeed(task: int, items: Iterable[tuple[int, int]]) -> None"""
    cdef size_t count = len(items)
    cdef PICT_SEED_ITEM* packed = NULL
    if count == 0:
        return
    packed = <PICT_SEED_ITEM*>malloc(sizeof(PICT_SEED_ITEM) * count)
    if packed == NULL:
        raise MemoryError()
    try:
        for i, (param, idx) in enumerate(items):
            packed[i].Parameter = <PICT_HANDLE><size_t>param
            packed[i].ValueIndex = <PICT_VALUE>idx
        check_retcode(PictAddSeed(<PICT_HANDLE>task, packed, count))
    finally:
        free(packed)


cpdef void generate(task: size_t) except *:
    """generate(task: int) -> None"""
    check_retcode(PictGenerate(<PICT_HANDLE>task))


cpdef size_t[:] allocateResultBuffer(task: size_t) except *:
    """allocateResultBuffer(task: int) -> memoryview"""
    cdef size_t paramCount = PictGetTotalParameterCount(<PICT_HANDLE>task)
    buf = PictAllocateResultBuffer(<PICT_HANDLE>task)
    if buf == NULL:
        raise MemoryError()
    return <size_t[:paramCount]>buf


cpdef void freeResultBuffer(resultRow: size_t[:]) except *:
    """freeResultBuffer(resultRow: memoryview) -> None"""
    PictFreeResultBuffer(<PICT_RESULT_ROW>&resultRow[0])


cpdef void resetResultFetching(task: size_t) except *:
    """resetResultFetching(task: int) -> None"""
    PictResetResultFetching(<PICT_HANDLE>task)


cpdef size_t getNextResultRow(task: size_t, resultRow: size_t[:]) except *:
    """getNextResultRow(task: int, resultRow: memoryview) -> int"""
    return PictGetNextResultRow(
        <PICT_HANDLE>task, <PICT_RESULT_ROW>&resultRow[0])


cpdef void deleteTask(task: size_t) except *:
    """deleteTask(task: int) -> None"""
    PictDeleteTask(<PICT_HANDLE>task)


cpdef size_t createModel(
        randomSeed: uint32_t = PICT_DEFAULT_RANDOM_SEED) except *:
    """createModel(randomSeed: int = PICT_DEFAULT_RANDOM_SEED) -> int"""
    handle = PictCreateModel(randomSeed)
    if handle == NULL:
        raise MemoryError()
    return <size_t>handle


cpdef size_t addParameter(
        model: size_t,
        valueCount: size_t,
        order: uint32_t = PICT_PAIRWISE_GENERATION,
        valueWeights: tuple = None) except *:
    """addParameter(model: int, valueCount: int, order: int = PICT_PAIRWISE_GENERATION, valueWeights: Optional[Iterable[int]] = None) -> int"""
    cdef unsigned int* packed = NULL
    try:
        if valueWeights is not None:
            assert valueCount == <size_t>len(valueWeights)
            packed = <unsigned int*>malloc(sizeof(unsigned int) * valueCount)
            if packed == NULL:
                raise MemoryError()
            for i, weight in enumerate(valueWeights):
                packed[i] = <unsigned int>weight
        handle = PictAddParameter(
            <PICT_HANDLE>model, valueCount, order, packed)
        if handle == NULL:
            raise MemoryError()
        return <size_t>handle
    finally:
        free(packed)


cpdef size_t getTotalParameterCount(task: size_t) except *:
    """getTotalParameterCount(task: int) -> int"""
    return <size_t>PictGetTotalParameterCount(<PICT_HANDLE>task)


cpdef void attachChildModel(
        modelParent: size_t,
        modelChild: size_t,
        order: uint32_t = PICT_PAIRWISE_GENERATION) except *:
    """attachChildModel(modelParent: int, modelChild: int, order: int = PICT_PAIRWISE_GENERATION) -> None"""
    check_retcode(PictAttachChildModel(
        <PICT_HANDLE>modelParent, <PICT_HANDLE>modelChild, order))


cpdef void deleteModel(model: size_t) except *:
    """deleteModel(model: int) -> None"""
    PictDeleteModel(<PICT_HANDLE>model)


##################################################
# Interface (CLI)
##################################################

cpdef str execute(args: list):
    """execute(args: list[str]) -> str"""
    cdef int c_argc = -1
    cdef wchar_t** c_args = NULL
    cdef wstring c_output

    c_argc = len(args) + 1
    c_args = <wchar_t**>malloc(sizeof(wchar_t*) * c_argc)
    if c_args == NULL:
        raise MemoryError()
    try:
        c_args[0] = PyUnicode_AsWideCharString("", NULL)
        for i in range(1, c_argc):
            c_args[i] = PyUnicode_AsWideCharString(args[i-1], NULL)
        PictExecuteCLI(c_argc, c_args, c_output)
        return PyUnicode_FromWideChar(c_output.data(), -1)
    finally:
        for i in range(c_argc):
            PyMem_Free(c_args[i])
        free(c_args)

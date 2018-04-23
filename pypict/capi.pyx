# distutils: language = c++

"""
Python wrapper for PICT C/API.
"""

from libc.stdlib cimport malloc, free


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


##################################################
# Constants
##################################################


PAIRWISE_GENERATION = PICT_PAIRWISE_GENERATION
DEFAULT_RANDOM_SEED = PICT_DEFAULT_RANDOM_SEED


##################################################
# Error Handling
##################################################


cdef void check_retcode(PICT_RET_CODE code):
    if code == PICT_SUCCESS:
        return
    elif code == PICT_OUT_OF_MEMORY:
        raise MemoryError()
    elif code == PICT_GENERATION_ERROR:
        raise RuntimeError('internal engine error')
    raise RuntimeError('unexpected error ({})'.format(code))


##################################################
# Interface
##################################################


cpdef size_t createTask():
    handle = PictCreateTask()
    if handle == NULL:
        raise MemoryError()
    return <size_t>handle


cpdef void setRootModel(size_t task, size_t model):
    PictSetRootModel(<PICT_HANDLE>task, <PICT_HANDLE>model)


cpdef void addExclusion(size_t task, list items):
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


cpdef void addSeed(size_t task, list items):
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


cpdef void generate(size_t task):
    check_retcode(PictGenerate(<PICT_HANDLE>task))


cpdef size_t[:] allocateResultBuffer(size_t task):
    cdef size_t paramCount = PictGetTotalParameterCount(<PICT_HANDLE>task)
    buf = PictAllocateResultBuffer(<PICT_HANDLE>task)
    if buf == NULL:
        raise MemoryError()
    return <size_t[:paramCount]>buf


cpdef void freeResultBuffer(size_t[:] resultRow):
    PictFreeResultBuffer(<PICT_RESULT_ROW>&resultRow[0])


cpdef void resetResultFetching(size_t task):
    PictResetResultFetching(<PICT_HANDLE>task)


cpdef size_t getNextResultRow(size_t task, size_t[:] resultRow):
    return PictGetNextResultRow(
        <PICT_HANDLE>task, <PICT_RESULT_ROW>&resultRow[0])


cpdef void deleteTask(size_t task):
    PictDeleteTask(<PICT_HANDLE>task)


cpdef size_t createModel(unsigned int randomSeed = PICT_DEFAULT_RANDOM_SEED):
    handle = PictCreateModel(randomSeed)
    if handle == NULL:
        raise MemoryError()
    return <size_t>handle


cpdef size_t addParameter(
        size_t model,
        size_t valueCount,
        unsigned int order = PICT_PAIRWISE_GENERATION,
        list valueWeights = None):
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


cpdef size_t getTotalParameterCount(size_t task):
    return <size_t>PictGetTotalParameterCount(<PICT_HANDLE>task)


cpdef void attachChildModel(
        size_t modelParent,
        size_t modelChild,
        unsigned int order = PICT_PAIRWISE_GENERATION):
    check_retcode(PictAttachChildModel(
        <PICT_HANDLE>modelParent, <PICT_HANDLE>modelChild, order))


cpdef void deleteModel(size_t model):
    PictDeleteModel(<PICT_HANDLE>model)

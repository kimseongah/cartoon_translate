def array_to_dictionary(array):
    ret = {}
    
    for idx, val in enumerate(array):
        ret[idx] = val
    
    return ret
def dupfiles_count(input_dict):
    count = 0
    for val in input_dict.values():
        count += len(val)
    return count

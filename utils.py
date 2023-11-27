def convert_nums_to_int_list(nums):
    """"""

    answer_as_string_list = list(str(nums))
    answer_as_int_list = [int(s) for s in answer_as_string_list]

    return answer_as_int_list

def convert_str_list_to_num(list):
    """"""

    combined_nums = int("".join(list))

    return combined_nums

def convert_int_list_to_num(list):
    """"""
    breakpoint()
    as_strings = [str(int) for int in list]
    combined_nums = int("".join(as_strings))

    return combined_nums
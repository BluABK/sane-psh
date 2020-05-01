

def list_item_types_equal(li: list, t: type):
    for item in li:
        if type(item) is not t:
            return False

    return True


def pp_dict(d, indent_lvl=0, indent_str='    ', suffix_last_item=None):
    for key in d:
        if type(d[key]) is dict:
            print("{key}: ".format(key=repr(key)))
            pp_dict(d[key], indent_lvl=indent_lvl + 1)
        else:
            # Handle dicts within lists.
            if type(d[key]) is list and list_item_types_equal(d[key], dict):
                print("{key}: [".format(key=repr(key)))
                for item in d[key]:
                    pp_dict(item, indent_lvl=indent_lvl + 1, suffix_last_item=',')
                # Indent list close bracket to match indented list items (i.e. thus the +1).
                print("{indent}]".format(indent=(indent_lvl + 1) * indent_str))
            else:
                if key == list(d.keys())[-1] and suffix_last_item is not None:
                    print("{indent}{key}: {value}{suffix}".format(indent=indent_lvl * indent_str, key=repr(key),
                                                                  value=repr(d[key]), suffix=suffix_last_item))
                else:
                    print("{indent}{key}: {value}".format(indent=indent_lvl * indent_str, key=repr(key),
                                                          value=repr(d[key])))

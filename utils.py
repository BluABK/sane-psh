def pp_dict(d, indent_lvl=0, indent_str='    '):
    for key in d:
        if type(d[key]) is dict:
            print("{key}: ".format(key=repr(key)))
            pp_dict(d[key], indent_lvl=indent_lvl + 1)
        else:
            print(
                "{indent}{key}: {value}".format(indent=indent_lvl * indent_str, key=repr(key), value=repr(d[key])))

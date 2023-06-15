def enum_as_choices(enum, drop_empty_choice: bool = False):
    empty_choice = [] if drop_empty_choice else [(None, "---")]
    choices = empty_choice + [(enumerate.value, enumerate.value) for enumerate in enum]
    return choices
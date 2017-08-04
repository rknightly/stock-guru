def translate(value, current_min, current_max, new_min, new_max):
    """
    Translate a value from one range to another
    :param value: the value to translate
    :param current_min: the minimum of the current range
    :param current_max: the maximum of the current range
    :param new_min: the minimum of the new range
    :param new_max: the maximum of the new range
    :return: the given value translated to the new range
    """

    # Swap them if the max and min are reversed
    if current_min > current_max:
        tmp = current_max
        current_max = current_min
        current_min = tmp

        tmp = new_max
        new_max = new_min
        new_min = tmp

    # Return the new min or max if the value falls beyond the current range
    # specified
    if value < current_min:
        return new_min
    if value > current_max:
        return new_max

    # Figure out how 'wide' each range is
    left_span = current_max - current_min
    right_span = new_max - new_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = (value - current_min) / left_span

    # Convert the 0-1 range into a value in the right range.
    return new_min + (value_scaled * right_span)
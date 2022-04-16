import re

# Match everything but the number in of "$1.01" or "($1.01)"
balance_pattern = re.compile('[\$\(\)]')

def balance_to_float(balance_string):
    """
    Converts a balance in the format "$1.01" or "($1.01)" to a float.
    
    Positive balances (indicated by wrapped parens) are returned as negative numbers - most money we get is unwrapped.
    """
    # It's a bit easier to treat positive balances as negative numbers in this context,
    # since we're thinking about it in terms of amount owed.
    #
    # Positive balances are wrapped in parens, e.g. ($10.20)
    if not balance_string:
        return 0.0

    sign = -1 if balance_string.startswith('(') else 1
    # Strip everything but the number.
    number_string = balance_pattern.sub('', balance_string)
    return sign * float(number_string)
from pricing import total


assert total(1000) == 1000
assert total(1000, member=True) == 900

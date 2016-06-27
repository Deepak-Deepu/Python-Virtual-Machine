num = 1204
sum_dig = 0

while num > 0:
    rem = num % 10
    sum_dig = sum_dig + rem
    num = num / 10

print sum_dig

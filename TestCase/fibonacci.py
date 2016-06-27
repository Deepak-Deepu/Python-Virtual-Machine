first = 0
second = 1

num = 5

if num == 0:
    print first

if num == 1:
    print second

if num > 1:
    i = 1
    while i < num:
        temp = first
        first = second
        second = temp + second
        i = i + 1
    print second

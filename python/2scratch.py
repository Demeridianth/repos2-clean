def test(n, x=[]):
    x.extend(range(n))
    return x

a = test(2)
b = test(3)
print(b)
m = int(input())
n = int(input())

a = []
b = []
if m >= n:
    for i in range(m,n+1):
        k = str(i)
        s = list(k)
        a.append(s)

    # print(a)

    for i in a:
        array = i
        result = {i: array.count(i) for i in array}
        for j in result:
            if result[j] >= 3:
                m = ''
                for l in array:
                    m += l
                e = int(m)
                b.append(e)

    
    for i in b: print(i)

if m <= m:
    for i in range(m,m+1):
        k = str(i)
        s = list(k)
        a.append(s)

    # print(a)

    for i in a:
        array = i
        result = {i: array.count(i) for i in array}
        for j in result:
            if result[j] >= 3:
                m = ''
                for l in array:
                    m += l
                e = int(m)
                b.append(e)


    for i in b: print(i)



# print(a)

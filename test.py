a = "A,B,C"

b = a.split(",")

c = dict(enumerate(b))


db = ['A', 'B', 'C', 'D', 'D', 'E', 'A', 'B', 'C']

input = ['A', 'B', 'C', 'B', 'D', 'E', 'A', 'B', 'C']

# quenumber = 1
# res = {}
# for expected, actual in zip(db, input):
#     res[str(quenumber)] = {
#         "actual": actual,
#         "expected": expected
#     }
#     quenumber += 1


a = ",".join(db)
print(a)

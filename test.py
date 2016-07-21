from collections import defaultdict
r = defaultdict(dict)
r['선생님']['학생']= 5
print(r)

l= {}
l['teacher'] = {}
l['teacher']['student'] = 5
print(l)

g ={}
g[('선생님','pos')] = 5
g[('선생님','neg')] =1

print(g)

k = []
k.append(['선생님','pos','3'])
k.append(['선생님','neg','1'])
print(k)
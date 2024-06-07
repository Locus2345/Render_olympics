"""

This file parses this mess of a quartic outputted by wolfram alpha

"""


mess = open("mess.txt")
for line in mess:
    messlist = line.split()
messlist.append("-")
removals = ["-", "+"]
newlist = []
for i in range(len(messlist)-1):
    if messlist[i] in removals:
        j = i
        entry = ""
        while i == j or messlist[j] not in removals:
            entry += messlist[j]
            j += 1
        newlist.append(entry)
# print(newlist)
nones = []
ones = []
toos = []
trees = []
foors = []
caseo = 0
for element in newlist:
    if element.find('t') == -1:
        nones.append(element)
    else:
        t_ind = element.find('t')
        try:
            caseo = element[t_ind+2]
        except:
            caseo = '1'
        match caseo:
            case '1':
                ones.append(element)
            case '2':
                toos.append(element)
            case '3':
                trees.append(element)
            case '4':
                foors.append(element)
print("zero", nones)
print("one", ones)
print("two", toos)
print("three", trees)
print("four", foors)
file = open("out.txt", 'w')
file.write(' '.join(nones))
file.write("\n")
file.write(' '.join(ones))
file.write("\n")
file.write(' '.join(toos))
file.write("\n")
file.write(' '.join(trees))
file.write("\n")
file.write(' '.join(foors))
file.close()

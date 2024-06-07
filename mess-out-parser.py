def parseletter(term_, index):
    out = ""
    expo = False
    if term_[index + 1] == "^":
        out += "(" + term_[index]
        expo = True
        out += "**" + term_[index + 2] + ")"
    else:
        out += term_[index]
    out += "*"
    return out, expo


file_out = open("out.txt", "r")
power = 0
output = [[], [], [], [], []]
for line in file_out:
    linelst = line.split()
    t_out = ""
    for term in linelst:
        t_out = ""
        i = 0
        if term[0] == "+":
            t_out += "+ "
        else:
            t_out += "- "
        i += 1
        try:
            t_out += (str(int(term[1]))+"*")
            i += 1
        except:
            power = power
        while i < len(term):
            if i+1 < len(term):
                add, exponent = parseletter(term, i)
            else:
                add = term[i] + "*"
                exponent = False
            t_out += add
            i += 1 + exponent*2
        output[power].append(t_out[0:-1])
        print(term, t_out[0:-1])
    power += 1

writefile = open("end.txt", "w")
for a in output:
    print(a)
    writefile.write((" ".join(a))+"\n")


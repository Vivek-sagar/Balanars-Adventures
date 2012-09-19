cells = []
temp = 10010110
j = 0
for j in range(8):
    cells.append(temp%10)
    temp /= 10
cells.reverse()
print cells

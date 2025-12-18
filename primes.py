import math
a=int(input("first number 1:"))
b=int(input("second number 2:"))
while b<a:
    print("error b is less than a, chose correct range")
    a = int(input("new number 1:"))
    b = int(input("new number 2:"))
k=[]
while a==1 or b==1:
    print("choose another number for a")
    a = int(input("new number 1:"))
    b = int(input("new number 2:"))

for i in range(a,b+1):
    for j in range(2,i//2+1):
        if i % j == 0:
            break
    else:
        k.append(i)
print(k)

a=33
def get_me(aa):
	aa=aa+3
	print aa

get_me(a)
print a

aa=[1,2,3,4]
def check(lst):
	lst.append(33)
	#print "Inside method :"+str(lst)

print "Before :"+str(aa)
check(aa)
print "After :"+str(aa)


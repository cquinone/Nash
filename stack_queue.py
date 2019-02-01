class Queue:
	def __init__ (self):
		self.data = []

	def __str__ (self):
		return str(self.data[0])

	def __getitem__(self,item):
		return str(self.data[item])

	def push(self,item):
		self.data.append(item)

	def pop(self):
		return self.data.pop(0)

	def isEmpty(self):
		if len(self.data) == 0:	
			return True
		else:
			return False

class Stack:
	def __init__ (self):
		self.data = []

	def __str__ (self):
		return str(self.data[0])
	
	def __getitem__(self,item):
		return str(self.data[item])

	def push(self,item):
		self.data.append(item)

	def pop(self):
		return self.data.pop()

	def isEmpty(self):
		if len(self.data) == 0:	
			return True
		else:
			return False


#a = Stack()
#a.push(1)
#a.push(2)
#a.push(3)
#a.pop()
#print a[0],a[1]
#a.push(3)
#print a[-1]
#print a.isEmpty()
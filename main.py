#! /usr/bin/env python3

def parallel(res1, res2):
	return 1/(1/res1 + 1/res2)

def serial(res1, res2):
	return res1 + res2

def y_delta(res1, res2, res3):
	pass
class Nodelist:
	def __init__(self):
		self.list = []

	def add_node(self, name):
		self.list.append(Node(name, self))

	def get_node(self, name):
		if type(name) == Node:
			return name
		else:
			return [x for x in self.list if x.name == name][0]

	def get_list(self):
		return self.list


class Node:
	def __init__(self, name, parent):
		self.name = name
		self.nl = parent
		self.rl = []
		pass
	def add_resistance(self, t_node, res):
		self.rl.append([self.nl.get_node(t_node), res])

	def count_conns(self, node):
		count = 0
		if type(node) == Node:
			for el in self.rl:
				if el[0] is node:
					count += 1
		elif type(node) == str:
			for el in self.rl:
				if el[0].name == node:
					count += 1
		else:
			raise TypeError('can not use type: {}'.format(type(node)))

		return count

#class Resistance:
#	def __init__(self, frm, to, res):
#		self.frm = frm
#		self.to = to
#		self.res = res

def simplify(nl):
	# parallel 
	print('')
	for el in nl.get_list():
		for i in range(0, len(el.rl)):
			for j in range(i + 1, len(el.rl)):
				if el.rl[i][0] is el.rl[j][0]:
					res1 = el.rl[i][1]
					res2 = el.rl[j][1]
					other_node = el.rl[i][0]
					print('found parallel link at node ', el.name, ': ', other_node.name, res1, '|', other_node.name, res2, end=" -> ")
					new_res = parallel(res1, res2)
					print(new_res)
					# remove one resistance on other node
					other_node.rl.remove([el, res1])
					# index of item to change
					# then change the value to the new resistance
					change_idx = other_node.rl.index([el, res2])
					other_node.rl[change_idx] = [el, new_res]

					el.rl[j][1] = new_res
					el.rl.remove([other_node, res1])

					return True
	# serial
	# slice off the first and last element since they are the start and end nodes.
	for el in nl.get_list()[1:-1]:
		if len(el.rl) == 2 and el.rl[0][0] is not el.rl[1][0]:
			first_conn, second_conn = [x for x in el.rl if el.count_conns(x[0].name) == 1]
			new_res = serial(first_conn[1], second_conn[1])

			first_node = first_conn[0]
			second_node = second_conn[0]

			print('found serial link at node ', el.name, ': ', first_node.name, first_conn[1], '|', second_node.name, second_conn[1], end=" -> ")
			print(new_res)

			# remove old connections to current node
			first_node.rl.remove([el, first_conn[1]])
			second_node.rl.remove([el, second_conn[1]])

			# establish connection with new resistance value
			first_node.add_resistance(second_node, new_res)
			second_node.add_resistance(first_node, new_res)

			# clean up current node
			el.rl.clear()

			return True

	print('nothing to simplify')
	return False


def main():
	nl = Nodelist()
	with open('input2.txt') as f:
		# parse first line as list of nodes
		for name in [x.strip() for x in f.readline().split(' ')]:
			nl.add_node(name)
		# parse resistors			
		for line in f.readlines():
			line = line.strip()
			n1, n2, res = line.split(' ')
			nl.get_node(n1).add_resistance(n2, int(res))
			nl.get_node(n2).add_resistance(n1, int(res))
	

	while True:
		print('%%%%%%%%%%%%%%')
		print('current state:')
		for element in nl.get_list():
			print(element.name)
			print('\t', [(el[0].name, el[1]) for el in element.rl])

		if not simplify(nl):
			break
	print('\n%%%%%%%%%%%%%%')
	print('End of program')





if __name__ == '__main__':
	main()
#! /usr/bin/env python3

def math_parallel(res1, res2):
	return 1/(1/res1 + 1/res2)

def math_serial(res1, res2):
	return res1 + res2

def simplify_parallel(node):
	nl = node.nl
	for i in range(0, len(node.rl)):
		for j in range(i + 1, len(node.rl)):
			if node.rl[i][0] is node.rl[j][0]:
				res1 = node.rl[i][1]
				res2 = node.rl[j][1]
				other_node = node.rl[i][0]
				print('found parallel link at node ', node.name, ': ', other_node.name, res1, '|', other_node.name, res2, end=" -> ")
				new_res = math_parallel(res1, res2)
				print(new_res)
				# remove one resistance on other node
				other_node.rl.remove([el, res1])
				# index of item to change
				# then change the value to the new resistance
				change_idx = other_node.rl.index([el, res2])
				other_node.rl[change_idx] = [el, new_res]

				node.rl[j][1] = new_res
				node.rl.remove([other_node, res1])

				return True
	return False

def simplify_serial(node):
	nl = node.nl
	if len(el.rl) == 2 and el.rl[0][0] is not el.rl[1][0]:
		first_conn, second_conn = el.rl#[x for x in el.rl if el.count_conns(x[0].name) == 1]
		new_res = math_serial(first_conn[1], second_conn[1])

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

	return False



def y_delta(node):
	if len(node.rl) == 3:
		if [node.count_conns(x) for x in nl.get_list()].count(1) == 3:
			first_conn, second_conn, third_conn = node.rl
			r1, r2, r3 = first_conn[1], second_conn[1], third_conn[1]
			r_p = r1*r2 + r1*r3 + r2*r3
			r12 = r_p/r3
			r13 = r_p/r2
			r23 = r_p/r1

			first_node, second_node, third_node = first_conn[0], second_conn[0], third_conn[0]

			print('found possibility for Y->DELTA on node',first_node.name, 'with nodes', second_node.name, 'and', third_node.name)
			# clear connections to current node
			first_node.rl.remove([el, r1])
			second_node.rl.remove([el, r2])
			third_node.rl.remove([el, r3])

			# clear connection from current node
			node.rl.clear()

			# create new connections
			first_node.add_resistance(second_node, r12)
			first_node.add_resistance(third_node, r13)
			second_node.add_resistance(first_node, r12)
			second_node.add_resistance(third_node, r23)
			third_node.add_resistance(first_node, r13)
			third_node.add_resistance(second_node, r23)

			return True

	return False

def delta_y(node):
	if len(node.rl) >= 2:
		for i in range(0, len(node.rl)):
			for j in range(i+1, len(node.rl)):
				first_node, second_node, third_node = el, node.rl[i][0], node.rl[j][0]
				# condition for Delta-Y transformation (with an additional check if
				# they are properly parallelized(only one connection to the other nodes.)
				if first_node.count_conns(second_node) == 1\
				and first_node.count_conns(third_node) == 1\
				and second_node.count_conns(third_node) == 1:
					print('found possibility for DELTA->Y on node',first_node.name, 'with nodes', second_node.name, 'and', third_node.name)

					# create the new node that will be needed.
					nl.add_new_node(str(nl.additional_node_name))
					#new_node = Node(str(nl.additional_node_name),nl)
					nl.additional_node_name += 1
					new_node = nl.get_node(str(nl.additional_node_name - 1))
					r12 = node.rl[i][1]
					r13 = node.rl[j][1]
					# too lazy to write better code. But i already checked that it will
					# be a list of length 1... so why not
					r23 = [x for x in second_node.rl if x[0] is third_node][0][1]

					# calculate new values
					r_sum = r12 + r13 + r23
					r1 = r12*r13/r_sum
					r2 = r23*r12/r_sum
					r3 = r13*r23/r_sum

					# delete old connections
					third_node.rl.remove([second_node,r23])
					third_node.rl.remove([first_node, r13])

					second_node.rl.remove([first_node, r12])
					second_node.rl.remove([third_node, r23])

					first_node.rl.remove([second_node, r12])
					first_node.rl.remove([third_node, r13])

					# create new connections to new new node

					first_node.add_resistance(new_node, r1)
					second_node.add_resistance(new_node, r2)
					third_node.add_resistance(new_node, r3)

					new_node.add_resistance(first_node, r1)
					new_node.add_resistance(second_node, r2)
					new_node.add_resistance(third_node, r3)

					return True
	return False

class Nodelist:
	def __init__(self):
		self.additional_node_name = 1
		self.list = []

	def add_setup_node(self, name):
		self.list.append(Node(name, self))

	def add_new_node(self, name):
		self.list.insert(-1, Node(name, self))

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
			raise TypeError('can not use type: {}'.format(str(type(node))))

		return count

def simplify(nl):
	# parallel 
	for el in nl.get_list():
		for i in range(0, len(el.rl)):
			for j in range(i + 1, len(el.rl)):
				if el.rl[i][0] is el.rl[j][0]:
					res1 = el.rl[i][1]
					res2 = el.rl[j][1]
					other_node = el.rl[i][0]
					print('found parallel link at node ', el.name, ': ', other_node.name, res1, '|', other_node.name, res2, end=" -> ")
					new_res = math_parallel(res1, res2)
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
			first_conn, second_conn = el.rl#[x for x in el.rl if el.count_conns(x[0].name) == 1]
			new_res = math_serial(first_conn[1], second_conn[1])

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

	# Y -> DELTA
	# slice off the first and last element since they are the start and end nodes.
	for el in nl.get_list()[1:-1]:
		if len(el.rl) == 3:
			if [el.count_conns(x) for x in nl.get_list()].count(1) == 3:
				first_conn, second_conn, third_conn = el.rl
				r1, r2, r3 = first_conn[1], second_conn[1], third_conn[1]
				r_p = r1*r2 + r1*r3 + r2*r3
				r12 = r_p/r3
				r13 = r_p/r2
				r23 = r_p/r1

				first_node, second_node, third_node = first_conn[0], second_conn[0], third_conn[0]

				print('found possibility for Y->DELTA on node',first_node.name, 'with nodes', second_node.name, 'and', third_node.name)
				# clear connections to current node
				first_node.rl.remove([el, r1])
				second_node.rl.remove([el, r2])
				third_node.rl.remove([el, r3])

				# clear connection from current node
				el.rl.clear()

				# create new connections
				first_node.add_resistance(second_node, r12)
				first_node.add_resistance(third_node, r13)
				second_node.add_resistance(first_node, r12)
				second_node.add_resistance(third_node, r23)
				third_node.add_resistance(first_node, r13)
				third_node.add_resistance(second_node, r23)

				return True

	# DELTA - Y:
	for el in nl.get_list():
		if len(el.rl) >= 2:
			for i in range(0, len(el.rl)):
				for j in range(i+1, len(el.rl)):
					first_node, second_node, third_node = el, el.rl[i][0], el.rl[j][0]
					# condition for Delta-Y transformation (with an additional check if
					# they are properly parallelized(only one connection to the other nodes.)
					if first_node.count_conns(second_node) == 1\
					and first_node.count_conns(third_node) == 1\
					and second_node.count_conns(third_node) == 1:
						print('found possibility for DELTA->Y on node',first_node.name, 'with nodes', second_node.name, 'and', third_node.name)

						# create the new node that will be needed.
						nl.add_new_node(str(nl.additional_node_name))
						#new_node = Node(str(nl.additional_node_name),nl)
						nl.additional_node_name += 1
						new_node = nl.get_node(str(nl.additional_node_name - 1))
						r12 = el.rl[i][1]
						r13 = el.rl[j][1]
						# too lazy to write better code. But i already checked that it will
						# be a list of length 1... so why not
						r23 = [x for x in second_node.rl if x[0] is third_node][0][1]

						# calculate new values
						r_sum = r12 + r13 + r23
						r1 = r12*r13/r_sum
						r2 = r23*r12/r_sum
						r3 = r13*r23/r_sum

						# delete old connections
						third_node.rl.remove([second_node,r23])
						third_node.rl.remove([first_node, r13])

						second_node.rl.remove([first_node, r12])
						second_node.rl.remove([third_node, r23])

						first_node.rl.remove([second_node, r12])
						first_node.rl.remove([third_node, r13])

						# create new connections to new new node

						first_node.add_resistance(new_node, r1)
						second_node.add_resistance(new_node, r2)
						third_node.add_resistance(new_node, r3)

						new_node.add_resistance(first_node, r1)
						new_node.add_resistance(second_node, r2)
						new_node.add_resistance(third_node, r3)

						return True



	print('nothing to simplify')
	return False


def main():
	nl = Nodelist()
	with open('input4x4.txt') as f:
		# parse first line as list of nodes
		for name in [x.strip() for x in f.readline().split(' ')]:
			nl.add_setup_node(name)
		# parse resistors			
		for line in f.readlines():
			line = line.strip()
			n1, n2, res = line.split(' ')
			nl.get_node(n1).add_resistance(n2, int(res))
			nl.get_node(n2).add_resistance(n1, int(res))
	
	iter_num = 1
	print('%%%%%%%%%%%%%%')
	print('initial grid:')
	for element in nl.get_list():
		print(element.name)
		print('\t', [(el[0].name, el[1]) for el in element.rl])

	input('press any key to start')
	
	while True:
		print('Iteration No.{}'.format(iter_num))
		iter_num += 1

		if not simplify(nl):
			break
	
	print('%%%%%%%%%%%%%%')
	print('final grid:')
	for element in nl.get_list():
		print(element.name)
		print('\t', [(el[0].name, el[1]) for el in element.rl])

	print('\n%%%%%%%%%%%%%%')
	print('End of program')





if __name__ == '__main__':
	main()
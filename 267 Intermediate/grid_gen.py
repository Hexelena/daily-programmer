from string import ascii_uppercase as a_u

def main():
	order = input("What grid size would you like to have(e.g. for 4x4 type 4)?\n")
	order = int(order)
	doc_lines = []

	first_line = ""

	for i in range(0, order):
		for j in range(0, order):
			first_line += '{}{} '.format(a_u[i], a_u[j])

	doc_lines.append(first_line.strip())

	for i in range(0, order):
		for j in range(0, order - 1):
			newline = '{}{} {}{} 10'.format(a_u[i], a_u[j], a_u[i], a_u[j+1])
			doc_lines.append(newline)
		if i < order - 1:
			for j in range(0, order):
				newline = '{}{} {}{} 10'.format(a_u[i], a_u[j], a_u[i + 1], a_u[j])
				doc_lines.append(newline)

	for line in doc_lines:
		print(line)
	with open('input{}x{}.txt'.format(order, order), 'w') as f:
		f.writelines([x + '\n' for x in doc_lines])


if __name__ == '__main__':
	main()
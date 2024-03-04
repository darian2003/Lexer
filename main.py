from sys import argv
from . import Lexer
LIST = 0
CONCAT = 1
SUM = 2
LAMBDA = 3
NUMBER = 4


def main():
	if len(argv) != 2:
		return

	filename = argv[1]
	content = ""

	try:
		# Open the file and read its content
		with open(filename, 'r') as file:
			# Read all lines from the file into a list
			lines = file.readlines()

			# Join the lines to form the content, preserving newline characters
			content = ''.join(lines)

	except FileNotFoundError:
		print(f"File '{filename}' not found.")

	except Exception as e:
		print(f"An error occurred: {e}")

	# TODO implementarea interpretor L (bonus)
	spec = [("(", "\\("), (")", "\\)"), ("space","\\ "), ("tab", "\t"), ("lambda-exp", "lambda "), ("var", "([a-z] | [A-Z])+"), ("concat", "++"), ("sum", "+"), ("function definition", ":"), ("number", "[0-9]+"), ("newline", "\n")]

	# Construct the lexer using our own specification
	lexer = Lexer.Lexer(spec)
	# Split the input into lexemes
	lexeme_list = lexer.lex(content)
	# Remove redundant elements (spaces, tabs, newlines)
	lexeme_list = remove_whitespaces(lexeme_list)

	print(f'{lexeme_list=}')


	# Step 1: Solve all the lambda expressions.
	(l, index) = solve_lambda(lexeme_list, 0)

	# Step 2: Solve all the function calls (if any) & compute the result
	(result, index) = compute_final_result(l, 0)

	print_result(result)

	

# This function returns when there are no longer any lambda expression in the list.
# Each lambda expression is going to be substituted with its body, with the remark than ANY variable from
# the body that can be replaced, will be replaced with the value dictated by the coresponding argument
# E.g : "... ((lambda x: lambda y: (x y) 1) 2) ..." will become "... (1 2) ...", since the body is "(x y)"
# and both of the variables can be replaced with the given arguments. In the above expression, "..." could be
# lists, numbers, function calls (+, ++) or even other lambda expressions
def solve_lambda(l: list[tuple[str, str]], index: int) -> (list[tuple[str, str]], int) :

	solved = False

	# This loop is broken out of only when there are no more lambda expressions left to be computed
	while not solved :
		solved = True
		index = 0
		lambda_exp_counter = 0 # the number of imbricated lambda-expressions

		# the number of variables from this list is equal to lambda_exp_counter, since each expression has a variable and receives an argument
		var_list = []
		value_list = []

		# iterate through the lexemes list looking for the "lambda" keyword hc
		while index < len(l) :
			if l[index][0] == "lambda-exp" :

				# Remember where the lambda expression started
				lambda_start_index = index

				# Remember how many imbricated lambda-expressions there are
				lambda_exp_counter += 1

				# Skip the "lambda" keyword
				index += 1

				# Remember the variable name
				var_list.append(l[index][1])

				# Skip the variable name and the ":"
				index += 2

				# Check if there are more lambda-expressions imbricated np
				while l[index][0] == "lambda-exp" :
					lambda_exp_counter += 1
					# Skip "lambda" keyword
					index += 1
					# Add next argument to list
					var_list.append(l[index][1])
					# Skip the variable name and the ":"
					index += 2

				# Now we reached the body of the expression. The body ends when the parenthesis counter becomes 0
				body_start = index
				body_end = index
				parenthesis_count = 0

				if l[index][0] == "(" :
					parenthesis_count += 1
					index += 1
					body_end += 1

				# Perform a "do-while" until we reach the end of the uup body
				while True :
					body_end += 1
					if l[index][0] == ")":
						parenthesis_count -= 1
					elif l[index][0] == "(" :
						parenthesis_count += 1

					index += 1

					# The body ends when the parenthesis count becomes 0!
					if parenthesis_count <= 0 :
						break

				# Compute the body
				body = l[body_start:body_end]

				i = 0
				# We parsed the body, so now we parse the arguments (whose number should be equal to that of lambda_exp_counter) utd
				while i < lambda_exp_counter :
					# An argument ends when the parenthesis counter becomes -1
					parenthesis_count = 0
					current_argument = []
					while True :
						if l[index][0] == ")" :
							parenthesis_count -= 1
							if parenthesis_count == -1 :
								index += 1
								break
						elif l[index][0] == "(" :
							parenthesis_count += 1
						current_argument.append(l[index])
						index += 1

					value_list.append(current_argument)
					i += 1


				# By replacing the variables with the appropriate values we are solving the lambda-expressions.
				# After that, we are recomputing lexemes list, replacing the lambda-exp with computed the new value.
				substituted_body = []
				for el in body :
					if el[0] == "var" :
						# Take the variable name and search for its replacement
						var_name = el[1]

						# We are iterating through the reversed var_list because the last variable assignment matters
						# E.g : ((lambda x: lambda x: x 1) 2) => result is 2
						for i in reversed(range(0, len(var_list))) :
							# Start searching for the name of the variable and replace it accordingly in the body
							if var_name == var_list[i] :
								substituted_body.extend(value_list[i])
								break

					else :
						# Every other lexeme that is not a variable is being copied
						substituted_body.append(el)

				# We may have some other instructions before or after the lambda expressions that we have computed.
				# So now we are going to compute the list that also incorporates the prefix and suffix of the lambda exp

				# The suffix goes up until the first "(" that belongs to the lambda-exp.
				# To find its index, from the first appearance of a lambda-exp, we are going back "lambda-exp-counter" characters.
				# The reason for that is: for each lambda-expression that we parsed, there is a pair of "()" at the beginning and end of the expression uhh
				prefix = l[0:lambda_start_index - lambda_exp_counter]
				suffix = l[index:]
				l = prefix + substituted_body + suffix

				solved = False
				break

			index += 1

	return (l, index)


def compute_final_result(l: list[tuple[str, str]], index: int) -> list | int:

	# The result could be a number or a und list
	if l[index][0] == "number":
		return (l[index][1], index)

	result = []

	if l[index][0] == "(" :
		if l[index+1][0] == "sum" :
			(result, index) = do_sum(l, index)
		elif l[index+1][0] == "concat" :
			(result, index) = do_concat(l, index)
		else :
			(result, index) = do_list(l, index)
	return (result, index)


# When calling this function, it is presumed that the list only contains numbers or library function calls (+, ++) and no longer contains lambda-exp
def do_list(l: list[tuple[str, str]], index: int) -> (list | int, int) :
	result = []

	# skip the "("
	index += 1

	while True :
		if l[index][0] == "number" :
			result.append(l[index][1])
		elif l[index][0] == "(" :
			(new_exp, index) = do_list(l, index)
			result.append(new_exp)
		elif l[index][0] == ")" :
			return (result, index)
		index += 1


# Computes a ++ operation and returns the resulted list
def do_concat(l: list[tuple[str, str]], index: int) -> list | int:

	# skip the "(" & "++"
	index += 2

	# skip the "("
	index += 1

	result = []

	while True :
		if l[index][0] == "number" :
			result.append(l[index][1])
		elif l[index][0] == "(" :
			if l[index+1][0] == "concat" :
				(new_list, index) = do_concat(l, index)
				for el in new_list :
					result.append(el)
			elif l[index+1][0] == "sum" :
				(nr, index) = do_sum(l, index)
				result.append(nr)
			else :
				(new_list, index) = do_list(l, index)
				for el in new_list :
					result.append(el)
		elif l[index][0] == ")":
			return result, index

		index += 1

# Receives a list and returns the sum of its elements
def sum_of_list(l: list) -> int :

	sum = 0
	i = 0
	for el in l :
		if isinstance(el, list) :
			sum += sum_of_list(el)
		else :
			sum += el
	return sum

def do_sum(l: list[tuple[str, str]], index: int) -> list | int:

	# skip the "(+"
	index += 2

	sum = 0

	while True :
		if l[index][0] == "(" :
			if l[index+1][0] == "sum" :
				(new_exp, index) = do_sum(l, index)
				sum += new_exp
			elif l[index+1][0] == "concat" :
				(new_list, index) = do_concat(l, index)
				sum += sum_of_list(new_list)
			else :
				(new_list, index) = do_list(l, index)
				sum += sum_of_list(new_list)
		elif l[index][0] == ")" :
			return (sum, index)

		index += 1

def remove_whitespaces(l: list[tuple[str, str]]) -> list[tuple[str, str]] :
	final_list = []
	for (i, j) in l:
		if i == "space" or i == "newline" or i == "tab":
			continue
		elif i == "number":
			final_list.append((i, int(j)))
		else:
			final_list.append((i, j))
	return final_list


def print_list(l: list) -> int:
	if l == []:
		print(f"() ", end ="")
		return

	print(f"( ", end="")
	for i, el in enumerate(l):
		if isinstance(el, list):
			print_list(el)
		else:
			print(f"{el} ", end="")
	print(f") ", end="")

def print_result(l: list | int) :
	if isinstance(l, list):
		print("( ", end="")
		for i in range(len(l)):
			if isinstance(l[i], list):
				print_list(l[i])
			else :
				print(f"{l[i]} ", end ="")
		print(")")
	else:
		print(f"{l}")



if __name__ == '__main__':
    main()




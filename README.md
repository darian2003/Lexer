# Python Interpreter
The purpose of this project is to create an interpreter for a personally created programming language (similar to LSIP) that receives as input a sequence of operations and computes the result.
For example, given the input "(++ ((1 2  ()) (3 4)))" it returns "( 1 2 () 3 4 )" 
or given the input "((((lambda x: lambda y: ((x y) x) lambda x: lambda y: x) lambda x: lambda y: y) 1 ) 2)" it returns "2".

The program works as follows:
1. A specification of all the possible tokens of the programming language is given.
2. The regex of each possible token is converted into a DFA.
3. Create a new big NFA by computing together all the previously created DFAs.
4. Run our input string on this NFA and get the list of all lexemes. This will split our string into opearnds and operators.
5. Create a tree of ordered operations.
6. Perform the opearations starting from the root of the tree.



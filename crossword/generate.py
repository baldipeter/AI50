import sys
import math

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Creates a set of the inconsistent values
        for var in self.domains:
            inconsistent = set()
            for word in self.domains[var]:
                if var.length != len(word):
                    inconsistent.add(word)
            # And removes them from the node's domain
            self.domains[var] = self.domains[var].difference(inconsistent)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        def check(shared, word):
            """
            Returns True if `word` is consistent with any words from the domain of variable `y`
            """
            no_of_letter_x = shared[x, y][0]
            no_of_letter_y = shared[x, y][1]
            for w in self.domains[y]:
                if word[no_of_letter_x] == w[no_of_letter_y]:
                    return True
            return False

        shared = self.crossword.overlaps

        # If there is no shared letter return False
        if not shared[x, y]:
            return False

        # Else check if inconsistent. Check is a separate function for readability
        inconsistent = set()
        for word in self.domains[x]:
            if not check(shared, word):
                inconsistent.add(word)

        # If the inconsistent set is not empty, then remove them from the domain and return True
        if inconsistent:
            self.domains[x] = self.domains[x].difference(inconsistent)
            return True
        elif not inconsistent:
            return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If `arcs` is None, begin with initial list of all arcs in the problem.
        if arcs == None:
            arcs = list(self.domains.keys())

        # Create queue
        queue = []
        for x in arcs:
            for y in arcs:
                if x == y:
                    continue
                else:
                    queue.append((x, y))

        # Loop queue with the help of the revise function
        for (x, y) in queue:
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                else:
                    for neighbor in self.crossword.neighbors(x):
                        queue.append((neighbor, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # If not all vars has been assigned
        for var in self.domains.keys():
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Find overlaping points
        shared = self.crossword.overlaps

        for var in assignment:
            # check if value fits space
            if len(assignment[var]) != var.length:
                return False

            # check if value is distinct
            for v in assignment:
                if v == var:
                    continue
                if assignment[var] == assignment[v]:
                    return False

            # check if there are no conflicts between neighboring variables
            for neighbor in self.crossword.neighbors(var):
                if shared[var, neighbor] and neighbor in assignment:
                    # For better readability
                    word = assignment[var]
                    no_of_letter_var = shared[var, neighbor][0]
                    neigbour_word = assignment[neighbor]
                    no_of_letter_neighbor = shared[var, neighbor][1]

                    if word[no_of_letter_var] != neigbour_word[no_of_letter_neighbor]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        order = {}
        shared = self.crossword.overlaps
        neighbors = self.crossword.neighbors(var)

        for word in self.domains[var]:
            # Has to be distinct
            if word in list(assignment.values()):
                continue
            n = 0
            for neighbor in neighbors:
                # Any variable present in assignment already has a value, and therefore shouldn’t be counted
                if neighbor in list(assignment.keys()):
                    continue
                if not shared[var, neighbor]:
                    continue
                for w in self.domains[neighbor]:
                    # If word and w do not match increase n
                    no_of_letter_var = shared[var, neighbor][0]
                    no_of_letter_neighbor = shared[var, neighbor][1]

                    if word[no_of_letter_var] != w[no_of_letter_neighbor]:
                        n += 1
            order[word] = n

        # return sorted order
        return sorted(order, key=lambda key: order[key], reverse=False)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        lowest = math.inf
        for var in self.domains.keys():
            if var in assignment:
                continue
            # If the new var has the minimum number of remaining values start a new order
            if len(self.domains[var]) < lowest:
                lowest = len(self.domains[var])
                order = {var: len(self.crossword.neighbors(var))}
            # If it is equal, add to dict
            elif len(self.domains[var]) == lowest:
                order[var] = len(self.crossword.neighbors(var))
            else:
                continue
        return sorted(order, key=lambda key: order[key], reverse=False)[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment is complete, return assignment
        if self.assignment_complete(assignment):
            return assignment

        # Chose variable with the minimum number of remaining values
        var = self.select_unassigned_variable(assignment)
        # Chose value from variable's domain based on the number of values they rule out for neighboring variables
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value

            # If not consistent try a new value
            if not self.consistent(assignment):
                assignment.pop(var)
                continue

            # If not arc-consistent try a new value
            if not self.ac3():
                assignment.pop(var)
                continue

            # If it is successfull, then return the result
            result = self.backtrack(assignment)
            if result != None:
                return result
            # try new value
            assignment.pop(var)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

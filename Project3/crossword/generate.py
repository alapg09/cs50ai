import sys

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
        for var in self.domains:
            for word in self.domains[var].copy():  # iterate over a copy
                if len(word) != var.length:
                    self.domains[var].remove(word)


        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False

        x_ind, y_ind = overlap
        revised = False

        for x_word in self.domains[x].copy():
            if not any(x_word[x_ind] == y_word[y_ind] for y_word in self.domains[y]):
                self.domains[x].remove(x_word)
                revised = True

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is not None:
            queue = list(arcs)
        else:
            queue = [(x, y) for (x, y) in self.crossword.overlaps if self.crossword.overlaps[(x, y)] is not None]

        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
            
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))     

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        words = set()

        for var1 in assignment:
            word1 = assignment[var1]

            # Check length constraint
            if len(word1) != var1.length:
                return False

            # Check for uniqueness
            if word1 in words:
                return False
            words.add(word1)

            # Check for conflicts with neighbors in assignment
            for var2 in assignment:
                if var1 == var2:
                    continue

                overlap = self.crossword.overlaps[var1, var2]
                if overlap is not None:
                    i, j = overlap
                    word2 = assignment[var2]
                    if word1[i] != word2[j]:
                        return False

        return True




    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        score = dict()


        for val in self.domains[var]:
            conflict_count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    if self.crossword.overlaps[var, neighbor] is not None:
                        for word in self.domains[neighbor]:
                            x, y = self.crossword.overlaps[var, neighbor]
                            if val[x] != word[y]:
                                conflict_count += 1

            score[val] = conflict_count
        

        sorted_keys = sorted(score, key = lambda k: score[k])
        return sorted_keys

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        import random

        unassigned_vars = [v for v in self.crossword.variables if v not in assignment]

        # Start with no candidate
        candidate = None

        for var in unassigned_vars:
            if candidate is None:
                candidate = var
                continue

            domain_len_var = len(self.domains[var])
            domain_len_cand = len(self.domains[candidate])

            if domain_len_var < domain_len_cand:
                candidate = var

            elif domain_len_var == domain_len_cand:
                degree_var = len(self.crossword.neighbors(var))
                degree_cand = len(self.crossword.neighbors(candidate))

                if degree_var > degree_cand:
                    candidate = var
                elif degree_var == degree_cand:
                    candidate = random.choice([candidate, var])

        return candidate
        

            


    def backtrack(self, assignment):
        import copy
        # If assignment is complete, return it
        if self.assignment_complete(assignment):
            return assignment

        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Try each value in order of least-constraining
        for value in self.order_domain_values(var, assignment):

            # If value is consistent with current assignment
            assignment[var] = value
            if self.consistent(assignment):

                # Inference: (optional) try to reduce domains using AC3
                inferences = dict()
                original_domains = copy.deepcopy(self.domains)

                # Run AC3 starting from neighbors of var
                if self.ac3([(neighbor, var) for neighbor in self.crossword.neighbors(var)]):
                    result = self.backtrack(assignment)
                    if result is not None:
                        return result

                # Restore domains if inference fails
                self.domains = original_domains

            # Backtrack: remove assignment and any inferences
            del assignment[var]

        # If no value leads to a solution
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

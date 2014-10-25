##############################################################################
# game.py - Responsible for generating moves to give to client.py            #
# Moves via stdout in the form of "# # # #" (block index, # rotations, x, y) #
# Important function is find_move, which should contain the main AI          #
##############################################################################
import sys
import json
import util

# Simple point class that supports equality, addition, and rotations
class Point:
    x = 0
    y = 0

    # Can be instantiated as either Point(x, y) or Point({'x': x, 'y': y})
    def __init__(self, x=0, y=0):
        if isinstance(x, dict):
            self.x = x['x']
            self.y = x['y']
        else:
            self.x = x
            self.y = y

    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def __eq__(self, point):
        return self.x == point.x and self.y == point.y

    # rotates 90deg counterclockwise
    def rotate(self, num_rotations):
        if num_rotations == 1: return Point(-self.y, self.x)
        if num_rotations == 2: return Point(-self.x, -self.y)
        if num_rotations == 3: return Point(self.y, -self.x)
        return self

    def distance(self, point):
        return abs(point.x - self.x) + abs(point.y - self.y)

class Game:
    blocks = []
    grid = []
    bonus_squares = []
    my_number = -1
    dimension = -1 # Board is assumed to be square
    turn = -1

    def __init__(self, args):
        self.interpret_data(args)

    # find_move is your place to start. When it's your turn,
    # find_move will be called and you must return where to go.
    # You must return a tuple (block index, # rotations, x, y)
    
    def get_legal_moves(self, turn=self.turn, grid=self.grid, yield_first=False):
        N = self.dimension
        no_legal_moves = True

        for index, block in enumerate(self.all_blocks[turn]):
            for i in xrange(0, N * N):
                x = i / N
                y = i % N

                for rotations in xrange(4):
                    new_block = self.rotate_block(block, rotations)

                    if self.can_place(new_block, Point(x, y)):
                        no_legal_moves = False
                        yield (index, rotations, x, y)

                        if yield_first:
                            break

        if no_legal_moves:
            yield False

    def do_move(self, move, turn=self.turn, grid=self.grid):
        index, rotations, x, y = move
        
        new_block = self.rotate_block(self.all_blocks[turn][index], rotations)
        ref_point = Point(x, y)
        
        # Bug Protection
        assert self.can_place(new_block, ref_point, turn, grid), "Illegal Block Move"
        
        new_grid = grid.copy()
        
        for offset in new_block:
            occupied_point = ref_point + offset
            new_grid[occupied_point.y][occupied_point.x] = turn    
        
        return new_grid
 
    def is_game_over(self, turn=self.turn, grid=self.grid):
        moves_generator = self.get_legal_moves(turn, grid)
        
        return not moves_generator.next()
    
    def is_terminal(self, depth, turn=self.turn, grid=self.grid):
        return depth <= 0 or self.is_game_over(turn, grid)
        
    def evaluate(self, turn=self.turn, grid=self.grid): #in progress
        N = self.dimension
        
        score = 0
        
        for i in xrange(0, N * N):        
            x = i / N
            y = i % N
        
            multiplier = 3 if [x, y] in self.bonus_squares else 1
            
            if grid[x][y] == -1:
                score += 0.5 * multiplier
            
            elif grid[x][y] == turn:
                score += 1 * multiplier
            
            elif grid[x][y] != turn:
                score += -1 * multiplier
            
            elif grid[x][y] == -2:
                score += 0 * multiplier
        
        return score
        
    def find_move(self, depth, turn=self.turn, grid=self.grid, alpha=None, beta=None, starting=True, maximizer=self.turn):       
        if starting:
            alpha, beta = (-float('inf'), float('inf'))

        if self.is_terminal(depth, turn, grid):
            return self.evaluate(turn, grid)

        for move, new_grid in self.get_legal_moves(turn, grid):
            if turn == maximizer or turn == (maximizer - 1)%4:
                new_val = -1 * self.find_move(depth - 1, (turn + 1)%4, new_grid, -beta, -alpha, False, maximizer)
            
            else:
                new_val = self.find_move(depth - 1, (turn + 1)%4, new_grid, alpha, beta, False, maximizer)
            
            if new_val > alpha:
                alpha = new_val
                next_move = move
                
            if alpha >= beta:
                break

        return next_move if starting else alpha       

    # Checks if a block can be placed at the given point
    def can_place(self, block, point, turn=self.my_number, grid=self.grid):
        onAbsCorner = False
        onRelCorner = False
        N = self.dimension - 1

        corners = [Point(0, 0), Point(N, 0), Point(N, N), Point(0, N)]
        corner = corners[turn]

        for offset in block:
            p = point + offset
            x = p.x
            y = p.y
            if (x > N or x < 0 or y > N or y < 0 or grid[x][y] != -1 or
                (x > 0 and grid[x - 1][y] == turn) or
                (y > 0 and grid[x][y - 1] == turn) or
                (x < N and grid[x + 1][y] == turn) or
                (y < N and grid[x][y + 1] == turn)
            ): return False

            onAbsCorner = onAbsCorner or (p == corner)
            onRelCorner = onRelCorner or (
                (x > 0 and y > 0 and grid[x - 1][y - 1] == turn) or
                (x > 0 and y < N and grid[x - 1][y + 1] == turn) or
                (x < N and y > 0 and grid[x + 1][y - 1] == turn) or
                (x < N and y < N and grid[x + 1][y + 1] == turn)
            )

        if grid[corner.x][corner.y] < 0 and not onAbsCorner: return False
        if not onAbsCorner and not onRelCorner: return False

        return True

    # rotates block 90deg counterclockwise
    def rotate_block(self, block, num_rotations):
        return [offset.rotate(num_rotations) for offset in block]

    # updates local variables with state from the server
    def interpret_data(self, args):
        if 'error' in args:
            debug('Error: ' + args['error'])
            return

        if 'number' in args:
            self.my_number = args['number']

        if 'board' in args:
            self.dimension = args['board']['dimension']
            self.turn = args['turn']
            self.grid = args['board']['grid']
            self.all_blocks = args['blocks']
            self.blocks = args['blocks'][self.my_number]
            self.bonus_squares = set(args['board']['bonus_squares'])

            for index, block in enumerate(self.blocks):
                self.blocks[index] = [Point(offset) for offset in block]

        if (('move' in args) and (args['move'] == 1)):
            send_command(" ".join(str(x) for x in self.find_move()))

        if self.is_my_turn():
            util.run_search_fn(self, util.memoize(self.find_move))

    def is_my_turn(self):
        return self.turn == self.my_number

def get_state():
    return json.loads(raw_input())

def send_command(message):
    print message
    sys.stdout.flush()

def debug(message):
    send_command('DEBUG ' + str(message))

def main():
    setup = get_state()
    game = Game(setup)

    while True:
        state = get_state()
        game.interpret_data(state)

if __name__ == "__main__":
    main()

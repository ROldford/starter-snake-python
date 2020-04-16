import os
import random

import cherrypy
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

"""
This is a simple Battlesnake server written in Python.
For instructions see 
https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    _HUNGER_LEVEL = 50

    @cherrypy.expose
    def index(self):
        # If you open your snake URL in a browser you should see this message.
        return "Your Battlesnake is alive!"

    @cherrypy.expose
    def ping(self):
        # The Battlesnake engine calls this function
        # to make sure your snake is working.
        return "pong"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game
        # that's about to be played.
        # TODO: Use this function to decide
        #       how your snake is going to look on the board.
        # data = cherrypy.request.json
        print("START")
        return {"color": "#61abff", "headType": "silly", "tailType": "sharp"}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your
        # snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to
        #       decide your next move.
        data = cherrypy.request.json
        board = data["board"]
        me = data["you"]
        head = data["you"]["body"][0]
        # snakes = board["snakes"]
        food = self.prioritize_food(head, board)

        if self.hungry(me):
            move = self.hunt_food(board, food, head)
        else:
            move = self.random_move(head, board)

        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes,
        # you don't have to make any decisions here.
        # data = cherrypy.request.json
        print("END")
        return "ok"

    # Helper functions
    def hunt_food(self, board, food, head):
        grid = self.generate_grid(board)
        start = grid.node(head["x"], head["y"])
        closest_food = food[0]
        end = grid.node(closest_food["x"], closest_food["y"])
        finder = AStarFinder()
        path = finder.find_path(start, end, grid)
        move = self.get_next_move_from_path(path)
        return move

    def random_move(self, head, board):
        possible_moves = ["up", "down", "left", "right"]
        possible_moves = [move for move in possible_moves
                          if not self.obstacle_adjacent(head, move, board)]
        if possible_moves:
            return random.choice(possible_moves)
        else:
            return random.choice(["up", "down", "left", "right"])

    def obstacle_adjacent(self, head, direction, board):
        snakes = board["snakes"]
        for snake in snakes:
            for segment in snake["body"]:
                if self.adjacent(head, direction, segment, board):
                    return True
        return False

    def adjacent(self, head, direction, segment, board):
        width = board["width"]
        height = board["height"]
        delta_x = segment["x"] - head["x"]
        delta_y = segment["y"] - head["y"]
        if direction == "up":
            return (delta_x == 0 and delta_y == -1) or head["y"] == 0
        elif direction == "down":
            return (delta_x == 0 and delta_y == 1) or head["y"] == height - 1
        elif direction == "left":
            return (delta_x == -1 and delta_y == 0) or head["x"] == 0
        elif direction == "right":
            return (delta_x == 1 and delta_y == 0) or head["x"] == width - 1

    def prioritize_food(self, head, board):
        food = board["food"]
        return food.sort(key=lambda x: (
                abs(x["x"] - head["x"]) + abs(x["y"] - head["y"])
        ))

    def hungry(self, me):
        health = me["health"]
        return health < self._HUNGER_LEVEL

    def generate_grid(self, board):
        height = board["height"]
        width = board["width"]
        matrix = [i[:] for i in [[1] * width] * height]
        for snake in board["snakes"]:
            for segment in snake:
                row = segment["y"]
                col = segment["x"]
                matrix[row][col] = 0
        return Grid(matrix=matrix)

    def get_next_move_from_path(self, path):
        current_position = path[0]
        next_position = path[1]
        delta_x = next_position["x"] - current_position["x"]
        delta_y = next_position["y"] - current_position["y"]
        if delta_x == 0:
            if delta_y > 0:
                return "down"
            else:
                return "up"
        else:
            if delta_x > 0:
                return "right"
            else:
                return "left"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")), }
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)

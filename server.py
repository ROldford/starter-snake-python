import os
import random

import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see 
https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
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
        head = data["you"]["body"][0]
        snakes = board["snakes"]
        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]
        # for direction in possible_moves:
        #     print(f"Checking {direction}")
        #     if self.obstacle_adjacent(head, direction, snakes, board):
        #         possible_moves.remove(direction)
        possible_moves = [move for move in possible_moves
                          if not self.obstacle_adjacent(
                                head, move, snakes, board)]

        move = random.choice(possible_moves)

        print(possible_moves)
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
    def obstacle_adjacent(self, head, direction, snakes, board):
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
            if (delta_x == 0 and delta_y == -1) or head["y"] == 0:
                return True
        elif direction == "down":
            if (delta_x == 0 and delta_y == 1) or head["y"] == height - 1:
                return True
        elif direction == "left":
            if (delta_x == -1 and delta_y == 0) or head["x"] == 0:
                return True
        elif direction == "right":
            if (delta_x == 1 and delta_y == 0) or head["x"] == width - 1:
                return True
        return False


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")), }
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)

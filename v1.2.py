import curses
import random


ENERGY_LOST_PER_STEP = 1
ENERGY_REWARD = 10
MAX_INITIAL_ENERGY = 30
INITIAL_AGENTS = 1
INITIAL_FOOD = 50
DELAY_BETWEEN_STEPS = 100  # ms
FOOD_THRESHOLD = 2
FOOD_ADDITION = 1
GRID_MAX = 50
GRID_WIDTH = 70
GRID_HEIGHT = 50
VISION_RADIUS = 20

def sign(value) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


class Agent:
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.energy = MAX_INITIAL_ENERGY
        self.status = 1

    def move(self, target, shortest_distance):
        if target[0] is not "None" and target[1] is not "None":
            x_diff = target[0] - self.pos_x
            y_diff = target[1] - self.pos_y
            x = self.pos_x + sign(x_diff)
            y = self.pos_y + sign(y_diff)

            if (x, y) == target:
                self.energy += ENERGY_REWARD
                self.energy -= ENERGY_LOST_PER_STEP
                self.pos_x += sign(x_diff)
                self.pos_y += sign(y_diff)
                return "food eaten", (self.pos_x, self.pos_y)
            else:
                self.pos_x += sign(x_diff)
                self.pos_y += sign(y_diff)
                self.energy -= ENERGY_LOST_PER_STEP
                return "moved", (self.pos_x, self.pos_y)
        else:
            return "not moved", (self.pos_x, self.pos_y)


def nearest_point(point_list, a, b):
    shortest_distance = float('inf')
    closest_point = None

    for x, y in point_list:
        # Calculate distance using Euclidean distance formula
        distance = (abs(x - a) + abs(y - b))

        if distance < shortest_distance:
            shortest_distance = distance
            closest_point = (x, y)

    shortest_distance = shortest_distance if shortest_distance <= VISION_RADIUS else "None"
    closest_point = closest_point if shortest_distance is not "None" else ("None", "None")

    return closest_point, shortest_distance


def simulate_process(food, agents, agents_pos):
    for agent in agents:
        prev_x, prev_y = agent.pos_x, agent.pos_y
        (x, y), shortest_distance = nearest_point(food, agent.pos_x, agent.pos_y)
        msg, new_pos = agent.move((x, y), shortest_distance)
        if msg == "food eaten":
            food.remove((x, y))
            agents_pos.remove((prev_x, prev_y))
            agents_pos.append(new_pos)
        elif msg == "moved":
            agents_pos.remove((prev_x, prev_y))
            agents_pos.append(new_pos)
    return food, agents, agents_pos


def update_status(win, alive, dead, avg_energy):
    max_y, max_x = win.getmaxyx()  # Get window height and width

    # Adjust y-coordinates to stay within bounds (assuming 0-based indexing)

    win.addstr(2, GRID_WIDTH + 6, f"Alive: {alive}")
    win.addstr(3, GRID_WIDTH + 7, f"Dead: {dead}")

    win.addstr(6, GRID_WIDTH + 1, f"Avg energy: {avg_energy}")

def main():
    agents = []
    agents_pos = []

    alive = INITIAL_AGENTS
    dead = 0

    stdscr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, not curses)
    curses.init_pair(2, curses.COLOR_GREEN, not curses);

    max_y, max_x = stdscr.getmaxyx()
    win = curses.newwin(max_y, max_x, 1, 1)

    food = [(random.randint(1, GRID_HEIGHT), random.randint(1, GRID_WIDTH))
            for _ in range(INITIAL_FOOD)]

    for _ in range(alive):
        agent = Agent(random.randint(1, GRID_HEIGHT), random.randint(1, GRID_WIDTH))
        agents.append(agent)
        agents_pos.append((agent.pos_x, agent.pos_y))

    while True:
        if len(food) < FOOD_THRESHOLD:
            extension = [(random.randint(1, GRID_HEIGHT), random.randint(1, GRID_WIDTH))
                         for _ in range(FOOD_ADDITION)]
            food.extend(extension)

        food, agents, agents_pos = simulate_process(food, agents, agents_pos)
        total_energy = 0
        avg_energy = 0

        for agent in agents:
            # agents_pos.append((agent.pos_x, agent.pos_y))
            total_energy += agent.energy

        try:
            avg_energy = total_energy / len(agents)
        except ZeroDivisionError:
            pass

        win.clear()

        for foo in food:
            win.addstr(foo[0], foo[1], "+", curses.color_pair(2))

        for agent in agents:
            if agent.energy <= 0:
                if agent.status:
                    agent.status = 0
                    agents.remove(agent)
                    agents_pos.remove((agent.pos_x, agent.pos_y))
                    alive -= 1
                    dead += 1
                elif agent.status == 0:
                    continue
            win.addstr(agent.pos_x, agent.pos_y, "O", curses.color_pair(1))

        update_status(win, alive, dead, avg_energy)

        win.refresh()
        curses.napms(DELAY_BETWEEN_STEPS)

    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    main()

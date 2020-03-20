fairway_section_dict = {}
fairway_section_list = []

trajectories_dict = {}

vessels = []
bridges = []
locks = []

network = None
environment = None
zoom = True
# Default dimensions for the visualisation pane
# Settings for the visualization
screen_x_min = 25
screen_x_max = 1000
screen_x_width = screen_x_max - screen_x_min
screen_y_min = 25
screen_y_max = 550
screen_y_width = screen_y_max - screen_y_min

node_x_min = float('inf')
node_x_max = float('-inf')
node_y_min = float('inf')
node_y_max = float('-inf')

x_min = 0
y_min = 0
x_max = 0
y_max = 0

import salabim as sim
from salabim import Animate

fairway_section_dict = {}
fairway_section_list = []

trajectories_dict = {}

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

queue_vessels_in_network = None
queue_vessels_waiting_bridge = None
queue_vessels_waiting_lock = None
queue_vessels_waiting_crossroad = None
num_vessels_finished = 0
num_vessels_failed = 0
queue_vessels_waiting_segment = None
num_vessels = 0
anim_num_vessels_in_network = None
anim_num_vessels_waiting_bridge = None
anim_num_vessels_waiting_lock = None
anim_num_vessels_waiting_crossroad = None
anim_num_vessels_finished = None
anim_num_vessels_waiting_segment = None
animate = True

crossroad_type = None

crossroad_stop_time = 2
crossroad_cyclic_delay = 5
crossroad_cyclic_inter_vessel_delay = 1
crossroad_cyclic_clear_time = crossroad_stop_time

lock_inout_time = 1
lock_wait_time = 15
lock_switch_time = 8

bridge_open_time = 5
bridge_pass_time = 1
bridge_min_wait = 10

seed = 0


def init():
    global queue_vessels_in_network
    global queue_vessels_waiting_lock
    global queue_vessels_waiting_segment
    global queue_vessels_waiting_crossroad
    global queue_vessels_waiting_bridge
    queue_vessels_in_network = sim.Queue(name="Vessels in network")
    queue_vessels_waiting_bridge = sim.Queue(name="Vessels waiting at bridges")
    queue_vessels_waiting_crossroad = sim.Queue(name="Vessels waiting at crossroad")
    queue_vessels_waiting_lock = sim.Queue(name="Vessels waiting at locks")
    queue_vessels_waiting_segment = sim.Queue(name="Vessels waiting at segments")


def update_counters():
    global anim_num_vessels_in_network
    global anim_num_vessels_waiting_bridge
    global anim_num_vessels_waiting_lock
    global anim_num_vessels_waiting_crossroad
    global anim_num_vessels_waiting_segment
    global anim_num_vessels_finished
    delta = x_max - x_min
    if anim_num_vessels_in_network is None:
        anim_num_vessels_in_network = Animate(text='Vessels: ' + str(len(queue_vessels_in_network)),
                                              textcolor0='black', x0=x_min + 0.7 * delta, y0=y_min + 0.6 * delta,
                                              fontsize0=4)
        anim_num_vessels_waiting_bridge = Animate(text='Vessels at bridges: ' + str(len(queue_vessels_waiting_bridge)),
                                                  textcolor0='black', x0=x_min + 0.7 * delta, y0=y_min + 0.55 * delta,
                                                  fontsize0=4)
        anim_num_vessels_waiting_lock = Animate(text='Vessels at locks: ' + str(len(queue_vessels_waiting_lock)),
                                                textcolor0='black', x0=x_min + 0.7 * delta, y0=y_min + 0.5 * delta,
                                                fontsize0=4)
        anim_num_vessels_waiting_crossroad = Animate(
            text='Vessels at crossroad: ' + str(len(queue_vessels_waiting_crossroad)),
            textcolor0='black', x0=x_min + 0.7 * delta,
            y0=y_min + 0.45 * delta,
            fontsize0=4)
        anim_num_vessels_waiting_segment = Animate(
            text='Vessels waiting at segment: ' + str(len(queue_vessels_waiting_segment)),
            textcolor0='black', x0=x_min + 0.7 * delta,
            y0=y_min + 0.4 * delta,
            fontsize0=4)
        anim_num_vessels_finished = Animate(text='Vessels finished: ' + str(num_vessels_finished),
                                            textcolor0='black', x0=x_min + 0.7 * delta,
                                            y0=y_min + 0.35 * delta,
                                            fontsize0=4)
    else:
        anim_num_vessels_in_network.update(text='Vessels: ' + str(len(queue_vessels_in_network)))
        anim_num_vessels_waiting_bridge.update(text='Vessels at bridges: ' + str(len(queue_vessels_waiting_bridge)))
        anim_num_vessels_waiting_lock.update(text='Vessels at locks: ' + str(len(queue_vessels_waiting_lock)))
        anim_num_vessels_waiting_crossroad.update(
            text='Vessels at crossroad: ' + str(len(queue_vessels_waiting_crossroad)))
        anim_num_vessels_waiting_segment.update(
            text='Vessels waiting at segment: ' + str(len(queue_vessels_waiting_segment)))
        anim_num_vessels_finished.update(text='Vessels finished: ' + str(num_vessels_finished))

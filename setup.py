import IO
import salabim as sim
import math
import simulation


def read_data():
    """ Read all the relevant data"""

    simulation.trajectories_dict = IO.read_trajectories()
    simulation.df_network = IO.read_network()
    simulation.df_bridges = IO.read_bridges()
    simulation.df_terminal = IO.read_terminals()
    simulation.df_passages = IO.read_passages()


def setup_scale():
    """ Setup draw dimensions"""
    draw_scale = simulation.draw_scale
    simulation.environment.animation_parameters(x0=3.140237*draw_scale, x1=3.371636*draw_scale, y0=50.794897*draw_scale)
    # geometry = simulation.df_network.geometry
    #
    # total_bounds = geometry.total_bounds
    # min_x = total_bounds[0]
    # min_y = total_bounds[1]
    # max_x = total_bounds[2]
    # max_y = total_bounds[3]
    #
    # diff_x = max_x - min_x
    # diff_y = max_y - min_y
    #
    # if diff_x > diff_y:
    #     scale = diff_x
    # else:
    #     scale = diff_y
    # simulation.environment.animation_parameters(x0=min_x, x1=min_x + scale, y0=math.floor(min_y))



def linestring_to_points(feature,line):
    return {feature:line.coords}


def draw_network():
    """ Draw the map"""
    draw_scale = simulation.draw_scale
    setup_scale()

    test = simulation.df_network.cascaded_union
    tmp = list(test.geoms)
    for line in tmp:
        xy = line.xy
        previous_x = None
        previous_y = None
        for x, y in zip(xy[0], xy[1]):
            if previous_x is not None:
                sim.AnimateLine(spec=(previous_x*draw_scale, previous_y*draw_scale, x*draw_scale, y*draw_scale), linewidth=0.005, linecolor="blue")
            previous_x = x
            previous_y = y
    # for line in tmp:
    #     xy = line.xy
    #     sim.AnimateLine(spec=(xy[0][0]*draw_scale, xy[1][0]*draw_scale,xy[0][int(len(xy[0]))-1]*draw_scale,xy[1][int(len(xy[1]))-1]*draw_scale), linewidth=0.005, linecolor="blue")
    for name, coord in simulation.trajectories_dict.items():
        sim.AnimateLine(spec=(coord.lon1*draw_scale, coord.lat1*draw_scale, coord.lon2*draw_scale, coord.lat2*draw_scale), linewidth=0.01, linecolor="red")

    for geometry in simulation.df_bridges.geometry:
        point = geometry.bounds
        sim.AnimateCircle(radius=0.005, x=point[0] * draw_scale, y=point[1] * draw_scale, fillcolor="purple")


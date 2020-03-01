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
    global xMin
    global yMin
    global xMax
    global yMax
    if simulation.zoomed:
        draw_scale = simulation.draw_scale
        xMin = 3.140237 * draw_scale
        yMin = 50.794897 * draw_scale
        xMax = 3.371636 * draw_scale
        yMax = yMin + (xMax - xMin)
    else:
        geometry = simulation.df_network.geometry
        total_bounds = geometry.total_bounds
        min_x = total_bounds[0]
        min_y = total_bounds[1]
        max_x = total_bounds[2]
        max_y = total_bounds[3]

        diff_x = max_x - min_x
        diff_y = max_y - min_y

        if diff_x > diff_y:
            scale = diff_x
        else:
            scale = diff_y
        xMin = min_x
        xMax = min_x + scale
        yMin = math.floor(min_y)
        yMax = yMin + scale

    simulation.environment.animation_parameters(x0=xMin, x1=xMax,
                                                y0=yMin)


def draw_network():
    """ Draw the map"""
    draw_scale = simulation.draw_scale
    setup_scale()

    test = simulation.df_network.cascaded_union
    tmp = list(test.geoms)
    if simulation.detailed_map:
        for line in tmp:
            xy = line.xy
            previous_x = None
            previous_y = None
            for x, y in zip(xy[0], xy[1]):
                if previous_x is not None:
                    if must_draw_line(previous_x * draw_scale, previous_y * draw_scale, x * draw_scale, y * draw_scale):
                        sim.AnimateLine(
                            spec=(previous_x * draw_scale, previous_y * draw_scale, x * draw_scale, y * draw_scale),
                            linewidth=0.005, linecolor="blue")
                previous_x = x
                previous_y = y
    else:
        for line in tmp:
            xy = line.xy
            sim.AnimateLine(spec=(xy[0][0] * draw_scale, xy[1][0] * draw_scale, xy[0][int(len(xy[0])) - 1] * draw_scale,
                                  xy[1][int(len(xy[1])) - 1] * draw_scale), linewidth=0.005, linecolor="blue")

    if simulation.draw_trajectories:
        for name, coord in simulation.trajectories_dict.items():
            if must_draw_line(coord.lon1 * draw_scale, coord.lat1 * draw_scale, coord.lon2 * draw_scale,
                              coord.lat2 * draw_scale):
                sim.AnimateLine(
                    spec=(
                    coord.lon1 * draw_scale, coord.lat1 * draw_scale, coord.lon2 * draw_scale, coord.lat2 * draw_scale),
                    linewidth=0.01, linecolor="red")

    for geometry in simulation.df_bridges.geometry:
        point = geometry.bounds
        if must_draw_point(point[0] * draw_scale, point[1] * draw_scale):
            sim.AnimateCircle(radius=0.005, x=point[0] * draw_scale, y=point[1] * draw_scale, fillcolor="purple")


def must_draw_line(x0, y0, x1, y1):
    if xMin < x0 < xMax and yMin < y0 < yMax:
        return True
    if xMin < x1 < xMax and yMin < y1 < yMax:
        return True
    return False


def must_draw_point(x0, y0):
    if xMin < x0 < xMax and yMin < y0 < yMax:
        return True
    return False

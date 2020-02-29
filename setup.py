import salabim as sim
import math


def setup_scale(env, geometry):
    """ Setup draw dimensions"""

    total_bounds = geometry.total_bounds
    minx = total_bounds[0]
    miny = total_bounds[1]
    maxx = total_bounds[2]
    maxy = total_bounds[3]

    diffx = maxx - minx
    diffy = maxy - miny

    if (diffx > diffy):
        scale = diffx
    else:
        scale = diffy

    env.animation_parameters(x0=minx, x1=minx + scale, y0=math.floor(miny))




def draw_network(env, df_network):
    """ Draw all the fairwaysegments"""

    setup_scale(env,df_network.geometry)

    for geometry in df_network.geometry:
        bounds = geometry.bounds
        sim.AnimateLine(spec=(bounds[0], bounds[1], bounds[2], bounds[3]), linewidth=0.005, linecolor="blue")

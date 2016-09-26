def set_viewer(viewer, query):
    """ 
    Helper hack because loading visualize
    breaks on some 14.04 instances
    """
    query.env.SetViewer(viewer)

    handles = []
    handles.append(draw_goal(query))
    handles.append(draw_sbounds(query))
    return handles

def saveQuery(filename):
    with(open(filename, 'w')) as f:
         f.write(yaml.dump(query.to_yaml()))


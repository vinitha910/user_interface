from state_updater import StateUpdater
from console import Module

class RunBackEnd():
    def runBackEnd(self, namespace):
        queryfiles=['../queries/bh280_practice1.query', '../queries/bh280_practice2.query',
                    '../queries/bh280_2movables.query', '../queries/bh280_2movables4.query',
                    '../queries/bh280_2movables.query', '../queries/bh280_2movables4.query',
                    '../queries/bh280_3movables.query', '../queries/bh280_3movables2.query',
                    '../queries/bh280_3movables.query', '../queries/bh280_3movables2.query',
                    '../queries/bh280_4movables.query', '../queries/bh280_4movables2.query',
                    '../queries/bh280_4movables.query', '../queries/bh280_4movables2.query',
                    '../queries/bh280_5movables.query', '../queries/bh280_5movables.query']
        path=None
        env = None
        robot = None
        
        m = Module()
        module, query = m.initialize_module(queryfiles[0], pathfile=path,     
                                            robot=robot, env=env)

        env = query.env
        robot = query.args[0]

        x = StateUpdater(robot,env,module,query,queryfiles,0,namespace)

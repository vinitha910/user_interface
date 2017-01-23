import rospy
import numpy
import openravepy
import json
import yaml

from datetime import datetime
from console import Module

# Import service messages
from user_interface.srv import *
from user_interface.msg import ReconfigurationObject
from std_msgs.msg import *

class ResetOnFailed():
    def __init__(self,env,module,state_o,control):
        self.env_ = env
        self.module = module
        self.state_original = state_o
        self.control = control
        
    def __enter__(self):
        self.state_original = self.module.GetState()

    def __exit__(self,*exc_info):
        state_new = self.module.GetState()
        if not state_new['valid']:
            self.module.SetState(self.state_original)
        else:
            addData(self.control)
            
class StateUpdater:   
    def __init__(self,robot,env,module,query,queryfiles,sceneNum,namespace):
        self.robot_ = robot
        self.env_ = env
        self.module = module
        self.query = query
        self.queryfiles = queryfiles
        self.sceneNum = sceneNum

        self.hand_off = 0
        self.target_off = 0
        self.hand_extents = [0.1195367166030446, 0.093081379275406051, 0.047751583158969879]
        self.target_extents = [0, 0, 0]
        self.bottle_radius = 0
        self.glass_radius = 0
        self.pop_tarts_extents = [0, 0, 0]
        self.pop_tarts_off = 0
        self.initialize = True 
        self.states = []

        self.startTime = None
        self.endTime = None
        self.data = dict()
        self.numReset = 0
        self.valMoves = 0
        self.invalMoves = 0

        self.namespace = namespace

        self.main()

    def main(self):
        rospy.init_node('user_interface_' + self.namespace)
        input_listener = rospy.Service("/" + self.namespace + '/input_to_state', InputToState, self.ConvertToState)
        table_listener = rospy.Service("/" + self.namespace + '/reconfiguration/gettableextents', GetTableExtents, self.get_table_extents)
        next_scene_listener = rospy.Service("/" + self.namespace + '/reconfiguration/nextscene', NextScene, self.next_scene)
        object_request_listener = rospy.Service("/" + self.namespace + '/reconfiguration/getobjects', GetObjectList, self.get_object_list)
        rospy.spin()
    
    def next_scene(self, req):
        self.endTime = datetime.now()

        if self.sceneNum == req.sceneNum:
            self.numReset = self.numReset + 1

        self.data[self.namespace] = {"Scene Number": self.sceneNum,
                                     "Time taken": str(self.endTime - self.startTime),
                                     "Number of Valid Moves": self.valMoves,
                                     "Number of Invalid Moves": self.invalMoves,
                                     "Number of Scene Resets": self.numReset}
        self.numReset = 0
        self.valMoves = 0
        self.invalMoves = 0
  
        with open('/home/ubuntu/results/path_S{}_{}.ompl'.format(self.sceneNum, self.namespace), 'w') as f:
            f.write(yaml.dump(self.states))
        self.states = []
        
        resp = NextSceneResponse()
        self.sceneNum = req.sceneNum

        for body in self.env_.GetBodies():
          self.env_.RemoveKinBody(body)

        if req.sceneNum < 16:
            path=None
            self.robot_ = None
            m = Module()
            self.module, self.query = m.initialize_module(self.queryfiles[self.sceneNum], pathfile=path,     
                                                                         robot=self.robot_, env=self.env_)
            self.env_ = self.query.env
            self.robot_ = self.query.args[0]
            self.initialize = True
            
        with open('/home/ubuntu/results/log_{}.json'.format(self.namespace), 'a') as outfile:
            json.dump(self.data, outfile)
            
        return resp

    def CheckMove(self, state_o, state_n, control):
        if not state_n[0]['valid']:
            self.module.SetState(state_o)
            self.invalMoves = self.invalMoves + 1
            return "False"
        else:
            controls = {'control': control, 'duration': 0.065, 'state': self.module.GetState()}
            self.states.append(controls)
            self.valMoves = self.valMoves + 1
            return "True"
        
    def ConvertToState(self, req):
        resp = InputToStateResponse()
        input = req.input
        state_o = self.module.GetState()

        if input == "":
            resp.validMove = "False"
        else:
            c = [float(x) for x in input.split(', ')]
            state_n = self.module.ExecuteTwist(c[0], c[1], c[2], c[3], stepsize=c[3])
            resp.validMove = self.CheckMove(state_o, state_n, c)

        hand_state = yaml.dump(self.module.GetState())

        return resp

    def get_table_extents(self, req):
        resp = GetTableExtentsResponse()
        x_max = self.query.kwargs['state_bounds']['high'][0]
        x_min = self.query.kwargs['state_bounds']['low'][0]
        y_max = self.query.kwargs['state_bounds']['high'][1]
        y_min = self.query.kwargs['state_bounds']['low'][1]
        resp.x = (x_max-x_min)/2
        resp.y = (y_max+y_min)/2
        resp.xextents = (x_max-x_min)/2
        resp.yextents = (y_max-y_min)/2
        resp.goalx = self.query.args[2][0]
        resp.goaly = self.query.args[2][1]
        resp.goalradius = self.query.kwargs['goal_epsilon']*1.2
        return resp

    def get_object_list(self, req):
        #rospy.loginfo('Getting object list')
        resp = GetObjectListResponse()

        resp.in_goal = False
        resp.num_objects = 0
        resp.objects = []
        bodyNum = 0

        for body in self.env_.GetBodies():
            body_name = body.GetName().lower()
            resp.num_objects += 1
            obj = ReconfigurationObject()
            s_pose = numpy.array([[0.,-1.,0.,0.],
                                  [0.,0.,1.,0.],
                                  [-1.,0.,0.,0.],
                                  [0.,0.,0.,1.]])
            s_inv = numpy.linalg.inv(s_pose)
            transform = body.GetTransform()
            q = transform[:3,:3]
            aa = openravepy.axisAngleFromRotationMatrix(q)
            state = self.module.GetState()
            obj_bb = body.ComputeAABB()

            if body_name == 'target':
                obj.type = 'target'
                obj.x = 1.0479 - state['movables'][bodyNum][0]
                obj.y = state['movables'][bodyNum][1]
                if self.initialize == True:
                    self.target_off = aa[2]
                    self.target_extents = [obj_bb.extents()[0], obj_bb.extents()[1], obj_bb.extents()[2]]
                obj.rot = state['movables'][bodyNum][2] + self.target_off
                obj.xextent = self.target_extents[0] 
                obj.yextent = self.target_extents[1]
                obj.zextent = self.target_extents[2]
                in_goal = self.module.CheckGoal(state)
                if in_goal:
                     resp.in_goal = True   
                bodyNum = bodyNum + 1
                
            elif body_name == 'fuze_bottle':
                obj.type = 'fuze_bottle'
                obj.x = state['movables'][bodyNum][0]
                obj.y = state['movables'][bodyNum][1]
                if self.initialize == True:
                    self.bottle_radius = obj_bb.extents()[0]
                obj.xextent = self.bottle_radius
                bodyNum = bodyNum + 1
                
            elif body_name in ['plastic_glass', 'plastic_glass2', 'plastic_glass3']:
                obj.type = 'plastic_glass'
                obj.x = state['movables'][bodyNum][0]
                obj.y = state['movables'][bodyNum][1]
                if self.initialize == True:
                    self.glass_radius = obj_bb.extents()[0]
                obj.xextent = self.glass_radius
                bodyNum = bodyNum + 1
                
            elif body_name in ['pop_tarts', 'pop_tarts2']:
                obj.type = 'pop_tarts'
                obj.x =  1.0479 - state['movables'][bodyNum][0]
                obj.y = state['movables'][bodyNum][1]
                if self.initialize == True:
                    self.pop_tarts_off = aa[2]
                    self.pop_tarts_extents = [obj_bb.extents()[0], obj_bb.extents()[1], obj_bb.extents()[2]]
                obj.rot = state['movables'][bodyNum][2] + self.pop_tarts_off
                obj.xextent = self.pop_tarts_extents[0] 
                obj.yextent = self.pop_tarts_extents[1]
                obj.zextent = self.pop_tarts_extents[2]
                bodyNum = bodyNum + 1
                
            elif body_name == 'bh280':
                obj.type = 'bh280'
                obj.x = state['manip'][0]
                obj.y = state['manip'][1]
                n_pose = body.GetTransform()
                now_in_start = numpy.dot(n_pose[:3,:3], s_inv[:3,:3])
                obj.rot = numpy.arctan2(now_in_start[1,0],now_in_start[0,0])
                if self.initialize == True:
                    self.hand_off = aa[2]
                    self.hand_extents = [obj_bb.extents()[0], obj_bb.extents()[1], obj_bb.extents()[2]]
                obj.xextent = self.hand_extents[0] 
                obj.yextent = self.hand_extents[1]
                obj.zextent = self.hand_extents[2]
                
            resp.objects.append(obj)

        if self.initialize:
            self.startTime = datetime.now()
            self.initialize = False

        return resp

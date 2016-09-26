cmake_minimum_required(VERSION 2.8.3)
project(user_interface)

find_package(catkin REQUIRED COMPONENTS
  openrave_catkin
  roscpp
  rospy
  std_msgs
  message_generation
)

catkin_python_setup()

## Generate messages in the 'msg' folder
 add_message_files(
   FILES
   ReconfigurationObject.msg
 )

## Generate services in the 'srv' folder
 add_service_files(
   FILES
   InputToState.srv
   GetTableExtents.srv
   GetObjectList.srv
   NextScene.srv
   ResetEnvironment.srv
 )

## Generate added messages and services with any dependencies listed here
 generate_messages(
   DEPENDENCIES
   std_msgs  # Or other packages containing msgs
 )

catkin_package(
   CATKIN_DEPENDS message_runtime
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)


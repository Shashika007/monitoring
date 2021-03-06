#!/usr/bin/env python

'''
   Copyright (c) 2018, University of Hannover
                       Institute for Systems Engineering - RTS
                       Professor Bernardo Wagner
 
   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions
   are met:
 
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.
    * Neither the name of Willow Garage, Inc. nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.
 
   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
   FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
   COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
   INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
   BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
   LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
   ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
   POSSIBILITY OF SUCH DAMAGE.
''' 


import rospy


from monitoring_core.monitor import Monitor
from nav_msgs.msg import OccupancyGrid

first_SLAM_map = True
old_SLAM_map = None
slam_total_changed_tiles = 0
slam_total_new_tiles = 0
slam_total_rewritten_tiles = 0

first_explorationPlanner_map = True
old_explorationPlanner_map = None
exploration_total_changed_tiles = 0
exploration_total_new_tiles = 0
exploration_total_rewritten_tiles = 0

monitor = Monitor("map_monitor")

def init():
     rospy.init_node("map_monitor", anonymous=False)

def subscribe():
    rospy.Subscriber("/map", OccupancyGrid, SLAM_map_callback)
    rospy.Subscriber("/ExplorationPlanner_GridMap", OccupancyGrid, explorationPlanner_map_callback)

def explorationPlanner_map_callback(msg):
    global first_explorationPlanner_map
    global old_explorationPlanner_map
    global exploration_total_changed_tiles
    global exploration_total_new_tiles
    global exploration_total_rewritten_tiles
    map_name = 'explorationPlanner_map'
    old_explorationPlanner_map, changed_tiles, new_tiles, rewritten_tiles = map_monitor(msg, map_name, first_explorationPlanner_map, old_explorationPlanner_map)
    exploration_total_changed_tiles += changed_tiles
    exploration_total_new_tiles += new_tiles
    exploration_total_rewritten_tiles += rewritten_tiles
    
    monitor.addValue(map_name+"/total_changed_tiles",str(exploration_total_changed_tiles), "", 0)
    monitor.addValue(map_name+"/total_new_discovered_tiles",str(exploration_total_new_tiles), "", 0)
    monitor.addValue(map_name+"/total_rewritten_tiles",str(exploration_total_rewritten_tiles), "", 0)
    monitor.publish()
    if first_explorationPlanner_map:
        first_explorationPlanner_map = False

def SLAM_map_callback(msg):
    global first_SLAM_map
    global old_SLAM_map
    global slam_total_changed_tiles
    global slam_total_new_tiles
    global slam_total_rewritten_tiles
    map_name = 'SLAM_map'
    old_SLAM_map, changed_tiles, new_tiles, rewritten_tiles = map_monitor(msg, map_name, first_SLAM_map, old_SLAM_map)
    slam_total_changed_tiles += changed_tiles
    slam_total_new_tiles += new_tiles
    slam_total_rewritten_tiles += rewritten_tiles
    
    monitor.addValue(map_name+"/total_changed_tiles",str(slam_total_changed_tiles), "", 0)
    monitor.addValue(map_name+"/total_new_discovered_tiles",str(slam_total_new_tiles), "", 0)
    monitor.addValue(map_name+"/total_rewritten_tiles",str(slam_total_rewritten_tiles), "", 0)
    monitor.publish()
    if first_SLAM_map:
        first_SLAM_map = False

def map_monitor(msg, map_name, first_map, old_map):
    """
    Compare the current map with the last update. Gather data on total changed tiles
    and tiles changed within the last update
    """
    map_size = len(msg.data)
    #print map_size
    #print len(old_map) + ""+ map_name
    changed_tiles = 0
    if first_map:
        first_map = False
        old_map = msg.data
        return old_map, changed_tiles,0,0
    l = len(old_map)
    if map_size != l:
        rospy.logerr("KACKE")
        return None, 0,0,0

    
    newly_discovered = 0
    rewritten_tiles = 0
    i = 0
    for element_new in msg.data:
        if element_new != old_map[i]:
            changed_tiles += 1
            if old_map[i] == -1:
                newly_discovered = newly_discovered + 1
        i += 1
    if changed_tiles != newly_discovered:
        rewritten_tiles = changed_tiles - newly_discovered
    print map_name + "/total tiles changed since last update: " + str(changed_tiles)
    print map_name + "/newly_discovered "+str(newly_discovered)
    print map_name + "/tiles rewritten: " + str(rewritten_tiles)
    monitor.addValue(map_name+"/changed_tiles",str(changed_tiles), "", 0)
    monitor.addValue(map_name+"/newly_discovered_tiles",str(newly_discovered), "", 0)
    monitor.addValue(map_name+"/rewritten_tiles",str(rewritten_tiles), "", 0)
    
    oldMap = msg.data
    return (oldMap, changed_tiles, newly_discovered, rewritten_tiles)

if __name__ == '__main__':
    init()
    subscribe()
    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        try:
            rate.sleep()
        except rospy.ROSInterruptException:
            rospy.loginfo("ERROR")
            pass

/*
 * stoplaunchfile.cpp
 *
 *  Created on: Dec 18, 2017
 *      Author: matthias
 */

#include "monitoring_fdir/recovery/std_handler/stoplaunchfile.h"

StopLaunchFile::StopLaunchFile() {
	// TODO Auto-generated constructor stub

}

StopLaunchFile::~StopLaunchFile() {
	// TODO Auto-generated destructor stub
}

/**
 * kills all started launchfiles to stop the programms.
 * Only use in emergencys.
 */
void StopLaunchFile::checkError(monitoring_msgs::Error msg) {
	ROS_ERROR("------------------- KILLING ALL ROSLAUNCH --------------------");
	char cmd[80];
	sprintf(cmd, "killall roslaunch");
	system (cmd);
}

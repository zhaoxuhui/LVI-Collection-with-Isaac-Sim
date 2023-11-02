import time

# 运行相关参数
imu_outpath = "/home/xuhui/imu_data.txt"        # IMU数据输出文件路径
imu_frequency = 500                     # IMU的观测频率
env_path = "/home/xuhui/Omniverse-Projects/sensor-lvi4.0.usd"	# 需要加载的场景和小车的usd文件
imu_prim_name = "/World/LVI_Sensor/Imu_Sensor"	# 场景文件中IMU传感器的Prim路径

# 启动Isaac Sim，对于Standalone方式而言是必须的
from omni.isaac.kit import SimulationApp
# 可以选择是否以headless模式运行
simulation_app = SimulationApp({"headless": False})

# 启用ros_bridge扩展
from omni.isaac.core.utils import extensions
extensions.enable_extension("omni.isaac.ros_bridge")

# 加载已有场景
from omni.isaac.core.utils.stage import open_stage
open_stage(usd_path=env_path)

# 添加世界
from omni.isaac.core import World
world = World()

# 根据参数设置IMU频率
from omni.isaac.core.utils.prims import get_prim_at_path
prim_imu = get_prim_at_path(imu_prim_name)
prim_imu.GetAttribute("sensorPeriod").Set(1/imu_frequency)

# 根据官方文档建议，添加完物体之后，最好重置刷新一下世界
world.reset()

# 构造接口，获取IMU数据
from omni.isaac.sensor import _sensor
_imu_sensor_interface = _sensor.acquire_imu_sensor_interface()

# 新建文件用于输出
fout = open(imu_outpath, "w")

flag = True

print("IMU Recoding in progress ...")

# 开启渲染
while simulation_app.is_running():
	world.step(render=True)
	
	if flag:
		start_time = time.time()
		flag = False
	imu_reading = _imu_sensor_interface.get_sensor_readings(imu_prim_name)

	# 解析IMU传感器数据
	if(len(imu_reading) != 0):
		for i in range(len(imu_reading)):
			tmp_imu_reading = imu_reading[i]
			data_timestamp = tmp_imu_reading[0]
			
			data_acc_x = tmp_imu_reading[1]
			data_acc_y = tmp_imu_reading[2]
			data_acc_z = tmp_imu_reading[3]

			data_ang_x = tmp_imu_reading[4]
			data_ang_y = tmp_imu_reading[5]
			data_ang_z = tmp_imu_reading[6]

			data_ori_x = tmp_imu_reading[7][0]
			data_ori_y = tmp_imu_reading[7][1]
			data_ori_z = tmp_imu_reading[7][2]
			data_ori_w = tmp_imu_reading[7][3]

			fout.write(str(data_timestamp) + " " + str(data_acc_x) + " " + str(data_acc_y) + " " + str(data_acc_z) + " " + str(data_ang_x) + " " + str(data_ang_y) + " " + str(data_ang_z) + " " + str(data_ori_x) + " " + str(data_ori_y) + " " + str(data_ori_z) + " " + str(data_ori_w) + "\n")

# cleanup and shutdown
fout.write("start time:"+str(start_time))
fout.close()
simulation_app.close()
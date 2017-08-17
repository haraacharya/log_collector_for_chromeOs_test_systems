import time
import datetime
import os
import pwd
import subprocess
from logcollectorlib import LogCollectorLib
import re
import multiprocessing

script_working_directory = os.getcwd()
log_collection_folder = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
os.makedirs(log_collection_folder)

test = LogCollectorLib()

#add the DUT ips to collect log from.
data = ['38.38.38.556735453', '38.38.38.2541', '38.38.38.2015', '38.38.38.1086', '38.38.38.239']
#process DUT ips and remove unreachable IPs
#data = [ip for ip in data if test.check_if_dut_is_live(ip)]
for ip in data[:]:	
	if test.check_if_dut_is_live(ip):	
		#running sshkeygen commands on the host to make the IPs ssh successfully
		print ip
		print "Update ssh-key knownhost to the ip for ssh to work without any issues."
		cmd = "ssh-keygen " + "-f " + "\"" + pwd.getpwuid(os.getuid()).pw_dir + "/.ssh/known_hosts\" " + "-R " + ip
		print cmd
		os.system(cmd)
	else:
		file = open(log_collection_folder + "/" + "log_dut_ip_" + ip + ".txt", "w") 
		file.write('DUT ip: %s is not pingable so not able to collect logs.' %(ip)) 
		file.close() 			
		data.remove(ip)

print "Ips to collect data from:", data

#Below method is not used because of new changes in generate_logs ..converted into c++ utility
def collect_logs_in_parallel((dut_ip)):
	print "collecting logs from: %s" % dut_ip
	test = LogCollectorLib()
	output = test.collect_dut_logs(dut_ip)
	print "output is", output
	if output:
		if self.run_command_on_dut("ls -l /home/chronos/user | grep -i Downloads", dut_ip):
			log_dir =  "/home/chronos/user/Downloads"
			print "log_dir is", log_dir
		else:
			log_dir =  "/tmp"
			print "log_dir is", log_dir
		for file in os.listdir(log_dir):
			if file.endswith(".tgz"):
				print(os.path.join(log_dir, file))
				dut_log_file_path = os.path.join(log_dir, file)
			elif file.endswith(".tar.gz"):
				print(os.path.join(log_dir, file))
				dut_log_file_path = os.path.join(log_dir, file)

		print dut_log_file_path
		return dut_log_file_path
	else:
		print "not able to collect logs"			
		return False

def collect_logs_in_parallel_new((dut_ip)):
#def collect_logs_in_parallel_new(dut_ip):
	print "collecting logs from: %s" % dut_ip
	dut_log_file_name = "log_dut_ip_" + dut_ip + ".tgz"
	#out = subprocess.check_output(["ssh-keygen", "-f", "\"" + pwd.getpwuid(os.getuid()).pw_dir + "/.ssh/known_hosts\"", "-R", dut_ip])
	#print out
	output = test.collect_dut_logs(dut_ip)
	print "output is", output
	if output:
		test.copy_file_from_dut_to_host(output, log_collection_folder + "/" + dut_log_file_name, dut_ip )
		print "DUT %s system_log copied to: %s, log_name: %s" % (dut_ip, log_collection_folder, dut_log_file_name)
	else:
		print "not able to collect logs"
		file = open(log_collection_folder + "/" + dut_log_file_name, dut_ip, "w") 
		file.write('Not able to collect logs from dut: %s' %(dut_ip)) 
		file.close() 			
		return False
	

def collect_logs_handler():
    p = multiprocessing.Pool(4)
    p.map(collect_logs_in_parallel_new, data)

if __name__ == "__main__":
	collect_logs_handler()
	#for ip in data:
	#	print ip
	#	collect_logs_in_parallel_new(ip)		



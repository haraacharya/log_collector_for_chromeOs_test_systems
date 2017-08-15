import paramiko
import os
import time
import re
import subprocess

class LogCollectorLib(object):
		
	def run_command_on_dut(self, command, dut_ip):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(dut_ip, username='root', password='test0000')
		stdin, stdout, stderr = client.exec_command(command)
		command_exit_status = stdout.channel.recv_exit_status()
		out= stdout.read()
		print "out is: ", out
		"""
		while not stdout.channel.exit_status_ready():
		    	# Only print data if there is data to read in the channel
		    	if stdout.channel.recv_ready():
				rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
				if len(rl) > 0:
			   		# Print data from stdout
			    		print stdout.channel.recv(1024),
		
			print "Command done."
		"""
		client.close()
		if command_exit_status == 0:
			return out
		else:
			#print "not able to run the command remotely"
			return False	

	def copy_file_from_host_to_dut(self, src,dst, dut_ip):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(dut_ip, username='root', password='test0000')

		sftp = client.open_sftp()
		sftp.put(src, dst)		
		sftp.close()

		if self.run_command_on_dut("ls -l " + dst, dut_ip):	
			print ("File copy successfull")	
			return True
		else:
			print ("File copy unsuccessfull")	
			return False

	def copy_file_from_dut_to_host(self, src,dst, dut_ip):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(dut_ip, username='root', password='test0000')

		sftp = client.open_sftp()
		sftp.get(src, dst)		
		sftp.close()

		if os.path.isfile(dst):	
			print ("File copy successfull")	
			return True
		else:
			print ("File copy unsuccessfull")	
			return False


	def check_if_dut_is_live(self, dut_ip):
		hostname = dut_ip #example
		response = os.system("ping -c 1 " + hostname)

		#and then check the response...
		if response == 0:
			return True
		else:
			return False

	def wait_for_dut_to_come_back_on(self, minutes, dut_ip):
		minutes = int(minutes)
		t_end = time.time() + 60 * minutes
		while time.time() < t_end:
	    		if self.check_if_dut_is_live(dut_ip):
				return True
		return False

	
	def collect_dut_logs(self, dut_ip):
		if self.check_if_dut_is_live(dut_ip):
			print "Deleting existing generate_log file if any."
			if self.run_command_on_dut("ls -l /tmp/*.tgz", dut_ip):
				self.run_command_on_dut("rm -rf /tmp/*.tgz", dut_ip)

			log_path = "/home/chronos/log_dut_ip_" + dut_ip + ".tgz"
			out = subprocess.check_output(["sshpass", "-p", "test0000", "ssh", "-o", "StrictHostKeyChecking=no", "root@"+ dut_ip,"\'generate_logs\'", "--output=" + log_path])
			if self.run_command_on_dut("ls -l " + log_path, dut_ip):
				print "log_path is:", log_path
				return log_path
			else:
				print "generate_logs couldn't generate logs"
				return False
		else:
			print "DUT %s is not up" % dut_ip
			return False
			
	







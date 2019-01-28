"""
@Author		:Furqan Khan
@Email		:furqankhan08@gmail.com
@Date 		:1/3/2017

Objective :
The purpose of this file /module /Class is to actually interact with the web service.Actually this is the
class which would merge all the mannual ,nessus and qualys findinds which are all stored in the database table for the project id passed.
Finally after the merging is over then depending upon the type of report the user wants ,this module/class 
invokes the Report_Printer module and that module is responsible for printing the report in various formats and then returning the actaull file for download.

"""

import Qualys_parser
import Nessus_parser
import IPexploits
import itertools
import Report_Generator
import Report_printer
import os
import json
import zipfile
class Report_merger:
	"""
	Objective :
	This class will actually merge the qualys mannual and nessus findings into 1 consolidated report
	"""
	def __init__(self,Nessus_report=False,Qualys_report=False):
		"""
		Objective :
		This method is the constructor of the class.
		"""
		self.Nessus_report=Nessus_report
		self.Qualys_report=Qualys_report
		self.nessus_all_hosts=[]
		self.mannual_all_hosts=[]	
		self.qualys_all_hosts=[]
		self.nessus_extra_hosts=[]
		self.qualys_extra_hosts=[]
		self.mannual_extra_hosts=[]
		self.mannual_host_port=[]
		self.nessus_host_port=[]
		self.qualys_host_port=[]
		self.mannual_extra_port_per_host=[]
		self.nessus_extra_port_per_host=[]
		self.qualys_extra_port_per_host=[]
		self.rp=Report_printer.Report_printer()
		self.folder_dir=os.path.dirname(os.path.realpath(__file__))
		self.results_path=os.path.join(self.folder_dir,"Results")
		#print "\n\nResult path is : "+str(results_path) 
		self.folder_name=os.path.join(self.results_path,"Data_")

			
	def init_project_directory(self,project_id):
		"""
		Objective :
		This method is used to initialise the project directory where the final download file would 
		be saved for json type result.For all the other types this project directory is created and
		initialized inside the Report_printer module
		"""
		
		print "Initialising parent directory "
		try:
			if not os.path.exists(self.folder_name+str(project_id)):
				os.mkdir(self.folder_name+str(project_id))
				s_path=os.path.join(self.results_path,'bk')
				#d_path=os.path.join(self.results_path,'bk')	
				
				os.system("cp -r "+s_path+ " "+ self.folder_name+str(project_id)+"/")

			self.data_path=self.folder_name+str(project_id)
			return 1;
		except Exception ,ee:
			#self.print_Error("Error while creating directory !!"+str(ee))
			print "EX "+str(ee)
			return -1

		
	def generate_report(self,project_id,format_):
		"""
		Objective :
		This method is used to invoke the Report_printer module and would pass on the report merged content 
		to it.The Report_printer module would print the content and would return the zipped folder where
		the final report would be present.The zipped folder is shared back with the webservice which can be
		further passed back to the web application. 
		Only of the report type is json ,the final report content is merged in this module only and 
		the zipped folder is also created here only.
		"""
		try:
			mannual_results=None
			mannual=IPexploits.IPexploits()
			mannual_results=mannual.generate_report_GUI(project_id)
			report_content=self.start_merging(mannual_results,self.Nessus_report,self.Qualys_report,project_id)
			if report_content:
				print "format is :"+str(format_)
				if format_=="html":
					#with open("test.json","w") as f:
					#	json.dump(report_content,f,sort_keys=True,indent=4)
					val=self.rp.generate_html(report_content,project_id)
					#print val
					return val
				elif format_=="xml":
					val=self.rp.generate_xml(report_content,project_id)
					print val
					return val
				elif format_ =="csv":
					print "in csv 1"
					val=self.rp.generate_csv(report_content,project_id)
					print val
					return val
				elif format_=="json":
					r=self.init_project_directory(project_id)
					if r !=-1:
						self.data_path=self.folder_name+str(project_id)
						report_file=str(project_id)+"__report.json"
						report_file_path = os.path.join(self.data_path, report_file)
			
						with open(report_file_path,"w") as f:
							json.dump(report_content,f,sort_keys=True,indent=4)

						zip_folder_name="Data_json_"+str(project_id)+".zip"
						zip_folder_creation_path=os.path.join(self.results_path,zip_folder_name)
						zip_folder_path=self.data_path #file to be zipped
						zipf=zipfile.ZipFile(zip_folder_creation_path,'w',zipfile.ZIP_DEFLATED)
						self.rp.zipdir(zip_folder_path,zipf,report_file,"json")
						zipf.close()
						ret_resp={}
						ret_resp["status"]="success"
						ret_resp["value"]=zip_folder_creation_path
						print ret_resp
						return ret_resp

					else:
						ret_resp={}
						ret_resp["status"]="failure"
						ret_resp["value"]="Some error occured while creating the directory"
						print ret_resp
						return ret_resp

						

		except Exception,ee:
			print "Exception caught :"+str(ee)

	def start_merging(self,mannual_results=None,nessus=False,qualys=False,project_id=0):
		"""
		Objective :
		This method is used to apppend nessus and qualys findings to teh mannual results.
		Thus the idea is thet the mannual results are traversed and for the mannual host and port
		it is checked if nessus results are present for mannual host and port ,if yes then they are merged
		in disctionary as nessus_findings and qualys_findings (for current host port)
		Same holds for nessus only ,qualys only ,both qualys and nessus .
		Same holds at host level also.
		Thus the final amalgmated report is returned.
		"""
		
		try:
			rep_obj=Report_Generator.ReportGenerator()
			report_template=[]
			service_count_matched=0
			parent_dict_mannual=mannual_results["value"]
			if parent_dict_mannual:
				print "\n\n"
				#print str(parent_dict_mannual)
				for host_items in parent_dict_mannual: #Mannual hosts
						report_item={}
						print str(host_items["host"])
						host=host_items["host"]
						report_item["host"]=host
						report_item["status"]="all"
						
						#is_host_in_nessus=is_host_present_nessus(host,nessus_results)
						if 1: #host not in (self.mannual_extra_hosts): #it would mean host is in m and either of (n and q)
							details_mannual=[]
							details_mannual=host_items["value"]
							findings=[]
							if details_mannual: 
															
								for items in details_mannual:
										found_item={}
										found_item["status"]="all"
										port=items["port"]
										service_nmap=items["service"]
										found_item["port"]=port
										found_item["service_nmap"]=service_nmap
										found_item["nessus"]=''
										found_item["qualys"]=''
										found_item['mannual']=items['exploits']
										
										details_nessus=rep_obj.get_details(int(project_id),host,port,'nessus')
										if details_nessus["status"]=="success":
											found_item["nessus"]=details_nessus["value"]
											service_count_matched=service_count_matched+1
											
										details_qualys=rep_obj.get_details(int(project_id),host,port,'qualys')
										if details_qualys["status"]=="success":
											found_item['qualys']=details_qualys['value']
											
										findings.append(found_item)

							missed_nessus=rep_obj.get_missed_mannual_ports(int(project_id),host,'nessus')
							if missed_nessus["status"]=="success":
								findings.append({'status':'nessus_only','value':missed_nessus["value"]})
							missed_qualys=rep_obj.get_missed_mannual_ports(int(project_id),host,'qualys')
							if missed_qualys["status"]=="success":
								findings.append({'status':'qualys_only','value':missed_qualys["value"]})
							missed_both=rep_obj.get_missed_mannual_ports(int(project_id),host,'both')
							if missed_both["status"]=="success": #context=nessus
								findings.append({'status':'both','value':missed_both["value"]})
							report_item["value"]=findings
							report_template.append(report_item)

			#print "The total number of services for host under test:"+str(ser)
			print "Mannual context-->The service count matched with nessus :"+str(service_count_matched)
			print "\n\n\n\n\nReport template :\n\n\n\n"
			
			nessus_hosts_only=rep_obj.get_missed_hosts(int(project_id),'nessus')
			if nessus_hosts_only["status"]=="success":
				nessus_hosts=nessus_hosts_only["value"]
				findings=[]
				for hosts in nessus_hosts:
					report_item={}
					report_item["host"]=str(hosts)
					missed_nessus=rep_obj.get_missed_mannual_ports(int(project_id),hosts,'nessus')
					if missed_nessus["status"]=="success":
						report_item["value"]=missed_nessus["value"]
						report_item["status"]="nessus_only"
						report_template.append(report_item)
			
			qualys_hosts_only=rep_obj.get_missed_hosts(int(project_id),'qualys')
			if qualys_hosts_only["status"]=="success":
				qualys_hosts=qualys_hosts_only["value"]
				findings=[]
				for hosts in qualys_hosts:
					report_item={}
					report_item["host"]=str(hosts)
					missed_qualys=rep_obj.get_missed_mannual_ports(int(project_id),hosts,'qualys')
					if missed_nessus["status"]=="success":
						report_item["value"]=missed_qualys["value"]
						report_item["status"]="qualys_only"
						report_template.append(report_item)

			b_hosts_only=rep_obj.get_missed_hosts(int(project_id),'both')
			if b_hosts_only["status"]=="success":
				b_hosts=b_hosts_only["value"]
				findings=[]
				for hosts in b_hosts:
					report_item={}
					report_item["host"]=str(hosts)
					missed_b=rep_obj.get_missed_mannual_ports(int(project_id),hosts,'both')
					if missed_b["status"]=="success":
						report_item["value"]=missed_b["value"]
						report_item["status"]="both"
						report_template.append(report_item)
					

			print "Final report template is :"
			return report_template
			#print str(report_template)
		except Exception ,ee:
				print "Exception caught --> "+str(ee)



#obj=Report_merger(True,True)
#obj.generate_report('246','json')










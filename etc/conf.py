# db connect url
sql_connection = "mysql+mysqlconnector://charging:charging@10.200.100.8/charging?charset=utf8"
sql_connection_worder = "mysql+mysqlconnector://worder:charging@10.200.100.11/worder?charset=utf8"
sql_connection_sia = "mysql+mysqlconnector://sia:sia@172.16.68.220/sia?charset=utf8"


# cmdb orders sync's end point
cmdb_ep = ""
# admin user
username = "admin"
# admin password
password = ""
# tenant
tenant = "admin"
# keystone enpoint
keystone_admin_endpoint = "http://10.200.100.8:5000/v2.0"
# sync time
sync_time_in = [0,]
# floating ip
floting_ip = "172.16.68.75"
# sia api port
sia_port = 8901

from sshtunnel import SSHTunnelForwarder
server = SSHTunnelForwarder(
    '156.111.80.32',
    ssh_username="sdc",
    ssh_password="nyspimri",
    remote_bind_address=('10.20.193.112', 8080)
)

server.start()

print(server.local_bind_port)

server.stop()
#!/usr/bin/python3
from fabric import task
from fabric import Connection
from datetime import datetime
import os

# Define the hosts, user, and key filename
env_hosts = ['54.91.80.128', '54.90.94.220']
env_user = 'ubuntu'
env_key_filename = '/home/ubuntu/.ssh/id_rsa'

@task
def do_pack(c):
    """Generates a .tgz archive from the contents of the web_static folder."""
    os.makedirs('versions', exist_ok=True)
    date = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_path = "versions/web_static_{}.tgz".format(date)
    result = c.local("tar -cvzf {} web_static".format(archive_path))
    if result.failed:
        return None
    return archive_path

@task
def do_deploy(c, archive_path):
    """Distributes an archive to the web servers."""
    if not os.path.exists(archive_path):
        return False

    try:
        file_name = os.path.basename(archive_path)
        file_without_ext = os.path.splitext(file_name)[0]

        c.put(archive_path, "/tmp/")
        c.run("mkdir -p /data/web_static/releases/{}/".format(file_without_ext))
        c.run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".format(file_name, file_without_ext))
        c.run("rm /tmp/{}".format(file_name))
        c.run("mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/".format(file_without_ext, file_without_ext))
        c.run("rm -rf /data/web_static/releases/{}/web_static".format(file_without_ext))
        c.run("rm -rf /data/web_static/current")
        c.run("ln -s /data/web_static/releases/{}/ /data/web_static/current".format(file_without_ext))
        print("New version deployed!")
        return True
    except Exception as e:
        return False

@task
def deploy(c):
    """Deploys the web static files."""
    archive_path = do_pack(c)
    if not archive_path:
        return False
    return do_deploy(c, archive_path)

@task
def deploy_all(c):
    """Deploys to all hosts."""
    for host in env_hosts:
        conn = Connection(host=host, user=env_user, connect_kwargs={"key_filename": env_key_filename})
        deploy(conn)


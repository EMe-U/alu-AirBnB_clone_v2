#!/usr/bin/python3
"""
Fabric script that creates and distributes an archive to web servers.
"""

from fabric import Connection
from datetime import datetime
from os.path import exists

Connection = ['54.91.80.128', '54.90.94.220']  


def do_pack():
    """
    Generates a .tgz archive from the contents of the web_static folder.

    Returns:
        str: The path to the created archive if successful, otherwise None.
    """
    time_stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    local("mkdir -p versions")
    archive_path = "versions/web_static_{}.tgz".format(time_stamp)
    local("tar -cvzf {} web_static".format(archive_path))

    if exists(archive_path):
        return archive_path
    return None


def do_deploy(archive_path):
    if not os.path.exists(archive_path):
        return False
    
    try:
        file_name = archive_path.split("/")[-1]
        name = file_name.split(".")[0]
        path_name = f"/data/web_static/releases/{name}"

        conn = Connection(host="your-server-ip", user="ubuntu")

        conn.put(archive_path, "/tmp/")
        conn.run(f"mkdir -p {path_name}/")
        conn.run(f"tar -xzf /tmp/{file_name} -C {path_name}/")
        conn.run(f"rm /tmp/{file_name}")
        conn.run(f"mv {path_name}/web_static/* {path_name}/")
        conn.run(f"rm -rf {path_name}/web_static")
        conn.run("rm -rf /data/web_static/current")
        conn.run(f"ln -s {path_name}/ /data/web_static/current")
        
        return True
    except Exception as e:
        print(e)
        return False

def deploy():
    """
    Creates and distributes an archive to web servers.

    Returns:
        bool: True if deployment succeeds, False otherwise.
    """
    archive_path = do_pack()
    if not archive_path:
        return False

    return do_deploy(archive_path)

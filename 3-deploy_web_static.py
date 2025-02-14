#!/usr/bin/python3
"""
Fabric script that creates and distributes an archive to web servers.
"""

from fabric import Connection, task
from datetime import datetime
import os

# List of servers
servers = ['54.91.80.128', '54.90.94.220']


def do_pack():
    """
    Generates a .tgz archive from the contents of the web_static folder.

    Returns:
        str: The path to the created archive if successful, otherwise None.
    """
    time_stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    os.system("mkdir -p versions")
    archive_path = f"versions/web_static_{time_stamp}.tgz"
    os.system(f"tar -cvzf {archive_path} web_static")

    if os.path.exists(archive_path):
        return archive_path
    return None


def do_deploy(archive_path):
    """
    Deploys the archive to the web servers.
    
    Args:
        archive_path (str): The path to the archive file.

    Returns:
        bool: True if successful, False otherwise.
    """
    if not os.path.exists(archive_path):
        return False

    try:
        file_name = archive_path.split("/")[-1]
        name = file_name.split(".")[0]
        remote_path = f"/data/web_static/releases/{name}"

        for server in servers:
            conn = Connection(host=server, user="ubuntu")

            # Upload archive
            conn.put(archive_path, "/tmp/")

            # Create release folder
            conn.run(f"mkdir -p {remote_path}")

            # Unpack archive
            conn.run(f"tar -xzf /tmp/{file_name} -C {remote_path}")

            # Remove archive from /tmp
            conn.run(f"rm /tmp/{file_name}")

            # Move files to proper location
            conn.run(f"mv {remote_path}/web_static/* {remote_path}/")

            # Remove empty directory
            conn.run(f"rm -rf {remote_path}/web_static")

            # Update symlink
            conn.run("rm -rf /data/web_static/current")
            conn.run(f"ln -s {remote_path} /data/web_static/current")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def deploy():
    """
    Creates and distributes an archive to web servers.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    archive_path = do_pack()
    if not archive_path:
        return False
    return do_deploy(archive_path)

#!/usr/bin/python3
"""
Fabric script that creates and distributes an archive to web servers.
"""

from fabric.api import local, put, run, env
from datetime import datetime
from os.path import exists

env.hosts = ['<IP web-01>', '<IP web-02>']  # Replace with actual server IPs


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
    """
    Distributes an archive to web servers and deploys it.

    Args:
        archive_path (str): Path to the archive file.

    Returns:
        bool: True if deployment succeeds, False otherwise.
    """
    if not exists(archive_path):
        return False
    try:
        file_name = archive_path.split("/")[-1]
        name = file_name.split(".")[0]
        path_name = "/data/web_static/releases/" + name
        put(archive_path, "/tmp/")
        run("mkdir -p {}/".format(path_name))
        run('tar -xzf /tmp/{} -C {}/'.format(file_name, path_name))
        run("rm /tmp/{}".format(file_name))
        run("mv {}/web_static/* {}".format(path_name, path_name))
        run("rm -rf {}/web_static".format(path_name))
        run('rm -rf /data/web_static/current')
        run('ln -s {}/ /data/web_static/current'.format(path_name))
        return True
    except Exception:
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

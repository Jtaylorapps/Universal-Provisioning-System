import pip
from subprocess import call

for dist in pip.get_installed_distributions():
    call("pip --proxy=http://proxy.statestr.com install --upgrade " + dist.project_name, shell=True)
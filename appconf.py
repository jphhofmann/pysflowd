from configparser import ConfigParser

# Read config
global config
config=ConfigParser()
config.read("/etc/pysflowd.conf")

# Configuration values for the OpenGalaxy machines
# Select config-file directed by OPTIONAL (INI file): /etc/sysconfig/ef-config ef_variant= line.
# File should: have no [section] header, use "# " comments, var="val" (no spaces around =),
# no dash in var-names, for good compatibility between python and bash.
#
# default if fail to read/parse the etc file is STAGING. These values:
#          ef_variant=DEV       ef_variant=STAGING       ef_variant=PROD
# yield respectively:
#    import config_DEV import config_STAGING import config_PROD
#
# Survive (try:) missing,improper,unreadable /etc/sysconfig/ef-config.
# DO NOT survive (no try:) failed imports (non-existent file, bad syntax, etc.).

#
# look-up ef_variant=... in optional etc file, default to STAGING
#
import configparser
#TODO: replace path with PREFIX
apps_path="/usr/share/pdk/bin"
#apps_path="PREFIX/pdk/bin"

config = configparser.ConfigParser(strict=False, allow_no_value=True)
try:
    config.read_string("[null]\n"+open("/etc/sysconfig/ef-config").read())
except:
    pass
ef_variant = config.get('null','ef_variant', fallback='STAGING').strip('\'"')

#
# emulate: import config_<ef_variant>
#
#cfgModule = __import__("config_"+ef_variant)
#globals().update(vars(cfgModule))

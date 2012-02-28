import sys
import subprocess
from subprocess import Popen, PIPE
import re
from optparse import OptionParser

parser = OptionParser()
usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)

parser.add_option("-f", "--from",
                  help="date to restrict search from. you can use the form yyyy-mm-dd.",
		  dest="from_date")

parser.add_option("-t", "--to",
                  help="date to restrict search from. you can use the form yyyy-mm-dd.",
		  dest="to_date")

parser.add_option("-d", "--directory", dest="directory",
                  help="directory to diff.  if not specified, all directories assumped.", metavar="FILE")

(options, args) = parser.parse_args()
cmd = "hg log . --date \"" + options.from_date + " to " + options.to_date + "\""
p = Popen(cmd, cwd=options.directory, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()

matches = re.findall(r'changeset:(.+)\nuser:(.+)\ndate:.+\nsummary:(.+)', stdout)

def isBugIgnorable(match):
    summary = match[2].lower()
    if summary.find("backout") != -1 or summary.find("back out") != -1 or summary.find("backed out") != -1:
        return True

    if summary.find("bug") != -1 and summary.find("r=") != -1:
        return True

    # check build user
    if match[1].find("ffxbld") != -1:
        return True

    return False

developers = {}

for match in matches:
    if isBugIgnorable(match):
        continue

    # flatten out the data and group by developer
    developer = match[1].strip();
    if developers.has_key(developer) == False:
        developers[developer] = ""

    current = developers[developer]
    developers[developer] = current + match[0].strip() + "\n  " + match[2].strip() + "\n"


print "=========================================="
print "No-Bugz-No-Reviews Report"
print "directory: " + options.directory
print "from: " + options.from_date
print "to: " + options.to_date
print "=========================================="
print ""

for index in enumerate(developers):
    print index[1]
    print "=========================================="
    print developers[index[1]]




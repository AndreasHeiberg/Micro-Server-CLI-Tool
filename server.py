#!/usr/bin/python
import sys, getpass, subprocess, os, shutil, getopt, re

sys.path.insert(0, './lib')

from getch import getch
from termcolor import colored, cprint
from tempfile import mkstemp

def prompt_bool(question, default = False):
	true = ["y", "yes"]
	false = ['n', "no"]

	if default == None:
		prompt = " [y/n]: "
	elif default == True:
		prompt = " [Y/n]: "
	elif default == False:
		prompt = " [y/N]: "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		sys.stdout.write(colored(question + prompt, 'grey', 'on_blue'))
		choice = getch().lower()
		print choice
		if default is not None and choice == '':
			return default
		elif choice in true:
			return True
		elif choice in false:
			return False
		elif choice in ['c', 'q']:
			sys.exit()
		else:
			cprint("Please respond with 'yes' or 'no' (or 'y' or 'n').", 'grey', 'on_red')

def file_append(file_path, content):
	source_file = open(file_path, 'a')
	source_file.write(content)
	source_file.close()

def file_search_replace(file_path, pattern, subst, in_ram=False):
	#Create temp file
	fh, abs_path = mkstemp()
	new_file = open(abs_path,'w')
	old_file = open(file_path)

	if in_ram:
		old_file = old_file.read()
		new_file.write(re.sub(pattern, "", old_file))
	else:
		for line in old_file:
			new_file.write(line.replace(pattern, subst))

		old_file.close()

	#close temp file
	new_file.close()
	os.close(fh)

	#Remove original file
	os.remove(file_path)

	#Move new file
	shutil.move(abs_path, file_path)

def setup_server():
	if prompt_bool("Install git?"):
		subprocess.call(['yum install git -y'], shell=True)

	if prompt_bool("Install zsh?"):
		subprocess.call(['sudo yum install zsh -y'], shell=True)
		subprocess.call(['usermod -s /bin/zsh ' + getpass.getuser()], shell=True)

	if prompt_bool("Install oh-my-zsh?"):
		subprocess.call(['curl -L https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh | sh'], shell=True)

	if prompt_bool("Setup oh-my-zsh?"):
		#change theme
		zshrcfile = os.path.expanduser("~") + '/.zshrc'
		file_search_replace(zshrcfile, 'ZSH_THEME="robbyrussell"', 'ZSH_THEME="agnoster"')

def project_make(name):
	# name = 'facebook.com'
	# create /var/www/facebook.com
	subprocess.call(['mkdir -p /var/www/' + name], shell=True)

	# create index.html
	subprocess.call(['echo Hello ' + name + '> /var/www/' + name + '/index.html'], shell=True)

	# setup the virtual host
	vhost = """
<VirtualHost *:80>
    ServerAdmin admin@{name}
    DocumentRoot /var/www/{name}
    ServerName {name}
    ErrorLog logs/{name}-error_log
    CustomLog logs/{name}-access_log common
</VirtualHost>""".format(name=name)

	file_append('/etc/httpd/conf/httpd.conf', vhost)

	# restart apache
	subprocess.call(['sudo apachectl -k stop', 'sudo /etc/init.d/httpd start'], shell=True)

	# setup git
	if prompt_bool("Would you like to use git?"):
		repo = re.match(r"^(.*)[\.]", name).group(0) + 'git'
		# create /var/repo/facebook.git
		subprocess.call(['mkdir -p /var/repo/' + repo], shell=True)

		# crete a bare repo
		# setup hooks
		subprocess.Popen(['git init --bare', "#!/bin/sh\ngit --work-tree=/var/www/" + name + " --git-dir=/var/repo/" + repo + " checkout -f > post-receive", 'chmod +x post-receive'], cwd=r'/var/repo/' + repo, shell=True)

		print ''
		print 'Please add the repo as a remote to your local repo';
		print 'git remote add live ssh://' + getpass.getuser() + '@' + name + '/var/repo/' + repo	
		print ''	

	cprint('Project was made', 'grey', 'on_green')

def project_delete(name):
	# name = 'facebook.com'
	# delete /var/www/facebook.com
	subprocess.call(['rm -r /var/www/' + name], shell=True)

	# delete /var/repo/facebook.git
	repo = re.match(r"^(.*)[\.]", name).group(0) + 'git'
	subprocess.call(['rm -r /var/repo/' + repo], shell=True)

	# delete the virtual host
	pattern = re.compile(r'<VirtualHost \*:[0-9]*>(?:.(?!</VirtualHost))*?ServerName +' + name + '(?:(?!</VirtualHost).)*?</VirtualHost>', re.DOTALL)
	file_search_replace('/etc/httpd/conf/httpd.conf', pattern, '', True)
	
	# restart apache
	subprocess.call(['sudo apachectl -k stop', 'sudo /etc/init.d/httpd start'], shell=True)

	cprint('Project was deleted', 'grey', 'on_green')





# ====================================
# Main program
# ====================================

argv = sys.argv[1:]

if 'project:make' in argv:
	if '-h' in argv:
		print 'server.py project:make <name>'
		sys.exit(2)
	else:
		project_make(argv[1])
elif 'project:delete' in argv:
	if '-h' in argv:
		print 'server.py project:delete <name>'
		sys.exit(2)
	else:
		project_delete(argv[1])
elif 'setup' in argv:
	if '-h' in argv:
		print 'server.py setup'
		sys.exit(2)
	else:
		setup_server()
else:
	print 'server.py setup [-h]'
	print 'server.py project:make <domain> [-h]'
	print 'server.py project:delete <domain> [-h]'
	sys.exit(2)
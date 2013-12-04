Micro Server Setup CLI Tool
===
I'm tired of setting up VPS's for clients, but can't really move to a more managed solution for various reasons. For this reason I created a script that replicates what I would typically do manually. It asks you easy to understand yes or no questions for everything you might want configure in my standard setup.

There are three commands:
	
	server.py setup [-h]
	server.py project:make <domain> [-h]
	server.py project:delete <domain> [-h]

Setup
---
Install git? [y/N]
Install zsh? [y/N]
Install oh-my-zsh? [y/N]
Setup oh-my-zsh?  [y/N]

Project make
---
Creates a folder for the project with a index.html
Configures Virtual Hosts
Restart apache
Would you like to use git? [y/N]
	Creates git repo that places any pushed file to the project folder

import os

folder = 'datasets-3/'
subfolders = [f.path for f in os.scandir(folder) if f.is_dir() ]

for subfolder in subfolders:
	subfolder_name = subfolder.split('/')[1]
	command = "cat {}{}/*/* >> /Users/manojkarthick/Code/CMPT-732/Spark/Project/hot100-tweets/{}.txt".format(folder, subfolder_name, subfolder_name)
	status = os.system(command=command)
	print(command, status)

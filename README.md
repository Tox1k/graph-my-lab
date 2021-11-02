# graph-my-lab
Python script to generate a network graph from kathara lab configuration files. [Kathara](https://github.com/KatharaFramework/Kathara)

graph-my-lab.py reads lab.conf and [device].startup for each device inside lab.conf.
before running the script make sure to populate your config files!

usage:
```shell
  git clone https://github.com/Tox1k/graph-my-lab.git
  
  cd graph-my-lab
  
  python graph-my-lab.py 'dir_to_lab/'
```
*Note: python3 is required to run the script, also make sure to install additional libraries!*


if everything went smoothly, you can see a **graph.html** file generated inside your directory!
keep in mind that graph.html is dependant on files inside **assets/**

example:
![Example 1](/examples/example_1.png)

Every time that you refresh the page the layout is different, you can even move freely each node of the board.

Enjoy :)

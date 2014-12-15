plogbook
========

Plogbook is a console application for personal logging. It turns personal logs written in console or favorite text editor into readable html pages. The personal logs(plogs for short) are located in categories which are part of the plogbook.

Execute via: 
>python plogbook.py  

and see --help for argument usage.  
For examples see /examples/. For suggestions and bugs please see [issues](https://github.com/Granitas/plogbook/issues)

First time usage
===
1. Create a folder that will be your plogbook.
2. Cd to that folder and simply execute the program via "python plogbook.py" answer yes when prompted.
3. Write your first plog to finish initiation!
4. See --help argument and FAQ below for more info.

FAQ
===
###### Which python version?  
Plogbook should run on 2.7+ and 3+ versions of Python. Please report any hicups to [issues](https://github.com/Granitas/plogbook/issues) it's mostly tested on 3.4  
###### Which operating systems plogbook works on?  
Tested on Linux and Windows 8, should work on pretty much anything that runs python, if it doesn't please report to [issues](https://github.com/Granitas/plogbook/issues).  
######So plogbook is basically a diary?  
In a way yeah, though diaries are for little girls and logs just sound cool. Makes me feel like a scientist everytime I write one, even those where I complain about how rubbish the new seasons of supernatural are (and yet I still watch it...)
###### What about security ?  
plogbook has no real security mechanism at the moment. Security should be kept outside of plogbook for now (i.e. see [for linux] (http://askubuntu.com/questions/104542/is-there-a-way-to-password-protect-individual-folders))
###### Can I change the css and html ? Default ones are ugly    
Yes, you can build out html and css templates by --build_templates. Templates will be created at plogbook/templates directory and will be used to build new plogs. To rebuild old plog files see --rebuild_<..> commands. Feel free to propose different default designs to [issues](https://github.com/Granitas/plogbook/issues) (would be really nice) !   
###### Can I rebuild plogs to use new html templates?  
You can rebuild styles but for html not yet, I'm working on this feature.  
###### Writting html sucks, can I write my plogs in markdown?  
Yes, however for markdown to html conversion you need to install [Markdown2](https://github.com/trentm/python-markdown2) package.  See --markdown  
###### Can I make plogbook download images from the plogs and store them locally?  
Yes, see --localize-images  

How does it look?
===
Note: any templates and looks can be adjusted, see faq and examples/build_templates example.   
**Default output.**  
Main page:  
![main page](http://wstaw.org/m/2014/12/15/plasma-desktopBE2314.png)
Category page:  
![category page for plogbook category](http://wstaw.org/m/2014/12/15/plasma-desktopYv2314.png)
Plog:  
![plog from the plogbook category](http://wstaw.org/m/2014/12/15/plasma-desktopew2314.png)  
Writting plog using console:  
![writting plog](http://wstaw.org/m/2014/12/15/plasma-desktopyy2314.png)  
Writting plog using kate text editor:  
![writting plog via kate](http://wstaw.org/m/2014/12/15/plasma-desktopYl2314.png)  

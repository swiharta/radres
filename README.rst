Setup Django Environment on Windows
##################################################

:Download and install:

Console2 (cmd.exe replacement)
 http://sourceforge.net/projects/console/

Python 2.7 32-bit
 http://www.python.org/download/releases/2.7.5/

Setuptools 32-bit (adds 'easy_install' command)
 http://pypi.python.org/pypi/setuptools

Ruby 1.9.3
 http://rubyinstaller.org/

Node.js (now comes as an installer that includes npm!)
 http://nodejs.org/download/

Putty
 http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html

Git for Windows (guide: http://nathanj.github.com/gitguide/tour.html)
 http://msysgit.github.com/

|

:Download below (install later to virtualenv using easy_install):

PIL
 http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe

PyWin ("pywin32-218.win32-py2.7.exe")
 http://sourceforge.net/projects/pywin32/files/pywin32/

PyCrypto ("PyCrypto 2.6 for Python 2.7 32bit")
 http://www.voidspace.org.uk/python/modules.shtml#pycrypto

|

:Add directories to your Windows PATH (adds commands to use in cmd.exe):
 * Start button
 * Start typing 'environment'
 * Select `Change System Environment Variables`
 * Add to "PATH" variable under System Variables:
   ``;C:\Python27;C:\Python27\Scripts;C:\Scripts;C:\Program Files (x86)\PuTTY``

|

:Install pip and virtualenv:

Open Console2 or cmd.exe:
::

 easy_install pip 
 pip install virtualenv
 pip install virtualenvwrapper_win

* virtualenvwrapper gives you some extra commands (ex. setprojectdir, cdproject)
  http://github.com/davidmarble/virtualenvwrapper-win
* By default, virtualenvs live in ``C:\Users\<USERNAME>\Envs``
   `Optional`: In Environment Variables (see above), edit this `WORKON_HOME` virtualenv storage path

::

  mkvirtualenv <virtualenv_name>

:Install some python libraries:

Windows binaries install globally when double-clicked, but can go in your virtualenv using easy_install. Just be sure you are working in your virtualenv first (you should be if you just made one). You need to ``cd`` to the directory where the .EXE files were saved.

::

 easy_install PIL-1.1.7.win32-py2.7.exe
 easy_install pycrypto-2.6.win32-py2.7.exe
 easy_install pywin32-218.win32-py2.7.exe

|

:Install some Ruby / Node.js stuff:

::

 gem update --system
 gem install compass
 gem install bootstrap-sass
 gem install sassy-buttons
 gem install susy

 npm install -g coffee-script

``-g`` flag for npm installs globally to ``\\AppData\Roaming\npm\node_modules``. Omitting it will create ``node_modules`` in the current working directory. It's probably best to install globally, as `coffee` command works automatically.

|

:Set up some custom tabs for Console2 and allow it to run PuTTY:
 * Open Console2
 * Go to "Settings"
 * Select "Tabs"
 * Under "Shell", enter below lines into "Shell text box" to create different tabs, named...

 "django" (or whatever you want to call this tab, workon your Env)
  ::

   cmd.exe /k workon <name_of_your_virtual_env>
   
  * This will also automatically change to the project directory if you set that using virtualenvwrapper

 "compass"
  ::

   cmd.exe /k compass watch media

  * Also change "start-up folder" to ``C:/<path_to>/radres/radres``

 "webfaction"
  ::

   C:\Program Files (x86)\Console2\ansicon.exe "C:\Program Files (x86)\PuTTY\plink.exe" -load "webfaction"

ansicon:
 * http://github.com/adoxa/ansicon
 * Download: http://adoxa.3eeweb.com/ansicon/

Extract the contents of ``x86`` folder to Console2 folder

|

:Clone RadRes from GitHub:

::

 cd <directory_where_you_want_to_store_your_project(s)>
 git clone git://github.com/swiharta/radres.git

|

:Set a project directory so virtualenv will put you in there when you do ``workon <your_virtualenv>``:

::

 setprojectdir <path_to_top_level_radres_project_directory>

|
 
:Install the project requirements:

::

 pip install -r radres/requirements.txt

|

:Sync the database (and migrate apps if needed):

::

 python manage.py syncdb
 python manage.py migrate --all

* South tutorial: http://south.aeracode.org/docs/tutorial/part1.html

|


:Try running the test server:

::

 python manage.py runserver

Open a browser and try loading http://127.0.0.1:8000

|

BELOW UNDER CONSTRUCTION
#############################

|

:Add and commit changes to your local git repo:

::

 git add .
 git commit -m "Commit message"

|

:Set your remote repository on Webfaction:

::

 git remote add origin <username>@<username>.webfactional.com:webapps/<git_app>/repos/<proj>.git

* Webfaction Git docs: http://docs.webfaction.com/software/git.html

|

:Push your project to the remote repository:

::

 git push origin master
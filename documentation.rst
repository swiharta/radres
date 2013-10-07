SETUP PYTHON AND DJANGO ON WINDOWS
##################################

Download and install some essentials
-----------------------
Console2 (cmd.exe replacement)
http://sourceforge.net/projects/console/

Python 2.7 32-bit
http://www.python.org/download/releases/2.7.2/

Setuptools 32-bit (adds 'easy_install' command)
http://pypi.python.org/pypi/setuptools

Ruby 1.9.3 (most recently, used to use 1.8.7)
http://rubyinstaller.org/

Node.js (now comes as an installer that includes npm!)
http://nodejs.org/download/

Putty
http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html

Git for Windows
http://msysgit.github.com/
* Read and follow these directions for hooking up to GitHub repos
  http://nathanj.github.com/gitguide/tour.html

Download only (install later to virtualenv using easy_install)
-----------------------
* Make sure to get 32-bit versions for Python 2.7

PIL
http://effbot.org/downloads/PIL-1.1.7.win32-py2.7.exe

PyWin (e.g. pywin32-218.win32-py2.7.exe)
http://sourceforge.net/projects/pywin32/files/pywin32/

PyCrypto (e.g. PyCrypto 2.6 for Python 2.7 32bit)
http://www.voidspace.org.uk/python/modules.shtml#pycrypto

Add directories to your Windows PATH (adds commands to use in cmd.exe)
-----------------------
* Start button -> Start typing 'environment' -> Change System Environment Variables
* Add to the "PATH" variable under System Variables:
::
  ;C:\Python27;C:\Python27\Scripts;C:\Scripts;C:\Program Files (x86)\PuTTY

Setup virtualenv and install essentials
-----------------------
* Open Console2 or cmd.exe
::
  easy_install virtualenv
  easy_install pip
  pip install virtualenvwrapper_win

* virtualenvwrapper provides several convenience methods (e.g. setprojectdir, cdproject)
http://github.com/davidmarble/virtualenvwrapper-win
* By default Envs live in C:\Users\<USERNAME>\Envs
  - (Optional) In Environmental Variables, edit `WORKON_HOME` virtualenv storage path
::
  mkvirtualenv <environment_name>

Install some essential python libraries using Windows binaries
-----------------------
::
  easy_install PIL-1.1.7.win32-py2.7.exe
  easy_install pycrypto-2.6.win32-py2.7.exe
  easy_install pywin32-218.win32-py2.7.exe

Assuming you are in the projects' root directory (e.g. C:\Websites, C:\Websites\projects)
-----------------------
::
  git clone <username>@<username>.webfactional.com:webapps/githttp/repos/<project_name>.git
  setprojectdir %CD%\<project_name>

* %CD% is a Windows variable for the current directory
* setting the project dir will put you in there when you activate the virtualenv

Install the project requirements
-----------------------
::
  pip install -r radres/requirements.txt

Install some Ruby / Node.js stuff
------------------------
::
  gem update --system
  gem install compass
  gem install bootstrap-sass
  gem install sassy-buttons
  gem install susy

  npm install -g coffee-script

* `-g` flag for npm installs globally to \\AppData\Roaming\npm\node_modules
  - Omitting it will create node_modules in the current working directory
  - Probably easiest / best to install globally, as `coffee` command works automatically
    + Not sure if it will be on the Windows PATH otherwise

Set up some custom tabs for Console2 and allow it to run PuTTY
-----------------------
* Settings -> Tabs -> Shell -> Shell text box
::
  django      :  cmd.exe /k workon <virtual_env>
  compass     :  cmd.exe /k compass watch media (change start-up folder to radres/radres)
  webfaction  :  C:\Program Files (x86)\Console2\ansicon.exe "C:\Program Files (x86)\PuTTY\plink.exe" -load "webfaction"

ansicon:
http://github.com/adoxa/ansicon
actual download you want (.exe):
http://adoxa.3eeweb.com/ansicon/
Extract the contents of x86 folder to Console2

Setup Fabric
------------------------

################# INCOMPLETE ##################
::
  pip install fabric


Install Django OR Pinax and start a project
-----------------------
* Make sure you're in the virtual environment (workon <environment_name>)
::
  pip install django
  cd \path\to\django_projects # up to you, I use C:\Websites
  django-admin startproject <project_name>

* if error, try
::
  python \path\to\django.admin.py startproject <project_name>

* OR INSTALL PINAX (pick one or the other)...
::
  pip install pinax
  pinax-admin setup_project -l  # lists base projects, we'll try 'social'
  pinax-admin setup_project -b social <project_name>

Install some essential apps
-----------------------
* Make sure you're in the virtual environment (workon <environment_name>)
::
  pip install south docutils django-extensions django-compressor django-memcached

Update settings.py: uncomment admin lines, enter database info, add above apps to INSTALLED_APPS
-----------------------
Update urls.py: uncomment admin lines
-----------------------
Create local_settings.py in project root (you can just use the file I provided)
-----------------------

Make some extra project directories (skip if you installed Pinax)
-----------------------
::
  cd \path\to\<project_name> # or just 'cd <project_name>' if you're following along
  mkdir templates
  mkdir deploy
  mkdir media
  mkdir site_media
  cd site_media
  mkdir media
  mkdir static

If you didn't install Pinax, put the provided django.wsgi file in <proj>/deploy and edit inside '<' and '>'
-----------------------
If you installed Pinax, take a look at <proj>/deploy/pinax.wsgi and make sure it looks like the one I provided
-----------------------

Sync the database
-----------------------
::
  python manage.py syncdb

Try running the test server
-----------------------
::
  python manage.py runserver # quit the server with Ctrl+C

Setup version control with Git
-----------------------
::
  git init

Now copy the .gitignore file I provided into your project directory
-----------------------

Make your first Django app
-----------------------
::
  python manage.py startapp <app_name>

http://docs.djangoproject.com/en/dev/intro/tutorial01/
* Build a basic app.
* models.py defines your database schema
* When you change models.py, you'll often need to do a database migration with South

Manage the database schemas of your custom Django apps using South
-----------------------
* For each Django app you have made, do...
::
  python manage.py schemamigration <app_name> --initial

* --initial for the first migration of each app
* use --auto instead everytime thereafter, when migrating your app
* then...
::
  python manage.py migrate --all

http://south.aeracode.org/docs/tutorial/part1.html

You'll probably find a lot of other 3rd party django / python apps to install
-----------------------
Freeze installed packages to requirements.txt
-----------------------
::
  pip freeze > requirements.txt

http://www.pip-installer.org/en/latest/#freezing-requirements
http://www.pip-installer.org/en/latest/requirement-format.html

Add and commit changes to your local git repo
-----------------------
::
  git add .
  git commit -m "Commit message"

Set your remote repository
-----------------------
::
  git remote add origin <username>@<username>.webfactional.com:webapps/<git_app>/repos/<proj>.git

Push your project to the remote repository
-----------------------
::
  git push origin master

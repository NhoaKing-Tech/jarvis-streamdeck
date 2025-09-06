# Display Servers / Protocols

I am running streamdeck XL from Elgato in Ubuntu 24.04.3 LTS (Noble Numbat).

I am using a miniconda environment I created. I installed miniconda by downloading:
'Miniconda3-py311_25.5.1-0-Linux-x86_64.sh' from [https://repo.anaconda.com/miniconda/]. During the installation I decided to enable the conda base at terminal startup, since this is the most convient for me, as I will only work in python from now on. In the future I might deactivate this. In that case I would need to run:

`conda config --set auto_activate_base false` 

Then I created my environment. Since in my case I will be using a single environment for working on two projects to which I assigned two codenames, my environment was called 'jarvis-mamba':

`conda create -n jarvis-mamba python=3.11`

After I created the environment the first thing I installed was pip.


From there I have installed the following trough pip:
-xdotools
-ydotools
-pyautogui

When installing the modules you may get some deprecation warnings. These will only become a worry if you upgrade your pip version to pip 25.3, according to the information that I got in my terminal when installing pyautogui for instance.

My pip version is: pip 25.2
My python version is: Python 3.11.13
My miniconda version is: conda 25.5.1

You can find the versions with: `which pip`, `which python` and `which conda` from your environment.

The default display server is wayland. However, 
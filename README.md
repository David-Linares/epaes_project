Proyecto EPAES (Bot de Ayuda para Aprender Español)
================

----

Pasos de Instalación
-------------
### Ambiente de Desarrollo (Fedora 22 < )
> **1.** Instalar Python3 y Pip3
> &emsp;  **$** sudo yum -y update
> &emsp;  **$** dnf intall python3
> &emsp;  **$** yum -y install python3-pip
> &emsp;  **$** yum -y install python3-devel
> **2.** Clonar el proyecto de GIT
> &emsp;  **$** git clone http://www.hydrasoftsas.com:8550/universidad/EPAES.git
> **3.** Crear y activar Ambiente Virtual
> &emsp;  **$** mv *EPAES* **epaes** & cd epaes
> &emsp;  **$** python3 -m venv **venvepaes**
> &emsp;  **$** source *venvepaes/bin/activate*
> **4.** Configurar proyecto
> &emsp;  **$** yum install -y mysql-devel
> &emsp;  **$** yum install -y gcc
> &emsp;  **$** pip3 install -r requirements
> &emsp;  **$** python3 manage.py runserver *0.0.0.0:8000*

### Ambiente de Producción (Centos 7)
> **1.** Instalar Python3 y Pip3
> &emsp;  **$** sudo yum -y update
> &emsp;  **$** yum -y install https://centos7.iuscommunity.org/ius-release.rpm
> &emsp;  **$** yum -y install python36u
> &emsp;  **$** python3.6 -V
> &emsp;  >> Python 3.6.2
> &emsp;  **$** yum -y install python36u-pip
> &emsp;  **$** yum -y install python36u-devel
> **2.** Clonar el proyecto de GIT
> &emsp;  **$** git clone http://www.hydrasoftsas.com:8550/universidad/EPAES.git
> **3.** Crear y activar Ambiente Virtual
> &emsp;  **$** mv *EPAES* **epaes** & cd epaes
> &emsp;  **$** python3.6 -m venv **venvepaes**
> &emsp;  **$** source *venvepaes/bin/activate*
> **4.** Configurar proyecto
> &emsp;  **$** yum install -y mysql-devel
> &emsp;  **$** yum install -y gcc
> &emsp;  **$** pip3 install -r requirements
> &emsp;  **$** yum install -y python36u-mod_wsgi
> &emsp;  **$** wget http://download.redis.io/releases/redis-stable.tar.gz
> &emsp;  **$** tar xzvf redis-stable.tar.gz
> &emsp;  **$** cd redis-stable
> &emsp;  **$** make
> &emsp;  **$** make install
> &emsp;  **$** redis-server
> &emsp;  **$** sudo rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-1.el7.nux.noarch.rpm
> &emsp;  **$** yum install ffmpeg 
 


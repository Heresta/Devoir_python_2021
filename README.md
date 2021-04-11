# Devoir python 2021

## A propos
Ce repository contient le résultat de mon devoir de Python à l'Ecole nationale des Chartes dans le cadre du master de Technologies numériques appliquées à l'Histoire.
On y trouve une application Flask qui a pour but de présenter une base de données relationnelle de liens vers des recettes.

## Installation
### Créer un environnement virtuel sous Linux-Ubuntu
Nous allons créer un environnement virtuel dans lequel il sera possible d'utiliser Python 3.6.

Pour ce faire, dans un terminal, il faut entrer la ligne de commandes suivante :
```shell
sudo apt-get install python3 libfreetype6-dev python3-pip python3-virtualenv
```
Choisissez ensuite un dossier dans lequel vous souhaitez enregistrer l'application et d'où vous pourrez l'utiliser. 

Dans ce dossier, il vous faut cloner le repository <i>Devoir Python 2021</i>.

C'est depuis ce même dossier qu'il vous faut entrer la ligne de commandes suivante pour créer l'environnement virtuel : 
```shell
virtualenv ~/.Devoir_python_2021 -p python3
```
Cela fait, toujours dans le terminal, il faut rentrer les lignes de commandes suivantes :
```shell
source ~/.Devoir_python_2021/bin/activate
```
A noter que cette commande est obligatoire pour toute activation de l'application.

### Installer les packages
Pour assurer le bon fonctionnement de cette application, il faut installer plusieurs packages. Ceux-ci se trouvent dans le document <i>requirements.txt</i>. Pour ne pas avoir à le faire à la main, il suffit de taper cette ligne de commande dans le terminal (assurez-vous d'être toujours dans l'environnement virtuel tout juste créé).
```shell
pip install -r requirements.txt
```
A noter que cette commande n'est à utiliser qu'une seule fois.


## Prise en main de l'application
Afin de démarrer l'application Flask, il suffit de rentrer ces deux dernières lignes de commandes : 
```shell
cd Le\ hasard\ des\ recettes
```
```shell
python3 run.py
```
A partir de là, l'application devrait fonctionner d'elle-même.

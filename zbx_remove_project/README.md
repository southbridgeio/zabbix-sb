Скрипт предназначен для удаления проекта из zabbix. Данный скрипт удаляет все 
хосты, группу, правила авторегистрации и пользователей, созданных для этого
проекта.

Запуск скрипта:

```
python zbx_remove_project/zbx_remove_project.py  --prname "1test.com" 

```
Ключи запуска:

* --prname -  имя проекта который надо удалить.
* -h - краткая справка по ключам.
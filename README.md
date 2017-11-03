##  Состав
Набор скриптов для управления zabbix:

1. zbx_add_maintenance скрипт постановки хостов на обслуживание
2. zbx_add_proj добавление нового проекта в zabbix
3. zbx_remove_project удалени проекта из zabbix
4. zbx_create_sslvalid_check создание проверки срока ssl сертификата
5. zbx_create_domain_check cоздание  проверка срока делегирования доммена
6. zbx_create_web_check создание веб проверки


При каждом запуске скрипта, проверяется наличие обновлений в git и если они есть, то выполняется комманда git pull. После требуется перезапустить скрипт. Для этого используется скрипт git_update.py 
##  Требования

Модули питона:
1. gitpython
2. ZabbixAPI


## Настройка

Настройки подключения в zabbix вынесены в отдельный файл: conf/zabbix.conf

Формат конфигурационного файла:
```
server=https://XXX.XX
user=XXXXXX
password=XXXX
```

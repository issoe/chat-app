# chat-app
## Requirements
 - MSVS Build tool 
 - python - kivy
 - flask (python)
 - mysql

## Installation
1. Create virtualenv (optional)
2. create new mysql db name: 'chatapp_new'
3. replace your database server credential in file \center_server\utils - function: connect_db
4. create some users in db using stored procedure
```sql
  CALL signup('__username__', '__password__');
```
5. center_server.py
```bash
  python center_server/center_server.py
```
5. run application
```bash
  python peer/main.py
```

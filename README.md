# chat-app
## Requirements
 - MSVS Build tool 
 - python - kivy
 - flask (python)
 - mysql

## Installation
1. Create virtualenv (optional)
2. Create new mysql db name: 'chatapp_new'
3. Run Schema and Procedure SQL file
4. Replace your database server credential in file \center_server\utils - function: connect_db
5. Create some users in db using stored procedure
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

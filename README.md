# forward messages bot

### prepare .env
```bash
cp ./.env.example ./env
```

### run migrations
```bash
alembic upgrade head
```
### prepare db
#### add chat settings
```sql
INSERT INTO chat_settings (variable_name, value, chat_id, user_id)
VALUES ('min_forward_message_length', <min lenght len>, chat_id, user_id);
```
#### add hashtags
```sql
INSERT INTO hashtag (from_chat_id, to_chat_id, hashtag_name)
VALUES (<from_chat_id>, <to_chat_id>, <hashtag_name>);
```

### run project
```bash
python3 server.py
```

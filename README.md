## To deploy bot

##### First step, setup config files

- create settings.py
  ```
  mv settings.example.py settings.py
  vim settings.py  # add config here
  ```
- create keys.yaml
  ```
  mv keys.backup.yaml keys.yaml
  vim keys.yaml   # write keys here
  ```

##### Second step, run scripts

- run buy_wiz bot
  ```
  python buy_wiz_routine.py
  ```
- run send_discord bot (open another screen / use nohup)
  ```
  python send_discord_routine.py
  ```

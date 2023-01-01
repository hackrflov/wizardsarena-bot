import os
import json
import time
import requests
import settings

if not os.path.exists('ids-yaml'):
    os.mkdir('ids-yaml')

discord_url = settings.DISCORD_URL
my_account = f'k:{settings.MY_PUB_KEY}'

while True:
    try:
        # read buy_wiz records and confirm owner is me
        rows = open('buy_wiz_reocrds.txt', 'r').read().split('\n')
        wiz_ids = []
        for row in rows:
            if row[:3] == 'wiz':
                wiz_id = int(row.split('has been')[0].split('#')[1])
                price = int(row.split('(')[1].split(' KDA')[0])
                records = [int(v) for v in open('send_discord_record.txt', 'r').read().split('\n') if v]
                if wiz_id not in wiz_ids and wiz_id not in records:
                    url = 'https://api.chainweb.com/chainweb/0.0/mainnet01/chain/1/pact/api/v1'
                    text = open('local-wiz.yaml', 'r').read().replace('$WIZ_IDS', str([wiz_id]))
                    new_fn = f'ids-yaml/local-wizard-with-ids-for-send.yaml'
                    with open(new_fn, 'w') as f:
                        f.write(text)
                    cmd = f'pact -a {new_fn} -l | curl -H "Content-Type: application/json" -d @- {url}/local'
                    print('now fetch cmd: {}'.format(cmd))
                    os.system(cmd + ' > tmp_local')
                    data = json.loads(open('tmp_local', 'r').read())['result']['data']
                    if data[0]['owner'] == my_account:
                        # send a notification to discord
                        wiz_ids.append(wiz_id)
                        os.system(f'echo {wiz_id} >> send_discord_record.txt')

                        data = {
                            'username': f'#{wiz_id}',
                            'avatar_url': f'https://storage.googleapis.com/wizarena/generated_imgs/{wiz_id}.png',
                            'content': f'#{wiz_id} just sold for {price} KDA',
                        }
                        print(data)
                        res = requests.post(discord_url, data=data)
                        print(res.text)
                        time.sleep(5)

        print(wiz_ids)

    except Exception as e:
        print(e)

    time.sleep(30)
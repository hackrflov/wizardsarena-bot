import os
import json
import time
import threading

bought_wiz_ids = []

def buy(wiz_id, wiz_owner_account, wiz_price):
    # execute purchase and write records
    print(f'now buy {wiz_id}')
    os.system(f'python run_buy_wizard.py {wiz_id} {wiz_owner_account} {wiz_price} > tmp_buy_wiz_{wiz_id}.txt')
    os.system(f'echo "wizard #{wiz_id} has been purchased ({wiz_price} KDA) successfully!" >> buy_wiz_reocrds.txt')

while True:
    try:
        # find on sale nfts and filter with certain requirements
        url = 'https://api.chainweb.com/chainweb/0.0/mainnet01/chain/1/pact/api/v1'
        cmd = f'pact -a local-wiz-on-sale.yaml -l | curl -H "Content-Type: application/json" -d @- {url}/local'
        print('now fetch cmd: {}'.format(cmd))
        os.system(cmd + ' > tmp_local')
        result = open('tmp_local', 'r').read()
        data = json.loads(result)['result']['data']
        print(data)
        wiz_ids = [int(v['id']) for v in sorted(data, key=lambda x: x['price']) if v['price'] <= 15]
        wiz_ids = [v for v in wiz_ids if v not in bought_wiz_ids]

        if wiz_ids:
            # if find any matched nft, fetch its info, and run buy_wiz script
            text = open('local-wiz.yaml', 'r').read().replace('$WIZ_IDS', str(wiz_ids))
            new_fn = f'local-wizard-with-ids.yaml'
            with open(new_fn, 'w') as f:
                f.write(text)
            cmd = f'pact -a {new_fn} -l | curl -H "Content-Type: application/json" -d @- {url}/local'
            print('now fetch cmd: {}'.format(cmd))
            os.system(cmd + ' > tmp_local')
            result = open('tmp_local', 'r').read()
            data = json.loads(result)['result']['data'][:1]  # one by one
            print(data)
            for nft in data:
                wiz_id = nft['id']
                wiz_owner_account = nft['owner']
                wiz_price = nft['price']
                threading.Thread(target=buy, args=[wiz_id, wiz_owner_account, wiz_price]).start()
                bought_wiz_ids.append(wiz_id)
            
        os.remove('tmp_local')
    except Exception as e:
        print(e)
        pass

    print(wiz_ids)
    time.sleep(60)
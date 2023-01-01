import os
import json
import time
import threading
import settings

if not os.path.exists('ids-yaml'):
    os.mkdir('ids-yaml')
url = 'https://api.chainweb.com/chainweb/0.0/mainnet01/chain/1/pact/api/v1'

bought_wiz_ids = []
price_limit = 15
my_account = f'k:{settings.MY_PUB_KEY}'

def buy(wiz_id, wiz_owner_account, wiz_price):
    # execute purchase and write records
    print(f'now buy {wiz_id}')
    os.system(f'python run_buy_wizard.py {wiz_id} {wiz_owner_account} {wiz_price} > tmp_buy_wiz_{wiz_id}.txt')
    os.system(f'echo "wizard #{wiz_id} has been purchased ({wiz_price} KDA) successfully!" >> buy_wiz_reocrds.txt')

def check_my_balance():
    text = open('check-balance.yaml', 'r').read().replace('$MY_ACCOUNT', my_account)
    new_fn = f'ids-yaml/check-balance-me.yaml'
    with open(new_fn, 'w') as f:
        f.write(text)
    cmd = f'pact -a {new_fn} -l | curl -H "Content-Type: application/json" -d @- {url}/local'
    print('now fetch cmd: {}'.format(cmd))
    os.system(cmd + ' > tmp_local_balance')
    result = open('tmp_local_balance', 'r').read()
    print(result)
    balance = json.loads(result)['result']['data']
    os.remove('tmp_local_balance')
    return balance > price_limit

while True:
    try:
        if check_my_balance():
            # find on sale nfts and filter with certain requirements
            cmd = f'pact -a local-wiz-on-sale.yaml -l | curl -H "Content-Type: application/json" -d @- {url}/local'
            print('now fetch cmd: {}'.format(cmd))
            os.system(cmd + ' > tmp_local')
            result = open('tmp_local', 'r').read()
            data = json.loads(result)['result']['data']
            print(data)
            wiz_ids = [int(v['id']) for v in sorted(data, key=lambda x: x['price']) if v['price'] <= price_limit]
            wiz_ids = [v for v in wiz_ids if v not in bought_wiz_ids]

            if wiz_ids:
                # if find any matched nft, fetch its info, and run buy_wiz script
                text = open('local-wiz.yaml', 'r').read().replace('$WIZ_IDS', str(wiz_ids))
                new_fn = f'ids-yaml/local-wizard-with-ids-for-buy.yaml'
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
                
            print(wiz_ids)
            os.remove('tmp_local')
        else:
            print('no enough balance')
            break

    except Exception as e:
        print(e)
        pass

    time.sleep(60)
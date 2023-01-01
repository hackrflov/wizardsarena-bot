import os
import sys
import json
import settings

my_pub_key = settings.MY_PUB_KEY

wiz_id = sys.argv[1]
wiz_owner_account = sys.argv[2]
wiz_price = sys.argv[3]
chain_id = 1
url = 'https://api.chainweb.com/chainweb/0.0/mainnet01/chain/{}/pact/api/v1'.format(chain_id)

# write custom yaml for certain wizard
text = open('buy-wizard.yaml', 'r').read() \
    .replace('$WIZ_ID', wiz_id) \
    .replace('$WIZ_OWNER_ACCOUNT', wiz_owner_account) \
    .replace('$WIZ_PRICE', wiz_price) \
    .replace('$MY_PUB_KEY', my_pub_key)
os.mkdir('ids-yaml')
new_fn = f'ids-yaml/buy-wizard-{wiz_id}.yaml'
with open(new_fn, 'w') as f:
    f.write(text)
        
# sign
pact_cmd = f'pact -u {new_fn} | pact add-sig keys.yaml'
tmp_fn = f'tmp_{wiz_id}'
os.system(pact_cmd + f' > {tmp_fn}')
result = open(tmp_fn, 'r').read().replace('\n', '')
print('now pact cmd: {}, after execution: {}'.format(pact_cmd, result))

# send to chainweb
cmd = '{} | curl -H "Content-Type: application/json" -d @- {}/send'.format(pact_cmd, url)
print('now send cmd: {}'.format(cmd))
os.system(cmd + f' > {tmp_fn}')
result = open(tmp_fn, 'r').read()
print('http result: {}'.format(result))

# fetch result
request_key = json.loads(result)['requestKeys'][0]
cmd = 'curl -H "Content-Type: application/json" -d ###A"listen":"{}"###B -X POST {}/listen'.format(request_key, url)
cmd = cmd.replace('###A', "'{").replace('###B', "}'")
for i in range(5):
    print('now run cmd, times: {}, {}'.format(i, cmd))
    os.system(cmd + f' > {tmp_fn}')
    result = open(tmp_fn, 'r').read()
    print(result)
    if 'timeout' not in result.lower() and '504' not in result.lower():
        break

os.remove(tmp_fn)
print('\n COMPLETE.')

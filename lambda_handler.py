import json
from async_get_data import *


def lambda_handler(event, context):
    exchange_info = get_exchange_info(info)
    with open('./assets/trade_universe.json','w') as f:
        f.write(json.dumps(exchange_info))
        f.close()

    asyncio.run(main())
    return {
        'statusCode': 200,
        'body': json.dumps(f'{context}')
    }

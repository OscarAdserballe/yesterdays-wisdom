import os

INTEGRATION_TOKEN = os.getenv('INTEGRATION_TOKEN')
print(INTEGRATION_TOKEN)
INTEGRATION_TOKEN='secret_QTLcb31ulTSLdxD12FgmmT1399yxB6YFcO78WEO1zNm'

HEADERS = {
    "Authorization": "Bearer " + INTEGRATION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

import os
import json
import logging
from datetime import datetime, timezone, timedelta

import boto3


def lambda_handler(event, context):
    BUCKET = os.environ['AWS_S3_BUCKET']
    TELEGRAM_CHAT_ID = int(os.environ['TELEGRAM_CHAT_ID'])

    try:
        # --------------------------------------------------
        # NORMALIZAÇÃO DO EVENTO (teste local OU API Gateway)
        # --------------------------------------------------
        if "body" in event and event["body"] is not None:
            # Evento vindo de API Gateway / webhook
            body = event["body"]

            # Caso venha codificado em base64
            if event.get("isBase64Encoded"):
                import base64
                body = base64.b64decode(body).decode("utf-8")

            message = json.loads(body)

        else:
            # Evento de teste local (JSON direto)
            message = event

        # --------------------------------------------------
        # VALIDA CHAT DO TELEGRAM
        # --------------------------------------------------
        chat_id = message.get("message", {}).get("chat", {}).get("id")

        if chat_id != TELEGRAM_CHAT_ID:
            return {
                "statusCode": 200,
                "body": json.dumps({"msg": "Mensagem ignorada"})
            }

        # --------------------------------------------------
        # GERA DATA E NOME DO ARQUIVO
        # --------------------------------------------------
        tzinfo = timezone(offset=timedelta(hours=-3))
        date = datetime.now(tzinfo).strftime('%Y-%m-%d')
        timestamp = datetime.now(tzinfo).strftime('%Y%m%d%H%M%S%f')
        filename = f'{timestamp}.json'

        # --------------------------------------------------
        # SALVA TEMPORARIAMENTE NO LAMBDA
        # --------------------------------------------------
        filepath = f"/tmp/{filename}"

        with open(filepath, "w", encoding="utf8") as fp:
            json.dump(message, fp, ensure_ascii=False)

        # --------------------------------------------------
        # ENVIA PARA O S3
        # --------------------------------------------------
        client = boto3.client("s3")

        client.upload_file(
            filepath,
            BUCKET,
            f"telegram/context_date={date}/{filename}"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"msg": "Arquivo salvo com sucesso"})
        }

    except Exception as exc:
        logging.error("Erro no Lambda:")
        logging.error(exc)

        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(exc)})
        }
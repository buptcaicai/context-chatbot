import dotenv
dotenv.load_dotenv(override=True)
import os
import aioboto3

async def get_ssm_parameter(
    param_name: str, with_decryption: bool = True
) -> str | None:
    async with aioboto3.Session().client("ssm") as ssm:
        try:
            response = await ssm.get_parameter(
                Name=param_name, WithDecryption=with_decryption
            )
            return response["Parameter"]["Value"]
        except Exception as e:
            print(f"Error fetching SSM parameter '{param_name}': {e}")
            return None


async def get_ssm_parameters(
    param_names: list[str], with_decryption: bool = True
) -> dict[str, str]:
    """
    Fetch multiple parameter values from AWS SSM Parameter Store.

    Args:
       param_names (list[str]): List of parameter names.
       with_decryption (bool): Whether to decrypt SecureString parameters.

    Returns:
       dict[str, str]: Dictionary of parameter names to values.
    """
    async with aioboto3.Session().client(
        "ssm", region_name=os.getenv("AWS_REGION")
    ) as ssm:
        result = {}
        try:
            response = await ssm.get_parameters(
                Names=param_names, WithDecryption=with_decryption
            )
            for param in response.get("Parameters", []):
                result[param["Name"]] = param["Value"]
            if response.get("InvalidParameters"):
                print(f"Invalid SSM parameters: {response['InvalidParameters']}")
        except Exception as e:
            print(f"Error fetching SSM parameters: {e}")
        return result


_PARAM_NAMES = [
    "/file-ingestion/sns/topic-arn",
    "/llm-chat/sns/topic-arn",
    "/file-ingestion-request/sqs/queue-url",
    "/file-ingestion-reply/sqs/queue-url",
    "/llm-chat-request/sqs/queue-url",
    "/llm-chat-response/sqs/queue-url",
]

sys_params = {
    "file_ingestion_request_queue_url": "",
    "file_ingestion_reply_queue_url": "",
    "llm_chat_request_queue_url": "",
    "llm_chat_response_queue_url": "",
    "file_ingestion_topic_arn": "",
    "llm_chat_topic_arn": "",
}


async def get_ssm_parameters_async():
    print(f"Getting SSM parameters")
    global sys_params
    _params = await get_ssm_parameters(_PARAM_NAMES)
    sys_params["file_ingestion_request_queue_url"] = _params[
        "/file-ingestion-request/sqs/queue-url"
    ]
    sys_params["file_ingestion_reply_queue_url"] = _params[
        "/file-ingestion-reply/sqs/queue-url"
    ]
    sys_params["llm_chat_request_queue_url"] = _params[
        "/llm-chat-request/sqs/queue-url"
    ]
    sys_params["llm_chat_response_queue_url"] = _params[
        "/llm-chat-response/sqs/queue-url"
    ]
    sys_params["file_ingestion_topic_arn"] = _params["/file-ingestion/sns/topic-arn"]
    sys_params["llm_chat_topic_arn"] = _params["/llm-chat/sns/topic-arn"]

import traceback
import dotenv
dotenv.load_dotenv(override=True)
import os
from kafka import KafkaConsumer, TopicPartition
import json
from src.components.file_upload import FileContent

if __name__ == "__main__":
    consumer = KafkaConsumer(
        bootstrap_servers=[os.getenv("KAFKA_BROKER")],
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    # consumer = KafkaConsumer(
    #     "file-injest",
    #     bootstrap_servers=[os.getenv("KAFKA_BROKER")],
    #     value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    # )
    tp = TopicPartition("file-injest", 0)
    consumer.assign([tp])
    consumer.seek(tp, 3)
    for message in consumer:
        try:
            print(f"Received message offset: {message.offset}")
            print(f"Received message: {message}")
            data = message.value

            file_content = FileContent(
                file_name=data.get("file_name"),
                file_size=data.get("file_size"),
                sentences=data.get("sentences", []),
                is_last=data.get("is_last", False)
            )

            print(f"Created FileContent object for file: {file_content.file_name}")
            print(f"File size: {file_content.file_size}")
            print(f"Number of sentences: {len(file_content.sentences)}")
            print(f"Is last chunk: {file_content.is_last}")

        except Exception as e:
            print(f"Error processing message: {e}")
            # stack_trace = traceback.format_exc()
            # print(f"Stack trace:\n{stack_trace}")
            continue

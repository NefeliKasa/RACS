import math
import json


class DataProcessor:
    @staticmethod
    def data_sharding(data, num_of_shards):
        binary_data = DataProcessor.data_binary_encoding(data)
        total_len = len(binary_data)

        block_size = math.ceil(total_len / num_of_shards)
        global_padding_size = (block_size * num_of_shards) - total_len

        shards = []
        shard_metadata = []
        for i in range(num_of_shards):
            shard = binary_data[i * block_size : (i + 1) * block_size]

            if i == num_of_shards - 1:
                padded_data_shard = DataProcessor.data_padding(
                    shard, global_padding_size
                )
            else:
                padded_data_shard = shard

            shards.append(padded_data_shard)
            shard_metadata.append(
                DataProcessor.generate_metadata(i, global_padding_size)
            )

        return (shards, shard_metadata)

    @staticmethod
    def generate_metadata(block_num, padding_size):
        return {"block_num": block_num, "padding_size": padding_size}

    @staticmethod
    def data_binary_encoding(data):
        return json.dumps(data).encode("utf-8")

    @staticmethod
    def data_binary_decoding(data):
        return json.loads(data.decode("utf-8"))

    @staticmethod
    def data_padding(data, padding_size):
        padded_data = data + (b"\0" * padding_size)

        return padded_data

    @staticmethod
    def remove_data_padding(data, padding_size):
        if padding_size > 0:
            data = data[:-padding_size]
        return data

from zfec import Encoder, Decoder
from codec_utils.data_processing import DataProcessor


class Codec:
    k = 2
    n = 3

    @staticmethod
    def encode(data):
        encoder = Encoder(
            Codec.k, Codec.n
        )  # k: number of primary chunks, n: total number of chunks

        data_shards, shard_metadata = DataProcessor.data_sharding(data, Codec.k)
        blocknums = [i for i in range(Codec.n)]

        encoded_blocks = encoder.encode(data_shards, blocknums)

        for i in range(Codec.k, Codec.n):
            shard_metadata.append(
                DataProcessor.generate_metadata(i, shard_metadata[0]["padding_size"])
            )

        return (encoded_blocks, shard_metadata)

    @staticmethod
    def decode(encoded_data, metadata):
        decoder = Decoder(Codec.k, Codec.n)

        blocknums = [
            metadata["blocknums"][i] for i in range(len(metadata["blocknums"]))
        ][: Codec.k]
        padding_sizes = [
            metadata["padding"][i] for i in range(len(metadata["padding"]))
        ][: Codec.k]

        blocks_to_decode = encoded_data[: Codec.k]

        decoded_tuple = decoder.decode(blocks_to_decode, blocknums)
        decoded_shards = list(decoded_tuple)

        decoded_shards[-1] = DataProcessor.remove_data_padding(
            decoded_shards[-1], padding_sizes[0]
        )

        decoded_data = b"".join(decoded_shards)

        return DataProcessor.data_binary_decoding(decoded_data)

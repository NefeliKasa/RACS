import base64
from fastapi import FastAPI, HTTPException
from model import EncodeRequest, DecodeRequest
from codec_utils.codec import Codec
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="Codec Service API")


# --- Helper Functions ---


def _convert_blocks_to_b64(binary_blocks: list[bytes]) -> list[str]:
    return [base64.b64encode(block).decode("utf-8") for block in binary_blocks]


def _build_data_metadata_response(
    b64_blocks: list[str], metadata: list[dict]
) -> list[dict]:
    return [
        {"encoded_data": b64_blocks[i], "metadata": metadata[i]}
        for i in range(len(b64_blocks))
    ]


def _parse_b64_to_binary(b64_blocks: list[str]) -> list[bytes]:
    return [base64.b64decode(block.encode("utf-8")) for block in b64_blocks]


# --- API Routes ---


@app.post("/encode")
def encode_data(request: EncodeRequest):
    try:
        encoded_binary_blocks, metadata = Codec.encode(request.data)

        encoded_b64_blocks = _convert_blocks_to_b64(encoded_binary_blocks)

        encoded_data_metadata = _build_data_metadata_response(
            encoded_b64_blocks, metadata
        )

        return {"encoded_data_metadata": encoded_data_metadata}
    except Exception as e:
        logger.error(f"Failed to encode data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Encoding failed: {str(e)}")


@app.post("/decode")
def decode_data(request: DecodeRequest):
    try:
        encoded_binary_data = _parse_b64_to_binary(request.encoded_data)

        decoded_data = Codec.decode(
            encoded_data=encoded_binary_data,
            metadata=request.metadata,
        )

        return {"decoded_data": decoded_data}
    except Exception as e:
        logger.error(f"Failed to decode data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Decoding failed: {str(e)}")

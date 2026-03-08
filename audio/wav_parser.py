import logging
import struct

logger = logging.getLogger(__name__)


def read_chunk(data: bytes, chunk_size: int, offset: int) -> bytes:
    # We start from the offset and end on the number of bytes we want
    # indiated by the offsetesired chunk size.
    chunk: bytes = data[offset : offset + chunk_size]
    logger.info(f" Chunk data: {chunk.hex(' ')}")

    return chunk


def traverse_wav():
    with open("440.wav", "rb") as wav:
        file_data: bytes = wav.read()

        logger.info(" Getting value for RIFF Chunk Descriptor...")
        descriptor: bytes = read_chunk(file_data, 12, 0)

        specification, chunk_size, format = struct.unpack_from("<4sI4s", descriptor)
        logger.info(
            f" Specification: {specification.decode()}\tChunk Size: {chunk_size / 1_000_000:.2f} MiB\tFile Format: {format.decode()}"
        )

        logger.info(" Retrieving Format subchunk...")
        fmt_sc_size, audio_fmt, channels, sample_rate, bit_rate = struct.unpack_from(
            "<IHHI6xH", buffer=file_data, offset=16
        )
        logger.info(
            f" : Size: {fmt_sc_size}\tAudio Format {'PCM' if (audio_fmt == 1) else 'MPEG'}\tAudio Channels: {channels}\tSample Rate: {sample_rate}\tBit Rate: {bit_rate}"
        )

        data_chunk_offset = 40 + (0 if audio_fmt == 1 else 2)
        logger.info(" Retrieving Data subchunk...")
        data_sc_size = struct.unpack_from(
            "<I", buffer=file_data, offset=data_chunk_offset
        )
        logger.info(f" Data Size: {data_sc_size[0]:,}")


def main():
    traverse_wav()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    main()

import logging
import struct

from .audio_signal import AudioSignal

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)


def read_audio_file(audio_file_path: str) -> bytes:
    logger.info(f" Opening file `{audio_file_path}`...")

    with open(audio_file_path, "rb") as audio_file:
        return audio_file.read()


def get_header_info(audio_file: bytes, offset: int = 0) -> dict:
    logger.info(" Reading header data...")
    _, file_size, file_format = struct.unpack_from(
        "<4sI4s", buffer=audio_file, offset=offset
    )

    logger.debug(f" Size: {file_size}\tFile Format: {file_format}")
    return {"file_size": file_size, "file_format": file_format}


def get_fmt_info(audio_file: bytes, offset: int = 0) -> dict:
    logger.info(" Reading fmt data...")
    fmt_id, chunk_size, format, channels, sample_rate, *_, bit_rate = (
        struct.unpack_from("<4sIHHIIHH", buffer=audio_file, offset=offset)
    )

    logger.debug(f" Verifying fmt_id == fmt: {fmt_id}")
    # Sanity Check. Ensure subchunk offset is the fmt chunk
    if fmt_id != b"fmt ":
        raise Exception("Invalid format for WAVE file.")

    logger.debug(" Logging fmt metadata:")
    logger.debug(
        f" id: {fmt_id}\tChunk Size: {chunk_size}\tFormat: {format}\tChannel(s): {channels}\tSample Rate: {sample_rate}\tBit Rate: {bit_rate}"
    )
    return {
        "fmt_id": fmt_id,
        "chunk_size": chunk_size,
        "format": format,
        "channels": channels,
        "sample_rate": sample_rate,
        "bit_rate": bit_rate,
    }


def get_data_info(audio_file: bytes, offset: int = 0, is_stereo: bool = False) -> dict:
    logger.info(" Reading data chunk data...")
    data_id, chunk_size = struct.unpack_from("<4sI", buffer=audio_file, offset=offset)

    logger.debug(" Logging data metadata:")
    logger.debug(f" id: {data_id}\tChunk Size: {chunk_size}\tIs Stereo: {is_stereo}")

    # Sanity Check. Ensure subchunk offset is the data chunk
    if data_id != b"data":
        raise Exception("Invalid offset for data chunk.")

    audio_data: list[float] = []
    logger.debug(" Getting audio data from raw bytes...")

    for i in range(0, chunk_size, 4):
        start: int = offset + i  # Add i to offset to ensure we are incrementing
        end: int = start + 4
        dword: bytes = audio_file[start:end]
        if is_stereo:
            logger.debug(f" Start: {start}\tEnd: {end}\tOffset: {offset}\tIndex: {i}")
            # logger.debug(f" Double Word: {dword}")
            l_word, r_word = struct.unpack_from("<hh", buffer=dword)
            audio_data.append(((l_word + r_word) / 2) / 32768.0)

            logger.debug(
                f" Audio Data (4 bytes | Stereo: {is_stereo}): {audio_data[-1]}"
            )
        else:
            logger.debug(f" Start: {start}\tEnd: {end}\tOffset: {offset}")
            logger.debug(f" Double Word: {dword}")
            mono_data: tuple = struct.unpack_from("<hh", buffer=dword)
            audio_data.extend([(i / 32768.0) for i in mono_data])
            logger.debug(
                f" Audio Data (4 bytes | Stereo: {is_stereo}): {audio_data[-1]}"
            )

    logger.debug(f" Sample f 10 bytes from audio data: {audio_data[:10]}")

    return {"data_id": data_id, "chunk_size": chunk_size, "audio_data": audio_data}


def get_audio_signal(audio_file_path: str) -> AudioSignal:
    audio_file: bytes = read_audio_file(audio_file_path)
    header: dict = get_header_info(audio_file)
    fmt: dict = get_fmt_info(audio_file, offset=12)

    data: dict = get_data_info(
        audio_file,
        offset=fmt.get("chunk_size", 0) + 20,
        is_stereo=bool(fmt.get("channels", 0) == 2),
    )

    return AudioSignal(
        file_format=header.get("file_format", "").decode(),
        file_size=header.get("file_size", 0),
        fmt_sc_size=fmt.get("chunk_size", 0),
        data_sc_size=data.get("chunk_size", 0),
        sample_rate=fmt.get("sample_rate", 0),
        bit_rate=fmt.get("bit_rate", 0),
        data=data.get("audio_data", []),
        is_stereo=bool(fmt.get("channels", 0) == 2),
        is_pcm=bool(fmt.get("format", 0) == 1),
    )


def main(file: str) -> None:
    audio: AudioSignal = get_audio_signal(file)
    logger.info(f" \n\nAudioSignal Metadata:\n{audio}")

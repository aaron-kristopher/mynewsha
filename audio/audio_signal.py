from dataclasses import dataclass


@dataclass(frozen=True)
class AudioSignal:
    file_format: str
    file_size: float
    fmt_sc_size: float
    data_sc_size: float
    sample_rate: int
    bit_rate: int
    is_stereo: bool
    is_pcm: bool
    data: list[float]

    def __repr__(self):
        return f" \
        \nFormat: {self.file_format} \
        \nFile Size: {self.file_size / 1_000_000:.2f} MiB \
        \nSample Rate: {self.sample_rate / 1_000:.1f} kHz \
        \nfmt Subchunk Size: {self.fmt_sc_size} \
        \ndata Subchunk Size: {self.data_sc_size}\
        \nBit Rate: {self.bit_rate} \
        \nIs Steroe: {self.is_stereo}\
        \nData Sample: {self.data[:5]}"

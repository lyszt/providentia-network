#include "binary_payload.hpp"

#include <cstdint>
#include <fstream>
#include <stdexcept>
#include <string>

namespace kievan::io {

namespace {

uint32_t toBigEndian(uint32_t value) {
    return ((value & 0x000000FFu) << 24) |
           ((value & 0x0000FF00u) << 8) |
           ((value & 0x00FF0000u) >> 8) |
           ((value & 0xFF000000u) >> 24);
}

}  // namespace

void writeBinaryPayload(const std::string &path,
                        bool success,
                        const std::string &contextJson,
                        const std::string &summary) {
    std::ofstream output(path, std::ios::binary);
    if (!output.is_open()) {
        throw std::runtime_error("Unable to open output path for writing: " + path);
    }

    uint8_t status = success ? 0 : 1;
    uint32_t contextLen = toBigEndian(static_cast<uint32_t>(contextJson.size()));
    uint32_t summaryLen = toBigEndian(static_cast<uint32_t>(summary.size()));

    output.write(reinterpret_cast<char *>(&status), sizeof(status));
    output.write(reinterpret_cast<char *>(&contextLen), sizeof(contextLen));
    if (!contextJson.empty()) {
        output.write(contextJson.data(), static_cast<std::streamsize>(contextJson.size()));
    }
    output.write(reinterpret_cast<char *>(&summaryLen), sizeof(summaryLen));
    if (!summary.empty()) {
        output.write(summary.data(), static_cast<std::streamsize>(summary.size()));
    }
}

}  // namespace kievan::io


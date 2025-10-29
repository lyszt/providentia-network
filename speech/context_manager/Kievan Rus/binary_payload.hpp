#pragma once

#include <string>

namespace kievan::io {

/**
 * @brief Write the structured response payload to disk for the Python caller.
 * @param success true when the thinking process succeeded, false otherwise.
 * @param contextJson Serialized JSON describing the thought context or an error message.
 * @param summary Summarised thought string (ignored on failures).
 * @throws std::runtime_error when the output file cannot be written.
 */
void writeBinaryPayload(const std::string &path,
                        bool success,
                        const std::string &contextJson,
                        const std::string &summary);

}  // namespace kievan::io


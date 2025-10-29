#pragma once

#include <string>

namespace kievan::config {

/**
 * @brief Resolve the Gemini API key from the environment or provided .env file.
 * @throws std::runtime_error when the API key cannot be found.
 */
std::string loadApiKey(const std::string &envPath);

}  // namespace kievan::config


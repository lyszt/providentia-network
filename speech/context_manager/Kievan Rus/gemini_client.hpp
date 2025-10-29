#pragma once

#include <string>

namespace kievan::gemini {

/**
 * @brief Execute a POST request to the Gemini API with the provided payload.
 * @throws std::runtime_error when the request fails or returns a non-success HTTP status.
 */
std::string callGemini(const std::string &apiKey,
                       const std::string &model,
                       const std::string &payload);

/**
 * @brief Extract the text field from the Gemini JSON response.
 * @throws std::runtime_error when the response format is unexpected.
 */
std::string extractTextField(const std::string &response);

}  // namespace kievan::gemini


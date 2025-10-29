#pragma once

#include <string>

#include "arguments.hpp"

namespace kievan::prompts {

/**
 * @brief Construct the natural-language analysis prompt sent to Gemini.
 */
std::string buildAnalysisPrompt(const Arguments &args);

/**
 * @brief Wrap the analysis prompt inside the JSON payload required by the Gemini API.
 */
std::string buildAnalysisPayload(const std::string &prompt);

/**
 * @brief Build the summarisation prompt used to compress the thought process.
 */
std::string buildSummaryPrompt(const std::string &contextJson);

/**
 * @brief Wrap the summary prompt inside the JSON payload required by the Gemini API.
 */
std::string buildSummaryPayload(const std::string &prompt);

}  // namespace kievan::prompts


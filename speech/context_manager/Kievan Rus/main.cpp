#include "arguments.hpp"
#include "binary_payload.hpp"
#include "curl_guard.hpp"
#include "environment.hpp"
#include "gemini_client.hpp"
#include "prompts.hpp"

#include <exception>
#include <iostream>
#include <sstream>
#include <string>

int main(int argc, char *argv[]) {
    std::string outputPath;
    try {
        kievan::Arguments args = kievan::parseArguments(argc, argv);
        outputPath = args.outputPath;

        kievan::curl::GlobalGuard curlGuard;

        std::string apiKey = kievan::config::loadApiKey(args.envPath);

        std::string analysisPrompt = kievan::prompts::buildAnalysisPrompt(args);
        std::string analysisPayload = kievan::prompts::buildAnalysisPayload(analysisPrompt);
        std::string analysisResponse = kievan::gemini::callGemini(apiKey, args.model, analysisPayload);
        std::string contextJson = kievan::gemini::extractTextField(analysisResponse);

        std::string summaryPrompt = kievan::prompts::buildSummaryPrompt(contextJson);
        std::string summaryPayload = kievan::prompts::buildSummaryPayload(summaryPrompt);
        std::string summaryResponse = kievan::gemini::callGemini(apiKey, args.model, summaryPayload);
        std::string summaryText = kievan::gemini::extractTextField(summaryResponse);

        kievan::io::writeBinaryPayload(args.outputPath, true, contextJson, summaryText);
        return 0;
    } catch (const std::exception &ex) {
        try {
            std::ostringstream oss;
            oss << "Thinking process failed: " << ex.what();
            if (!outputPath.empty()) {
                kievan::io::writeBinaryPayload(outputPath, false, oss.str(), "");
            }
        } catch (...) {
            // Suppress secondary failures when writing the error payload.
        }
        std::cerr << "Error: " << ex.what() << std::endl;
        return 1;
    }
}


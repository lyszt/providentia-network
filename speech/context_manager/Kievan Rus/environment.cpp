#include "environment.hpp"

#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <fstream>
#include <stdexcept>
#include <string>

namespace kievan::config {

namespace {

std::string trim(const std::string &value) {
    auto left = std::find_if_not(value.begin(), value.end(), [](unsigned char ch) {
        return std::isspace(ch);
    });
    auto right = std::find_if_not(value.rbegin(), value.rend(), [](unsigned char ch) {
        return std::isspace(ch);
    }).base();
    if (left >= right) {
        return {};
    }
    return std::string(left, right);
}

std::string readValueFromEnvFile(const std::string &path, const std::string &key) {
    std::ifstream input(path);
    if (!input.is_open()) {
        return {};
    }

    std::string line;
    while (std::getline(input, line)) {
        if (line.empty() || line[0] == '#') {
            continue;
        }
        auto pos = line.find('=');
        if (pos == std::string::npos) {
            continue;
        }
        auto currentKey = trim(line.substr(0, pos));
        if (currentKey == key) {
            return trim(line.substr(pos + 1));
        }
    }
    return {};
}

}  // namespace

std::string loadApiKey(const std::string &envPath) {
    const char *fromEnv = std::getenv("GEMINI_API_KEY");
    if (fromEnv != nullptr) {
        return std::string(fromEnv);
    }
    if (!envPath.empty()) {
        auto candidate = readValueFromEnvFile(envPath, "GEMINI_API_KEY");
        if (!candidate.empty()) {
            return candidate;
        }
    }
    throw std::runtime_error("Unable to locate GEMINI_API_KEY in environment or .env file.");
}

}  // namespace kievan::config


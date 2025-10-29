#include "gemini_client.hpp"

#include <algorithm>
#include <cctype>
#include <curl/curl.h>
#include <sstream>
#include <stdexcept>
#include <string>

namespace kievan::gemini {

namespace {

size_t writeToString(void *ptr, size_t size, size_t nmemb, void *userdata) {
    auto *stream = static_cast<std::string *>(userdata);
    stream->append(static_cast<char *>(ptr), size * nmemb);
    return size * nmemb;
}

std::string urlEncode(const std::string &value) {
    static const char hex[] = "0123456789ABCDEF";
    std::string encoded;
    encoded.reserve(value.size() * 3);
    for (unsigned char c : value) {
        if (std::isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
            encoded.push_back(c);
        } else {
            encoded.push_back('%');
            encoded.push_back(hex[c >> 4]);
            encoded.push_back(hex[c & 15]);
        }
    }
    return encoded;
}

std::string unescapeJsonString(const std::string &input, std::size_t startPos) {
    std::string result;
    result.reserve(input.size() - startPos);
    for (std::size_t i = startPos; i < input.size();) {
        char c = input[i++];
        if (c == '\\') {
            if (i >= input.size()) {
                break;
            }
            char esc = input[i++];
            switch (esc) {
                case '\\': result.push_back('\\'); break;
                case '"': result.push_back('"'); break;
                case '/': result.push_back('/'); break;
                case 'b': result.push_back('\b'); break;
                case 'f': result.push_back('\f'); break;
                case 'n': result.push_back('\n'); break;
                case 'r': result.push_back('\r'); break;
                case 't': result.push_back('\t'); break;
                case 'u': {
                    if (i + 3 >= input.size()) {
                        break;
                    }
                    unsigned int code = 0;
                    for (int j = 0; j < 4; ++j) {
                        char hex = input[i++];
                        code <<= 4;
                        if (hex >= '0' && hex <= '9') {
                            code += static_cast<unsigned>(hex - '0');
                        } else if (hex >= 'a' && hex <= 'f') {
                            code += static_cast<unsigned>(hex - 'a' + 10);
                        } else if (hex >= 'A' && hex <= 'F') {
                            code += static_cast<unsigned>(hex - 'A' + 10);
                        } else {
                            code = 0;
                            break;
                        }
                    }
                    if (code <= 0x7F) {
                        result.push_back(static_cast<char>(code));
                    } else if (code <= 0x7FF) {
                        result.push_back(static_cast<char>(0xC0 | ((code >> 6) & 0x1F)));
                        result.push_back(static_cast<char>(0x80 | (code & 0x3F)));
                    } else {
                        result.push_back(static_cast<char>(0xE0 | ((code >> 12) & 0x0F)));
                        result.push_back(static_cast<char>(0x80 | ((code >> 6) & 0x3F)));
                        result.push_back(static_cast<char>(0x80 | (code & 0x3F)));
                    }
                    break;
                }
                default:
                    result.push_back(esc);
                    break;
            }
        } else if (c == '"') {
            break;
        } else {
            result.push_back(c);
        }
    }
    return result;
}

}  // namespace

std::string callGemini(const std::string &apiKey,
                       const std::string &model,
                       const std::string &payload) {
    CURL *curl = curl_easy_init();
    if (!curl) {
        throw std::runtime_error("Unable to initialize CURL context.");
    }

    std::string response;
    std::string url = "https://generativelanguage.googleapis.com/v1beta/models/";
    url += urlEncode(model);
    url += ":generateContent?key=";
    url += urlEncode(apiKey);

    struct CurlHandle {
        CURL *ptr;
        explicit CurlHandle(CURL *c) : ptr(c) {}
        ~CurlHandle() {
            if (ptr) {
                curl_easy_cleanup(ptr);
            }
        }
    } handle(curl);

    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_POST, 1L);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, payload.size());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeToString);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

    struct curl_slist *headers = nullptr;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    CURLcode code = curl_easy_perform(curl);
    curl_slist_free_all(headers);
    if (code != CURLE_OK) {
        std::ostringstream oss;
        oss << "CURL request failed: " << curl_easy_strerror(code);
        throw std::runtime_error(oss.str());
    }

    long httpStatus = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &httpStatus);
    if (httpStatus < 200 || httpStatus >= 300) {
        std::ostringstream oss;
        oss << "Gemini API responded with HTTP status " << httpStatus << ": " << response;
        throw std::runtime_error(oss.str());
    }

    return response;
}

std::string extractTextField(const std::string &response) {
    const std::string key = "\"text\"";
    auto pos = response.find(key);
    if (pos == std::string::npos) {
        throw std::runtime_error("Gemini response did not contain the expected text field: " + response);
    }

    pos = response.find(':', pos + key.size());
    if (pos == std::string::npos) {
        throw std::runtime_error("Gemini response contained a malformed text field: " + response);
    }
    ++pos;
    while (pos < response.size() && std::isspace(static_cast<unsigned char>(response[pos]))) {
        ++pos;
    }
    if (pos >= response.size() || response[pos] != '"') {
        throw std::runtime_error("Gemini response text field was not a JSON string: " + response);
    }

    return unescapeJsonString(response, pos + 1);
}

}  // namespace kievan::gemini

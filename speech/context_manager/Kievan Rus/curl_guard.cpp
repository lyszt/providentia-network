#include "curl_guard.hpp"

#include <curl/curl.h>

namespace kievan::curl {

GlobalGuard::GlobalGuard() {
    auto code = curl_global_init(CURL_GLOBAL_DEFAULT);
    if (code != 0) {
        throw std::runtime_error("Unable to initialize CURL.");
    }
}

GlobalGuard::~GlobalGuard() {
    curl_global_cleanup();
}

}  // namespace kievan::curl


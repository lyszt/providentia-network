#pragma once

#include <stdexcept>

namespace kievan::curl {

/**
 * @brief RAII helper ensuring libcurl global state is initialised before use.
 */
class GlobalGuard {
public:
    GlobalGuard();
    ~GlobalGuard();

    GlobalGuard(const GlobalGuard &) = delete;
    GlobalGuard &operator=(const GlobalGuard &) = delete;
};

}  // namespace kievan::curl


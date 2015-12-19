
export const meta = {
    controller: "mission/mission-manage/updates",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/manage\/goals"
    ]
};


/**
 * Init
 */
export function init() {

}

/**
 * Load
 */
export function load() {
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}
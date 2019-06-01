// local custom helper function to check if UI element exists
function exist(element_identifier) {

    var exist_timeout = Date.now() + casper.options.waitTimeout;

    while (Date.now() < exist_timeout) {
        if (present(element_identifier))
            return true;
        else
           sleep(100);
    }

    return false;
}

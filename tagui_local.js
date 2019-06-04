// local custom helper function to check if UI element exists
// keep checking until timeout is reached before return result
// effect is interacting with element as soon as it appears

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

// function to replace add_concat() in tagui_header.js
// gain - echoing string with single and double quotes
// loss - text-like variables usage since Python env

function add_concat(source_string) {

    return source_string;

}

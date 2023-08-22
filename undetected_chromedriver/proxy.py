import os
import zipfile
import uuid
import tempfile

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""


def __get_background_js(host, port, username, password):
    return """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (
        host,
        port,
        username,
        password,
    )


def get_proxy_extension(proxy_data: dict):
    extension_path = tempfile.mkdtemp()

    if not proxy_data.get("host") and not proxy_data.get("port"):
        raise ValueError("you need to specify host and port")

    host = proxy_data.get("host")
    port = proxy_data.get("port")

    username = proxy_data.get("username") or ""
    password = proxy_data.get("password") or ""

    open(os.path.join(extension_path, "manifest.json"), "w").write(manifest_json)
    open(os.path.join(extension_path, "background.js"), "w").write(
        __get_background_js(host, port, username, password)
    )
    
    return extension_path

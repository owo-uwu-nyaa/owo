import itertools
import json
import sys
import re

"""
Usage: build_emoji_list.py <picker.json> <api.json>

Discord doesn't publish what their emoji names are,
and they don't correspond to any other library (e.g. twemoji or official unicode names).
Instead, the list was extracted from the Discord client.

picker.json can be extracted from the Discord client, by first opening the emoji picker, then running:
```js
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const node = document.querySelector("[id^='emoji-picker-grid'] [class^='scroller']");

const result = await (async (node) => {
    const result = new Set();
    for (let y = 0.9 * node.scrollHeight; y <= node.scrollHeight; y += node.offsetHeight) {
        console.log(y);
        node.scroll(0, y);
        await delay(1000);
        node.querySelectorAll("[class^='emojiSpriteImage'] span").forEach(n => result.add(n.innerHTML));
    }
    return result;
})(document.querySelector("[id^='emoji-picker-grid'] [class^='scroller']"));

console.log(JSON.stringify(result));
```

api.json can be extracted from the Discord client,
by searching through the network requests for an emoji name such as 'pleading_face'.
In Firefox, the search is labelled as a magnifying glass next to the main "Filter URLs" search bar.

Open the file from which the network request originates, which should look something like this:
```js
"use strict";(this.webpackChunkdiscord_app=this.webpackChunkdiscord_app||[]).push([[99549],{399549:e=>{
e.exports=JSON.parse('{"100":["100",..."treasure"]}')
}}]);
```

Download the file with e.g. wget, since copying it directly has encoding issues.
Copy the JSON.parse call back into a JS console and copy the result. 
"""


_PICKER_ITEM_RE = re.compile(":(?P<name>[^:]+):")


def process_picker_data(data):
    for item in data:
        for match in _PICKER_ITEM_RE.finditer(item):
            yield match.group("name")


def process_api_data(data):
    for k, vs in data.items():
        yield k
        yield from vs


def main():
    with open(sys.argv[1], "r") as picker_file:
        picker_json = json.load(picker_file)
    with open(sys.argv[2], "r") as api_file:
        api_json = json.load(api_file)

    for line in sorted(set(itertools.chain(process_picker_data(picker_json), process_api_data(api_json)))):
        print(line)


if __name__ == "__main__":
    main()

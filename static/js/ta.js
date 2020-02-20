function moveOption(e1, e2) {
    try {
        for (let i = 0; i < e1.options.length; i++) {
            if (e1.options[i].selected) {
                var e = e1.options[i];
                e2.options.add(new Option(e.text, e.value));
                e1.remove(i);
                i = i - 1;
            }
        }
        document.ta.ranking.value = getvalue(document.ta.list2);
    } catch (e) {
    }
}

function getvalue(geto) {
    let allvalue = "";
    for (let i = 0; i < geto.options.length; i++) {
        allvalue += geto.options[i].value + ",";
    }
    return allvalue;
}

function changepos(obj, index) {
    if (index === -1) {
        if (obj.selectedIndex > 0) {
            let now = obj.options[obj.selectedIndex];
            let former = obj.options[obj.selectedIndex - 1];
            obj.insertBefore(now,former);
        }
    }
    else if (index === 1) {
        if (obj.selectedIndex < obj.options.length - 1) {
            let now = obj.options[obj.selectedIndex];
            let letter = obj.options[obj.selectedIndex + 1];
            obj.insertBefore(letter,now);
        }
    }
}
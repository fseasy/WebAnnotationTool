

var HIGHLIGHT_CLS_NAME = "ann_highlight";

function addHighlightTag(text, rangeArray, clsName){
    clsName = (typeof clsName !== 'undefined')? clsName: HIGHLIGHT_CLS_NAME;
    var plainStartPos = 0,
        plainEndPos = text.length,
        result = [],
        tagStart = "<span class='" + clsName + "'>",
        tagEnd = "</span>";
    for(var i = 0; i < rangeArray.length; i++){
        var range = rangeArray[i],
            rStartPos = range[0],
            rEndPos = range[1],
            plainText = text.slice(plainStartPos, rStartPos),
            rangeText = text.slice(rStartPos, rEndPos),
            plainStartPos = rEndPos;
        result.push(plainText, tagStart, rangeText, tagEnd);
    }
    // process the end
    var lastPlainText = text.slice(plainStartPos, plainEndPos);
    result.push(lastPlainText);
    return result.join("");
}

// http://stackoverflow.com/questions/5379120/get-the-highlighted-selected-text
function getSelectionText(){
    var text = "";
    if(window.getSelection){
        text = window.getSelection().toString();
    } else if(document.selection && docuemnt.selection.type != "Control") {
        text = document.selection.createRage().text;
    }
    return text;
}
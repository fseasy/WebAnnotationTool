

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

function  insertInterval(intervalArray, newInterval){
    // 1. keep equal value not merged (because this will not overlap)
    // 2. keep newInterval, and may break the original interval
    if(intervalArray.length == 0){ 
        return [newInterval, ];
    }
    var left = [],
        right = [],
        middle = [],
        result = [],
        leftEndIdx = 0,
        rightStartIdx = 0,
        oriLen = intervalArray.length;
    for(leftEndIdx = 0; 
        leftEndIdx < oriLen && intervalArray[leftEndIdx][1] <= newInterval[0];
        leftEndIdx++){
        left.push(intervalArray[leftEndIdx]);    
    }
    rightStartIdx = leftEndIdx;
    for(;
        rightStartIdx < oriLen && intervalArray[rightStartIdx][0] < newInterval[1];
        rightStartIdx++);
    if(leftEndIdx == rightStartIdx){
        // no overlap
        middle.push(newInterval);
    } else {
        if(intervalArray[leftEndIdx][0] < newInterval[0]){
            middle.push([intervalArray[leftEndIdx][0], newInterval[0]]);
        }
        middle.push(newInterval);
        if(newInterval[1] < intervalArray[rightStartIdx-1][1]){
            middle.push([newInterval[1], intervalArray[rightStartIdx-1][1]])
        }
    }
    for(; rightStartIdx < oriLen; rightStartIdx++){
        right.push(intervalArray[rightStartIdx]);
    }
    result = result.concat(left, middle, right);
    return result;
}

function arrayEqual(a1, a2){
    if(a1.length != a2.length){ return false; }
    for(var i = 0; i < a1.length; i++){
        if(a1[i] != a2[i]){ return false; }
    }
    return true;
}

function removeInterval(intervalArray, interval){
    var equalIdx = 0;
    for(; equalIdx < intervalArray.length; equalIdx++){
        if(arrayEqual(intervalArray[equalIdx], interval)){
            break;
        }
    }
    if(equalIdx != intervalArray.length){
        intervalArray.splice(equalIdx, 1);
    }
    return intervalArray;
}

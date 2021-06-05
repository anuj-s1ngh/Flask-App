document.addEventListener('DOMContentLoaded', function() {
    elems = document.getElementsByClassName("read_only");
    for(var i = 0; i < elems.length; i++) {
        elems[i].readOnly = true;
    }
});



function modification() {
    let node = document.getElementsByClassName('duty');
    for(let i = 0; i < node.length; i++){
       node[i].removeAttribute('disabled');
    }
}
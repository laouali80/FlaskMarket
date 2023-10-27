function generate_barcode(){
    let str_form = '';

    for(let i = 0; i < 12; i++){
        num = randomNumber(0, 9);
        str_form += num
    }
    
    const element = document.getElementById('barcode');

    element.value = str_form;
}

function randomNumber(min, max){
    return Math.floor(Math.random() * (max - min + 1)) + min;
}


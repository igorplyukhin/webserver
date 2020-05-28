function Code() {
    var message = document.getElementById('mes').value;
    let num = message.split('').map(Number);
    let x = (num[0] + num[1] + num[2]) % 2;
    let y = (num[0] + num[1] + num[3]) % 2;
    let z = (num[0] + num[2] + num[3]) % 2;
    document.getElementById('mes_cod').value = message + x + y + z;
}

function Decode() {
    var message = document.getElementById('mes_cod').value;
    let num = message.split('').map(Number);
    let top = (num[0] + num[1] + num[2] + num[4]) % 2;
    let rigth = (num[0] + num[1] + num[3] + num[5]) % 2;
    let left = (num[0] + num[2] + num[3] + num[6]) % 2;
    let errorBytes = top.toString() + rigth.toString() + left.toString();
    if (errorBytes === "000")
        document.getElementById('decod_mes').value = message.substr(0, 4);
    else {
        if (errorBytes != "011" && errorBytes != "100")
            errorBytes = Invert(errorBytes);
        num[parseInt(errorBytes, 2)] = (num[parseInt(errorBytes, 2)] + 1) % 2;
        document.getElementById('decod_mes').value = num.join('').substr(0, 4);
        document.getElementById('error').innerText = 'Error was corrected';
    }
}

function Invert(number) {
    let s = "";
    for (let i = 0; i < number.length; i++)
        s += (parseInt(number[i]) + 1) % 2;
    return s;
}

function Refresh() {
    document.getElementById('error').innerText = '';
}

function CheckChar(id)
{
    var str=document.getElementById(id);
    var regex=/[^0-1]/gi;
    str.value=str.value.replace(regex ,"");
}
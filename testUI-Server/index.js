let url = "http://127.0.0.1:5000/compile"
let resetUrl = "http://127.0.0.1:5000/compile-reset"
let API_TOKEN = "ELDA"
let button = document.getElementById('compile');
let result = document.getElementById('result');
let reset = document.getElementById('reset');
button.addEventListener('click', event => {
    result.value = "";
    let codigo;
    codigo = document.getElementById('pycoffee').value;
    let data = {
        codigo: codigo
    }
    console.log(data);
    let settings = {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${API_TOKEN}`,
            'Content-Type': 'application/json'
        },
        body : JSON.stringify( data )
    }
    fetch(url, settings)
        .then( response => {
            console.log(response);
            if(response.ok){
                return response.json();
            }
            throw new Error( response.statusText );
        })
        .then( responseJSON => {
            console.log(responseJSON);
            for (let key in responseJSON) {
                if (responseJSON.hasOwnProperty(key)) {
                    console.log(key + " -> " + responseJSON[key]);
                    result.value += `${key} -> ${responseJSON[key]}\n`
                }
            }
            return responseJSON;
        })
        .catch( err => {
           console.log(err);
        });
})

reset.addEventListener('click', event => {
    let codigo = document.getElementById('pycoffee').innerText = ""
    let result = document.getElementById('result').innerText = "";
    result = "";
})
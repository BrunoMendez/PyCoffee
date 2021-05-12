let url = "http://127.0.0.1:5000/compile"


let button = document.getElementById('compile');
let result = document.getElementById('result');
button.addEventListener('click', event => {
    let codigo = document.getElementById('pycoffee').value;
    let data = {
        codigo: codigo
    }
    console.log(data);
    let settings = {
        method: 'POST',
        headers: {
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
            Array.from(responseJSON).forEach(element => {
                result.value +=  `${element}`
            })
        })
        .catch( err => {
           console.log(err);
        });
})
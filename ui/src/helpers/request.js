const fetchAPI = (request, settings = {}) => {
    let url = request;
    if( process.env.NODE_ENV !== 'production'){
        url = `http://localhost:3000${request}`
    }
    if( process.env.NODE_ENV === 'production'){
        url = `https://pycoffeecompiler.herokuapp.com${request}`
    }
    return fetch(url, settings)
}

export default fetchAPI;
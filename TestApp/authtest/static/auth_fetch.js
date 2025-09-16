async function authFetch(url, options = {}) {
    let access = localStorage.getItem('jwt_token');
    let refresh = localStorage.getItem('jwt_refresh');
    if (!options.headers) options.headers = {};
    options.headers['Authorization'] = 'Bearer ' + access;
    let response = await fetch(url, options);
    if (response.status === 401) {
        const refreshResp = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh })
        });
        if (refreshResp.ok) {
            const data = await refreshResp.json();
            localStorage.setItem('jwt_token', data.access);
            options.headers['Authorization'] = 'Bearer ' + data.access;
            response = await fetch(url, options); 
        } else {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('jwt_refresh');
            window.location.href = '/login/';
            return;
        }
    }
    return response;
}

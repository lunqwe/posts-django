document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const logoutButton = document.getElementById('logoutButton');
    const loginFormDiv = document.getElementById('login-form');
    const logoutFormDiv = document.getElementById('logout-form');

    // Проверка токена при загрузке страницы
    if (localStorage.getItem('access')) {
        loginFormDiv.style.display = 'none';
        logoutFormDiv.style.display = 'block';
    } else {
        loginFormDiv.style.display = 'block';
        logoutFormDiv.style.display = 'none';
    }

    // Обработка формы входа
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('http://localhost:8000/api/accounts/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            console.log(data.user.tokens.access)
            localStorage.setItem('access', data.user.tokens.access);
            localStorage.setItem('refresh', data.user.tokens.refresh);
            alert("Login success!");
            window.location.href = 'http://localhost:8000/posts/';
        } catch (error) {
            alert('Login failed!');
        }
    });

    // Обработка кнопки выхода
    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('token');
        loginFormDiv.style.display = 'block';
        logoutFormDiv.style.display = 'none';
    });

});
export default {
  async login(credentials:{"login": "string",
  "password": "string"}) {
    const response = await fetch('http://rocketloud.ru:8000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(credentials)
    });
    
    if (!response.ok) {
      throw new Error('Ошибка авторизации');
    }
    
    return response.json();
  }
};